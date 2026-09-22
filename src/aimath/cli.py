"""Command line for the local mathematician."""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from multiprocessing import freeze_support
from pathlib import Path

from aimath import __version__
from aimath.agents.curiosity import curious_step, next_question
from aimath.agents.loop import Mathematician
from aimath.agents.personalities import personality_names
from aimath.agents.report import write_report
from aimath.agents.research import research_step
from aimath.agents.search import search_proof
from aimath.agents.swarm import expand_agents, run_swarm
from aimath.config import find_config, load_config
from aimath.formal.system import load_system
from aimath.host.budget import Timings, compute_budget, steer_budget
from aimath.host.probe import probe
from aimath.host.sense import sense_host
from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Retriever
from aimath.knowledge.sources import assess_novelty
from aimath.lean.project import ELAN_HELP, init_workspace, lake_executable, template_dir, workspace_ready
from aimath.lean.sandbox import CheckResult, lean_check_job
from aimath.llm.router import LLMError, build_client
from aimath.runtime.distributed import Coordinator, worker_once
from aimath.runtime.protocol import WorkItem, WorkResult
from aimath.runtime.scheduler import Scheduler


def _gb(num: int) -> str:
    return f"{num / (1024 ** 3):.1f} GB"


def _example_config() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config.example.yaml"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("config.example.yaml is missing from the aimath project")


def _print_outcome(status: str, system: str, detail: str, lean_src: str | None) -> None:
    if status == "theorem" and system != "mathlib":
        label = f"theorem relative to system {system}"
    else:
        label = status
    print(label)
    print(detail)
    if lean_src and status == "theorem":
        print(lean_src.rstrip())


def _resources(cfg_path: Path | None) -> int:
    host = probe()
    ratio, footprint, llm_cap = 0.25, 3.0, 2
    if cfg_path is not None and cfg_path.is_file():
        cfg = load_config(cfg_path)
        ratio = cfg.host.ram_reserve_ratio
        footprint = cfg.host.lean_worker_gb
        llm_cap = cfg.host.max_llm_inflight
    budget = compute_budget(
        host,
        ram_reserve_ratio=ratio,
        lean_worker_gb=footprint,
        max_llm_inflight=llm_cap,
    )
    root = cfg_path.parent if cfg_path is not None and cfg_path.is_file() else Path.cwd()
    base_url = None
    if cfg_path is not None and cfg_path.is_file():
        base_url = load_config(cfg_path).llm.base_url
    sense = sense_host(root, base_url)
    print(f"aimath {__version__}")
    print(f"CPU logical: {host.cpu_count}")
    print(f"RAM total: {_gb(host.ram_total_bytes)}")
    print(f"RAM available: {_gb(host.ram_available_bytes)}")
    print(f"Load: {host.load:.2f}")
    print(f"Disk free: {_gb(sense.disk_free_bytes)}")
    print(f"GPU: {sense.gpu_name or 'none detected'}")
    print(f"Temperature C: {sense.temperature_c if sense.temperature_c is not None else 'unavailable'}")
    if sense.llm_latency_ms is None:
        print("Model server latency: unavailable")
    else:
        print(f"Model server latency: {sense.llm_latency_ms:.0f} ms")
    print(f"RAM reserve: {ratio:.0%} ({_gb(budget.ram_reserve_bytes)})")
    print(f"Per Lean worker: {footprint:.1f} GB")
    print(f"Lean workers: {budget.lean_workers}")
    print(f"LLM in flight: {budget.llm_inflight}")
    print(f"Memory pressure: {'yes' if budget.memory_pressure else 'no'}")
    print("Process priority: at or below normal")
    return 0


def _require_ready(workspace: Path) -> str | None:
    if workspace_ready(workspace):
        return None
    if lake_executable() is None:
        return ELAN_HELP
    return (
        f"Mathlib workspace is not ready at {workspace}.\n"
        "Run `aimath init`. The first run downloads the Mathlib cache (many GB, network required).\n"
        "prove and explore refuse to start until that workspace exists."
    )


