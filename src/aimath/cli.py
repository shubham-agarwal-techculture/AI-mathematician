"""Command line for the local mathematician."""

from __future__ import annotations

import argparse
import shutil
import sys
from multiprocessing import freeze_support
from pathlib import Path

from aimath import __version__
from aimath.agents.loop import Mathematician
from aimath.agents.personalities import personality_names
from aimath.config import find_config, load_config
from aimath.formal.system import load_system
from aimath.host.budget import compute_budget
from aimath.host.probe import probe
from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Retriever
from aimath.lean.project import ELAN_HELP, init_workspace, lake_executable, template_dir, workspace_ready
from aimath.lean.sandbox import CheckResult, lean_check_job
from aimath.llm.router import LLMError, build_client
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
    print(f"aimath {__version__}")
    print(f"CPU logical: {host.cpu_count}")
    print(f"RAM total: {_gb(host.ram_total_bytes)}")
    print(f"RAM available: {_gb(host.ram_available_bytes)}")
    print(f"Load: {host.load:.2f}")
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
    budget = compute_budget(
        host,
        ram_reserve_ratio=cfg.host.ram_reserve_ratio,
        lean_worker_gb=cfg.host.lean_worker_gb,
        max_llm_inflight=cfg.host.max_llm_inflight,
    )
    client = build_client(cfg.llm) if need_llm else None
    scheduler = Scheduler(budget)
    corpus = Corpus(cfg.knowledge.db)
    corpus.ensure_library()
    retriever = Retriever(cfg.lean.workspace, corpus, arxiv=cfg.knowledge.arxiv)

    def checker(source: str) -> CheckResult:
        data = scheduler.run_lean(
            lean_check_job, str(cfg.lean.workspace), source, cfg.lean.timeout_seconds
        )
        return CheckResult.from_dict(data)

    def completer(system: str, user: str, temperature: float) -> str:
        if client is None:
            raise LLMError("this command needs a configured language model")
        return scheduler.run_llm(client.complete, system, user, temperature)

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
