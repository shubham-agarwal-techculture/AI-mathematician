from pathlib import Path

from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Retriever, known_in_mathlib, module_name, parse_arxiv, search_mathlib


ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>A note on addition</title>
    <summary>Untrusted abstract text.</summary>
  </entry>
</feed>
"""


def _mathlib(root: Path) -> Path:
    pkg = root / ".lake" / "packages" / "mathlib"
    folder = pkg / "Mathlib" / "Data" / "Nat"
    folder.mkdir(parents=True)
    (folder / "Basic.lean").write_text(
        "theorem add_zero (n : Nat) : n + 0 = n := by rfl\n"
        "theorem add_zero_forall : ∀ n : Nat, n + 0 = n := add_zero\n",
        encoding="utf-8",
    )
    return pkg


def test_module_name(tmp_path: Path):
    file = tmp_path / "Mathlib" / "Data" / "Nat" / "Basic.lean"
    file.parent.mkdir(parents=True)
    file.write_text("", encoding="utf-8")
    assert module_name(tmp_path, file) == "Mathlib.Data.Nat.Basic"


def test_search_and_verbatim(tmp_path: Path):
    _mathlib(tmp_path)
    hits = search_mathlib(tmp_path, "add_zero", limit=5)
    assert hits
    assert hits[0].module == "Mathlib.Data.Nat.Basic"
    assert hits[0].untrusted is False
    assert known_in_mathlib(tmp_path, "n + 0 = n") is None
    copied = known_in_mathlib(tmp_path, "∀ n : Nat, n + 0 = n")
    assert copied is not None
    assert copied.title == "add_zero_forall"
    assert copied.module == "Mathlib.Data.Nat.Basic"


def test_arxiv_parse_is_untrusted():
    hits = parse_arxiv(ATOM)
    assert hits[0].untrusted is True
    assert hits[0].source == "arxiv"
    assert "addition" in hits[0].title


def test_retriever_order_includes_corpus_then_arxiv(tmp_path: Path):
    _mathlib(tmp_path)
    corpus = Corpus(tmp_path / "aimath.sqlite")
    corpus.ensure_library()
    corpus.add_statement("mathlib", "∀ n : Nat, n + n = 2 * n", "conjecture", "curious", "")
    seen = {}

    def fake_get(url, params):
        seen["url"] = url
        return ATOM

    retriever = Retriever(tmp_path, corpus, arxiv=True, http_get=fake_get)
    hits = retriever.search("add_zero Nat", limit=8)
    sources = [hit.source for hit in hits]
    assert "mathlib" in sources
    assert "arxiv" in sources
    assert any(hit.untrusted for hit in hits)
    corpus.close()
