import json
import socket
import time
from pathlib import Path

import pytest

from aimath.agents.curiosity import next_question
from aimath.agents.loop import Mathematician
from aimath.agents.personalities import get_personality, switch_personality
from aimath.agents.report import rank_records, render_markdown, write_report
from aimath.agents.research import research_step
from aimath.agents.search import rank_scripts, search_proof
from aimath.agents.swarm import expand_agents, run_swarm
from aimath.host.budget import Budget, Timings, steer_budget
from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Retriever
from aimath.knowledge.sources import assess_novelty, match_open_problem, parse_oeis, parse_wikipedia
from aimath.lean.sandbox import CheckResult
from aimath.runtime.distributed import Coordinator, JobQueue, require_token, worker_once
from aimath.runtime.protocol import WorkItem, WorkResult


class FakeRetriever:
    def __init__(self):
        self.modules = ["Mathlib"]

    def search(self, query: str, limit: int = 8):
        return []

    def modules_for(self, query: str):
        return ["Mathlib"]

    def known_in_mathlib(self, statement: str):
        return None


def _math(tmp_path: Path, completer, checker) -> tuple[Mathematician, Corpus]:
    corpus = Corpus(tmp_path / "aimath.sqlite")
    corpus.ensure_library()
    math = Mathematician(
        corpus=corpus,
        retriever=FakeRetriever(),
        completer=completer,
        checker=checker,
        workspace=tmp_path,
        enqueue=lambda _item: None,
    )
    return math, corpus


def _typecheck_or(predicate):
    def checker(source: str) -> CheckResult:
        if "aimath_typecheck_dummy" in source:
            return CheckResult(True, 0, "", "", "typechecks")
        if predicate(source):
            return CheckResult(True, 0, "", "", "ok")
        return CheckResult(False, 1, "", "unsolved goals", "failed")

    return checker


def test_open_problem_is_not_a_new_truth():
    problem = match_open_problem("a note on the Riemann hypothesis")
    assert problem is not None
    assert problem["name"] == "Riemann hypothesis"
    report = assess_novelty("the Riemann hypothesis", in_mathlib=False, in_corpus=False, literature=[])
    assert report.verdict == "adjacent_to_open_problem"
    assert "not a solution" in report.summary


def test_new_to_corpus_is_not_a_world_claim():
    report = assess_novelty("forall n : Nat, n = n", in_mathlib=False, in_corpus=False, literature=[])
    assert report.verdict == "new_to_this_corpus"
    assert "not a claim" in report.summary


def test_wikipedia_and_oeis_are_untrusted():
    wiki = parse_wikipedia({"query": {"search": [{"title": "Prime number", "snippet": "<b>prime</b>"}]}})
    oeis = parse_oeis({"results": [{"name": "Primes", "data": "2,3,5"}]})
    assert wiki[0].untrusted and wiki[0].source == "wikipedia"
    assert "prime" in wiki[0].text
    assert oeis[0].untrusted and oeis[0].source == "oeis"


def test_notes_and_foreign_text_are_searched(tmp_path: Path):
    notes = tmp_path / "notes"
    foreign = tmp_path / "foreign"
    notes.mkdir()
    foreign.mkdir()
    (notes / "paper.md").write_text("the twin prime conjecture remains open", encoding="utf-8")
    (foreign / "Prime.thy").write_text("theorem goldbach: True", encoding="utf-8")
    corpus = Corpus(tmp_path / "aimath.sqlite")
    retriever = Retriever(tmp_path, corpus, notes_dir=notes, foreign_dir=foreign)
    hits = retriever.search("twin prime goldbach", limit=8)
    sources = {hit.source for hit in hits}
    assert "notes" in sources
    assert "foreign" in sources
    assert all(hit.untrusted for hit in hits if hit.source in {"notes", "foreign"})
    corpus.close()


def test_equation_ladder_prefers_ring_and_skips_failures():
    ranked = rank_scripts("n + 0 = n", ["custom"], ["ring"], beam=4)
    assert ranked[0] != "ring"
    assert "custom" in ranked
    assert "sorry" not in rank_scripts("n = n", ["sorry"], [], beam=4)


def test_solver_accepts_without_calling_the_model(tmp_path: Path):
    def completer(system, user, temperature):
        raise AssertionError("the ladder should not call the model")

    math, corpus = _math(tmp_path, completer, _typecheck_or(lambda source: "\n  ring" in source))
    outcome = search_proof(math, "∀ n : Nat, n + 0 = n", beam=4)
    assert outcome.status == "theorem"
    corpus.close()


def test_failed_tactic_is_not_repeated(tmp_path: Path):
    seen: list[str] = []

    def checker(source: str) -> CheckResult:
        if "aimath_typecheck_dummy" in source:
            return CheckResult(True, 0, "", "", "typechecks")
        for tactic in ("ring", "omega", "norm_num", "simp", "custom"):
            if f"\n  {tactic}" in source:
                seen.append(tactic)
                return CheckResult(False, 1, "", "no", "failed")
        return CheckResult(False, 1, "", "no", "failed")

    def completer(system, user, temperature):
        return json.dumps({"scripts": ["ring", "custom"]})

    math, corpus = _math(tmp_path, completer, checker)
    outcome = search_proof(math, "n + 0 = n", beam=6)
    assert outcome.status == "conjecture"
    assert seen.count("ring") == 1
    assert "custom" in seen
    corpus.close()


