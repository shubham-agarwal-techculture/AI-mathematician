from pathlib import Path

from aimath.agents.loop import Mathematician
from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Hit
from aimath.lean.sandbox import CheckResult
from aimath.runtime.protocol import WorkItem


class FakeRetriever:
    def __init__(self, known: Hit | None = None, modules: list[str] | None = None):
        self.known = known
        self.modules = modules or ["Mathlib"]
        self.queries: list[str] = []

    def search(self, query: str, limit: int = 8):
        self.queries.append(query)
        return []

    def modules_for(self, query: str) -> list[str]:
        return list(self.modules)

    def known_in_mathlib(self, statement: str) -> Hit | None:
        if self.known is not None and statement.strip() == "Nat.add_zero":
            return self.known
        return None


def _math(tmp_path: Path, completer, checker, retriever=None) -> tuple[Mathematician, Corpus, list[WorkItem]]:
    corpus = Corpus(tmp_path / "aimath.sqlite")
    corpus.ensure_library()
    items: list[WorkItem] = []
    math = Mathematician(
        corpus=corpus,
        retriever=retriever or FakeRetriever(),
        completer=completer,
        checker=checker,
        workspace=tmp_path,
        enqueue=items.append,
    )
    return math, corpus, items


def _accepting_checker(source: str) -> CheckResult:
    if "aimath_typecheck_dummy" in source:
        if "Mathlib.Data.Nat.Basic" in source and "import Mathlib\n" not in source:
            return CheckResult(False, 1, "", "unknown identifier", "narrow import failed")
        return CheckResult(True, 0, "", "", "typechecks")
    if "rfl" in source:
        return CheckResult(True, 0, "", "", "ok")
    return CheckResult(False, 1, "", "unsolved goals", "failed")


def test_prove_records_a_theorem(tmp_path: Path):
    math, corpus, items = _math(tmp_path, lambda s, u, t: "rfl", _accepting_checker)
    outcome = math.prove("∀ n : Nat, n = n", "elementary", attempts=2)
    assert outcome.status == "theorem"
    assert "Lean accepted" in outcome.detail
    row = corpus.find_statement("mathlib", "∀ n : Nat, n = n")
    assert row["status"] == "theorem"
    assert any(item.kind == "prove" for item in items)
    corpus.close()


def test_sorry_attempt_stays_a_conjecture(tmp_path: Path):
    math, corpus, _items = _math(tmp_path, lambda s, u, t: "sorry", _accepting_checker)
    outcome = math.prove("∀ n : Nat, n = n", attempts=1)
    assert outcome.status == "conjecture"
    row = corpus.find_statement("mathlib", "∀ n : Nat, n = n")
    assert row["status"] == "conjecture"
    corpus.close()


def test_mathlib_hit_is_known_not_a_new_theorem(tmp_path: Path):
    called = {"n": 0}

    def completer(system, user, temperature):
        called["n"] += 1
        return "rfl"

    known = Hit("mathlib", "Nat.add_zero", "n + 0 = n", "Mathlib.Data.Nat.Basic", False)
    math, corpus, _items = _math(
        tmp_path, completer, _accepting_checker, FakeRetriever(known=known)
    )
    outcome = math.prove("Nat.add_zero")
    assert outcome.status == "known"
    assert called["n"] == 0
    assert "Mathlib" in outcome.detail
    corpus.close()


def test_narrow_import_falls_back_to_mathlib(tmp_path: Path):
    math, _corpus, _items = _math(
        tmp_path,
        lambda s, u, t: "rfl",
        _accepting_checker,
        FakeRetriever(modules=["Mathlib.Data.Nat.Basic"]),
    )
    outcome = math.prove("∀ n : Nat, n = n", attempts=1)
    assert outcome.status == "theorem"
    assert outcome.lean_src is not None
    assert "import Mathlib" in outcome.lean_src


def test_explore_drops_true_and_keeps_a_conjecture(tmp_path: Path):
    def completer(system, user, temperature):
        if "Propose" in user or "conjectures" in user:
            return '{"conjectures": ["True", "∀ n : Nat, n = n"]}'
        return "exact False"

    math, corpus, items = _math(tmp_path, completer, _accepting_checker)
    outcomes = math.explore("nat", "curious", steps=5)
    assert len(outcomes) == 1
    assert outcomes[0].status == "conjecture"
    assert any(item.kind == "conjecture" for item in items)
    corpus.close()


def test_propose_system_is_relative(tmp_path: Path):
    raw = (
        '{"name": "Parity", "notes": "toy", "axioms": '
        '[{"name": "zero_even", "statement": "True"}]}'
    )

    def checker(source: str) -> CheckResult:
        assert source.startswith("import Mathlib")
        assert "namespace User.Parity" in source
        return CheckResult(True, 0, "", "", "ok")

    math, corpus, items = _math(tmp_path, lambda s, u, t: raw, checker)
    outcome = math.propose_system("structural")
    assert outcome.status == "accepted"
    assert corpus.system_status("Parity") == "accepted"
    assert (tmp_path / "Aimath" / "User" / "Parity.lean").is_file()
    assert any(item.kind == "formalize" for item in items)
    proved = math.prove("True", system="Parity", attempts=1)
    # True is rejected as trivial before it can be called a theorem of the user system.
    assert proved.status == "rejected"
    corpus.close()