def _open_math(cfg_path: Path, *, need_llm: bool) -> tuple[Mathematician, Scheduler, Corpus]:
    cfg = load_config(cfg_path)
    problem = _require_ready(cfg.lean.workspace)
    if problem:
        raise RuntimeError(problem)
    host = probe()
    corpus = Corpus(cfg.knowledge.db)
    corpus.ensure_library()
    raw_budget = compute_budget(
        host,
        ram_reserve_ratio=cfg.host.ram_reserve_ratio,
        lean_worker_gb=cfg.host.lean_worker_gb,
        max_llm_inflight=cfg.host.max_llm_inflight,
    )
    sense = sense_host(cfg.root, cfg.llm.base_url)
    lean_ms = corpus.recent_timing("lean")
    llm_ms = corpus.recent_timing("llm")
    timings = Timings(lean_ms, llm_ms) if lean_ms is not None and llm_ms is not None else None
    budget, _note = steer_budget(
        raw_budget,
        disk_free_bytes=sense.disk_free_bytes,
        temperature_c=sense.temperature_c,
        timings=timings,
    )
    client = build_client(cfg.llm) if need_llm else None
    scheduler = Scheduler(budget)
    retriever = Retriever(
        cfg.lean.workspace,
        corpus,
        arxiv=cfg.knowledge.arxiv,
        web=cfg.knowledge.web,
        notes_dir=cfg.knowledge.notes,
        foreign_dir=cfg.knowledge.foreign,
    )

    def checker(source: str) -> CheckResult:
        started = time.perf_counter()
        data = scheduler.run_lean(
            lean_check_job, str(cfg.lean.workspace), source, cfg.lean.timeout_seconds
        )
        corpus.record_timing("lean", (time.perf_counter() - started) * 1000)
        return CheckResult.from_dict(data)

    def completer(system: str, user: str, temperature: float) -> str:
        if client is None:
            raise LLMError("this command needs a configured language model")
        started = time.perf_counter()
        text = scheduler.run_llm(client.complete, system, user, temperature)
        corpus.record_timing("llm", (time.perf_counter() - started) * 1000)
        return text

    math = Mathematician(
        corpus=corpus,
        retriever=retriever,
        completer=completer,
        checker=checker,
        workspace=cfg.lean.workspace,
        enqueue=scheduler.enqueue,
        budget_ms=cfg.lean.timeout_seconds * 1000,
    )
    return math, scheduler, corpus