def test_swarm_queues_many_agents_and_stops_on_a_proof(tmp_path: Path):
    items = expand_agents("∀ n : Nat, n = n", 1000, "curious", 1000)
    assert len(items) == 1000
    calls: list[str] = []

    def completer(system, user, temperature):
        calls.append(user)
        if "Personality: elementary" in user:
            return "rfl"
        return "sorry"

    math, corpus = _math(tmp_path, completer, _typecheck_or(lambda source: "\n  rfl" in source))
    outcome = run_swarm(math, "∀ n : Nat, n = n", agents=4, seed="curious", workers=1)
    assert outcome.status == "theorem"
    assert len(calls) < 8
    corpus.close()


def test_switch_personality_leaves_the_current_style():
    assert switch_personality("curious") != "curious"
    assert get_personality("nerd").name == "nerd"


def test_research_keeps_only_a_proved_definition(tmp_path: Path):
    raw = json.dumps(
        {
            "name": "Double",
            "definition": "def double (n : Nat) : Nat := n + n",
            "goal": "∀ n : Nat, double n = n + n",
            "tactics": "intro n; rfl",
        }
    )
    math, corpus = _math(tmp_path, lambda s, u, t: raw, _typecheck_or(lambda source: "def double" in source))
    kept = research_step(math, "noether")
    assert kept.status == "kept"
    assert (tmp_path / "Aimath" / "Research" / "Double.lean").is_file()

    def reject(source: str) -> CheckResult:
        return CheckResult(False, 1, "", "failed", "failed")

    math.checker = reject
    math.completer = lambda s, u, t: raw.replace("Double", "Triple").replace("double", "triple")
    dropped = research_step(math, "noether")
    assert dropped.status == "dropped"
    assert not (tmp_path / "Aimath" / "Research" / "Triple.lean").exists()
    corpus.close()


def test_curiosity_rotates_fields_and_warns_on_open_problems():
    field, personality, note = next_question(0, "curious")
    assert field == "algebra"
    assert personality
    assert "Lean" in note
    later = [next_question(i)[0] for i in range(len(["a", "b", "c", "d", "e", "f", "g", "h"]))]
    assert "physics" in later
    assert "music" in later


def test_report_ranks_theorems_first(tmp_path: Path):
    ordered = rank_records(
        [
            {"text": "a long conjecture that is still open", "status": "conjecture"},
            {"text": "n = n", "status": "theorem"},
        ]
    )
    assert ordered[0]["status"] == "theorem"
    text = render_markdown(ordered)
    assert text.index("## theorem") < text.index("## conjecture")
    corpus = Corpus(tmp_path / "aimath.sqlite")
    corpus.ensure_library()
    corpus.add_statement("mathlib", "n = n", "theorem", "curious", "Lean accepted this proof.")
    note, lean = write_report(corpus, tmp_path / "reports")
    assert "n = n" in note.read_text(encoding="utf-8")
    assert "import Mathlib" in lean.read_text(encoding="utf-8")
    corpus.close()


def test_steer_budget_follows_disk_and_the_slow_side():
    base = Budget(4, 2, 0, False)
    tight, note = steer_budget(base, disk_free_bytes=1024, temperature_c=None, timings=None)
    assert tight.lean_workers == 1
    assert "disk" in note
    hot, hot_note = steer_budget(base, disk_free_bytes=20 * 1024**3, temperature_c=95, timings=None)
    assert hot.lean_workers == 1 and hot.llm_inflight == 1
    assert "90" in hot_note
    slow_lean, lean_note = steer_budget(
        base, disk_free_bytes=20 * 1024**3, temperature_c=None, timings=Timings(lean_ms=9000, llm_ms=100)
    )
    assert slow_lean.llm_inflight == 1
    assert "Lean" in lean_note


def test_remote_bind_requires_a_token():
    with pytest.raises(ValueError):
        require_token("0.0.0.0", "")


def test_worker_disconnect_requeues_the_job():
    queue = JobQueue()
    item = WorkItem(id="job-1", kind="check", payload={"source": "import Mathlib"}, budget_ms=10)
    queue.put(item)
    coordinator = Coordinator("127.0.0.1", 0, "", queue)
    coordinator.start()
    try:
        with socket.create_connection(("127.0.0.1", coordinator.port), timeout=5) as sock:
            reader = sock.makefile("r", encoding="utf-8", newline="\n")
            writer = sock.makefile("w", encoding="utf-8", newline="\n")
            writer.write(json.dumps({"op": "hello", "token": ""}) + "\n")
            writer.flush()
            assert json.loads(reader.readline())["op"] == "ok"
            writer.write(json.dumps({"op": "pull"}) + "\n")
            writer.flush()
            message = json.loads(reader.readline())
            assert message["op"] == "work"
            writer.close()
            reader.close()
        for _ in range(50):
            if queue.pending and queue.pending[0].id == "job-1" and "job-1" not in queue.inflight:
                break
            time.sleep(0.02)
        else:
            raise AssertionError("the dropped job was not returned to the queue")

        def handle(work: WorkItem) -> WorkResult:
            return WorkResult(work.id, True, True, {"reason": "lean accepted the file"})

        result = worker_once("127.0.0.1", coordinator.port, "", handle)
        assert result is not None and result.lean_accepted is True
        assert queue.results["job-1"].ok is True
    finally:
        coordinator.stop()