def cmd_init(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    config_path = cwd / "aimath.yaml"
    if not config_path.exists():
        shutil.copyfile(_example_config(), config_path)
        print(f"wrote {config_path}")
    elif args.force:
        print(f"kept existing {config_path}")
    cfg = load_config(config_path)
    try:
        init_workspace(cfg.lean.workspace, cfg.lean.toolchain_url, force=args.force)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Mathlib workspace ready at {cfg.lean.workspace}")
    return 0


def cmd_resources(args: argparse.Namespace) -> int:
    path = None
    if args.config:
        path = Path(args.config)
    else:
        candidate = Path.cwd() / "aimath.yaml"
        if candidate.is_file():
            path = candidate
    return _resources(path)


def cmd_prove(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        outcome = math.prove(args.statement, args.personality, args.attempts, args.system)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        scheduler.close()
        corpus.close()
    _print_outcome(outcome.status, outcome.system, outcome.detail, outcome.lean_src)
    return 0 if outcome.status in {"theorem", "known"} else 1


def cmd_explore(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        outcomes = math.explore(args.domain, args.personality, args.steps)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        scheduler.close()
        corpus.close()
    if not outcomes:
        print("no conjectures were kept")
        return 1
    proved = 0
    for outcome in outcomes:
        print("---")
        _print_outcome(outcome.status, outcome.system, outcome.detail, outcome.lean_src)
        if outcome.status in {"theorem", "known"}:
            proved += 1
    print(f"kept {len(outcomes)} statement(s), {proved} proved or already in Mathlib")
    return 0


def cmd_system_load(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=False)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        system = load_system(Path(args.file))
        outcome = math.install_system(system)
    except (ValueError, OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        scheduler.close()
        corpus.close()
    print(outcome.status)
    print(outcome.detail)
    return 0 if outcome.status == "accepted" else 1


def cmd_system_propose(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        outcome = math.propose_system(args.personality)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        scheduler.close()
        corpus.close()
    print(outcome.status)
    if outcome.name:
        print(outcome.name)
    print(outcome.detail)
    return 0 if outcome.status == "accepted" else 1


def cmd_status(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(find_config(args.config))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    ready = workspace_ready(cfg.lean.workspace)
    print(f"config: {cfg.path}")
    print(f"mathlib workspace: {cfg.lean.workspace}")
    print(f"mathlib ready: {'yes' if ready else 'no'}")
    print(f"llm: {cfg.llm.provider} {cfg.llm.model}")
    print(f"arxiv hints: {'on' if cfg.knowledge.arxiv else 'off'}")
    if cfg.knowledge.db.is_file():
        corpus = Corpus(cfg.knowledge.db)
        counts = corpus.counts()
        print("statements: " + (", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "none"))
        for row in corpus.list_systems():
            print(f"system {row['name']}: {row['status']}")
        corpus.close()
    else:
        print("statements: none")
    _resources(cfg.path)
    return 0 if ready else 1


def _print_novelty(math: Mathematician, statement: str) -> None:
    known = math.retriever.known_in_mathlib(statement) is not None
    row = math.corpus.find_statement("mathlib", statement)
    in_corpus = row is not None and str(row["status"]) in {"theorem", "known"}
    literature = [hit for hit in math.retriever.search(statement, limit=6) if hit.untrusted]
    report = assess_novelty(statement, in_mathlib=known, in_corpus=in_corpus, literature=literature)
    print(report.summary)


def _finish(scheduler: Scheduler, corpus: Corpus) -> None:
    scheduler.close()
    corpus.close()


def cmd_search(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        outcome = search_proof(
            math, args.statement, personality=args.personality, beam=args.beam, system=args.system
        )
        _print_novelty(math, args.statement)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        _finish(scheduler, corpus)
    _print_outcome(outcome.status, outcome.system, outcome.detail, outcome.lean_src)
    return 0 if outcome.status in {"theorem", "known"} else 1


def cmd_swarm(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        queued = expand_agents(args.statement, args.agents, args.personality, math.budget_ms)
        print(f"queued {len(queued)} logical agents; live model calls stay within the host budget")
        outcome = run_swarm(
            math,
            args.statement,
            agents=args.agents,
            seed=args.personality,
            workers=max(1, scheduler.budget.llm_inflight),
        )
        _print_novelty(math, args.statement)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        _finish(scheduler, corpus)
    _print_outcome(outcome.status, outcome.system, outcome.detail, outcome.lean_src)
    return 0 if outcome.status in {"theorem", "known"} else 1


def cmd_research(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    kept = 0
    try:
        for _ in range(args.steps):
            outcome = research_step(math, args.personality)
            print(f"{outcome.status}: {outcome.name}")
            print(outcome.detail)
            if outcome.status == "kept":
                kept += 1
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        _finish(scheduler, corpus)
    print(f"kept {kept} definition(s)")
    return 0 if kept else 1


def cmd_curious(args: argparse.Namespace) -> int:
    try:
        math, scheduler, corpus = _open_math(find_config(args.config), need_llm=True)
    except (FileNotFoundError, RuntimeError, LLMError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        for step in range(args.steps):
            field, personality, note = next_question(step, args.personality)
            print(f"--- {field} / {personality}")
            print(note)
            outcomes = curious_step(math, step, args.personality)
            for outcome in outcomes:
                _print_outcome(outcome.status, outcome.system, outcome.detail, outcome.lean_src)
    except (ValueError, LLMError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        _finish(scheduler, corpus)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(find_config(args.config))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    corpus = Corpus(cfg.knowledge.db)
    try:
        note, lean = write_report(corpus, cfg.root / "reports")
    finally:
        corpus.close()
    print(note)
    print(lean)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(find_config(args.config))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    host = args.host or cfg.distributed.host
    port = args.port or cfg.distributed.port
    token = args.token if args.token is not None else cfg.distributed.token
    try:
        coordinator = Coordinator(host, port, token)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    coordinator.start()
    print(f"coordinator listening on {host}:{coordinator.port}")
    print("workers send JSON lines. A dropped connection returns the job to the queue.")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        coordinator.stop()
        return 0


def _remote_check(item: WorkItem) -> WorkResult:
    if item.kind != "check":
        return WorkResult(item.id, False, None, {"reason": f"this worker only runs check, got {item.kind}"})
    source = str(item.payload.get("source") or "")
    workspace = str(item.payload.get("workspace") or "")
    timeout = int(item.payload.get("timeout") or 180)
    data = lean_check_job(workspace, source, timeout)
    return WorkResult(item.id, bool(data["accepted"]), bool(data["accepted"]), data)


def cmd_worker(args: argparse.Namespace) -> int:
    host = args.host
    port = args.port
    token = args.token or ""
    print(f"worker pulling from {host}:{port}")
    try:
        while True:
            result = worker_once(host, port, token, _remote_check)
            if result is None:
                time.sleep(1)
                continue
            print(f"{result.id} accepted={result.lean_accepted}")
    except KeyboardInterrupt:
        return 0
    except (OSError, PermissionError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    names = ", ".join(personality_names())
    parser = argparse.ArgumentParser(prog="aimath", description="Local AI mathematician")
    parser.add_argument("--config", help="path to aimath.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="write aimath.yaml and download Mathlib")
    init.add_argument("--force", action="store_true", help="replace an existing lean workspace")
    init.set_defaults(func=cmd_init)

    resources = sub.add_parser("resources", help="show the host budget")
    resources.set_defaults(func=cmd_resources)

    prove = sub.add_parser("prove", help="typecheck a statement and search for a proof")
    prove.add_argument("--statement", required=True)
    prove.add_argument("--personality", default="curious", help=names)
    prove.add_argument("--attempts", type=int, default=3)
    prove.add_argument("--system", default="mathlib", help="mathlib, or an accepted user system")
    prove.set_defaults(func=cmd_prove)

    explore = sub.add_parser("explore", help="propose conjectures in a domain and try to prove them")
    explore.add_argument("--domain", required=True)
    explore.add_argument("--personality", default="curious", help=names)
    explore.add_argument("--steps", type=int, default=5)
    explore.set_defaults(func=cmd_explore)

    system = sub.add_parser("system", help="load or propose a formal system on top of Mathlib")
    system_sub = system.add_subparsers(dest="system_cmd", required=True)
    load = system_sub.add_parser("load", help="typecheck a user YAML system")
    load.add_argument("file")
    load.set_defaults(func=cmd_system_load)
    propose = system_sub.add_parser("propose", help="ask the model for a small axiom system")
    propose.add_argument("--personality", default="structural", help=names)
    propose.set_defaults(func=cmd_system_propose)

    status = sub.add_parser("status", help="show the corpus and whether Mathlib is ready")
    status.set_defaults(func=cmd_status)

    search = sub.add_parser("search", help="try a tactic beam, then model scripts, skipping failures")
    search.add_argument("--statement", required=True)
    search.add_argument("--personality", default="formula", help=names)
    search.add_argument("--beam", type=int, default=4)
    search.add_argument("--system", default="mathlib")
    search.set_defaults(func=cmd_search)

    swarm = sub.add_parser("swarm", help="queue many logical agents and stop at the first proof")
    swarm.add_argument("--statement", required=True)
    swarm.add_argument("--agents", type=int, default=8)
    swarm.add_argument("--personality", default="curious", help=names)
    swarm.set_defaults(func=cmd_swarm)

    research = sub.add_parser("research", help="keep a new definition only when a consequence is proved")
    research.add_argument("--steps", type=int, default=1)
    research.add_argument("--personality", default="structural", help=names)
    research.set_defaults(func=cmd_research)

    curious = sub.add_parser("curious", help="pick questions from rotating fields, including other subjects")
    curious.add_argument("--steps", type=int, default=1)
    curious.add_argument("--personality", default="curious", help=names)
    curious.set_defaults(func=cmd_curious)

    report = sub.add_parser("report", help="write a ranked markdown note and a Lean export")
    report.set_defaults(func=cmd_report)

    serve = sub.add_parser("serve", help="share the check queue with workers")
    serve.add_argument("--host", default=None)
    serve.add_argument("--port", type=int, default=None)
    serve.add_argument("--token", default=None)
    serve.set_defaults(func=cmd_serve)

    worker = sub.add_parser("worker", help="pull Lean checks from a coordinator")
    worker.add_argument("--host", default="127.0.0.1")
    worker.add_argument("--port", type=int, default=8765)
    worker.add_argument("--token", default="")
    worker.set_defaults(func=cmd_worker)
    return parser


def main(argv: list[str] | None = None) -> int:
    freeze_support()
    # Touch the template so a broken install fails here, not halfway through init.
    template_dir()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except LLMError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
