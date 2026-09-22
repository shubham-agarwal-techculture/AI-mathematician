"""Untrusted sources around Mathlib: encyclopedias, OEIS, notes, and other provers.

Mathlib stays the trusted library. Nothing returned here is a proof.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_NOTE_SUFFIXES = {".txt", ".md", ".lean", ".v", ".thy", ".mm", ".ml"}
_TOKEN = re.compile(r"[A-Za-z0-9_']+")


def _tokens(text: str, min_len: int) -> list[str]:
    return [tok.lower() for tok in _TOKEN.findall(text) if len(tok) >= min_len]


def load_open_problems() -> list[dict]:
    path = Path(__file__).resolve().parent / "open_problems.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data)


def match_open_problem(query: str, problems: list[dict] | None = None) -> dict | None:
    """Return a catalog entry when the query names it. This is not a solution."""
    hay = set(_tokens(query, 4))
    if not hay:
        return None
    for problem in problems if problems is not None else load_open_problems():
        name_tokens = _tokens(str(problem.get("name") or ""), 4)
        long = [tok for tok in name_tokens if len(tok) >= 6 and tok in hay]
        short = [tok for tok in name_tokens if tok in hay]
        if long or len(short) >= 2:
            return problem
    return None


def search_folder(folder: Path | None, query: str, source: str, limit: int = 3) -> list:
    from aimath.knowledge.retrieve import Hit

    if folder is None or not folder.is_dir():
        return []
    needles = _tokens(query, 3)
    if not needles:
        return []
    hits = []
    for path in folder.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _NOTE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        low = text.lower()
        if not any(tok in low for tok in needles):
            continue
        snippet = " ".join(text.split())[:400]
        hits.append(
            Hit(source=source, title=path.name, text=snippet, module=None, untrusted=True)
        )
        if len(hits) >= limit:
            break
    return hits


def parse_wikipedia(payload: dict) -> list:
    from aimath.knowledge.retrieve import Hit

    hits = []
    for item in (payload.get("query") or {}).get("search") or []:
        title = str(item.get("title") or "")
        snippet = re.sub(r"<[^>]+>", "", str(item.get("snippet") or ""))
        snippet = " ".join(snippet.split())
        if title:
            hits.append(
                Hit(source="wikipedia", title=title, text=snippet, module=None, untrusted=True)
            )
    return hits


def parse_oeis(payload: dict) -> list:
    from aimath.knowledge.retrieve import Hit

    hits = []
    for item in payload.get("results") or []:
        title = str(item.get("name") or item.get("number") or "OEIS")
        data = str(item.get("data") or "")
        hits.append(Hit(source="oeis", title=title, text=data[:240], module=None, untrusted=True))
    return hits


def search_wikipedia(query: str, limit: int = 3, http_get=None) -> list:
    getter = http_get or _get_json
    payload = _as_dict(getter(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": str(limit),
        },
    ))
    return parse_wikipedia(payload)[:limit]


def search_oeis(query: str, limit: int = 3, http_get=None) -> list:
    getter = http_get or _get_json
    payload = _as_dict(getter("https://oeis.org/search", {"fmt": "json", "q": query}))
    return parse_oeis(payload)[:limit]


def _as_dict(payload) -> dict:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}
    return {}


def _get_json(url: str, params: dict) -> dict:
    import httpx

    response = httpx.get(url, params=params, timeout=30, follow_redirects=True)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else {}


@dataclass(frozen=True)
class NoveltyReport:
    verdict: str
    summary: str
    open_problem: str | None
    literature: tuple[str, ...]


def assess_novelty(statement: str, *, in_mathlib: bool, in_corpus: bool, literature: list) -> NoveltyReport:
    """Say how this statement sits against Mathlib, this corpus, and untrusted notes.

    `new_to_this_corpus` means those checks did not find it. It does not mean the
    statement is new to mathematics.
    """
    titles = tuple(f"{hit.source}: {hit.title}" for hit in literature if getattr(hit, "untrusted", False))
    problem = match_open_problem(statement)
    problem_name = None if problem is None else str(problem["name"])
    if in_mathlib:
        verdict = "known_in_mathlib"
        summary = "Already in Mathlib. Not a new theorem."
    elif in_corpus:
        verdict = "already_in_corpus"
        summary = "Already recorded in this corpus."
    elif problem_name:
        verdict = "adjacent_to_open_problem"
        summary = (
            f"This names the open problem '{problem_name}'. "
            "A tactic script here is not a solution of it."
        )
    elif titles:
        verdict = "literature_hits_untrusted"
        summary = (
            "Untrusted notes mention related text ("
            + "; ".join(titles[:4])
            + "). Only a Lean proof can become a theorem, and that still would not "
            "show the result is new to mathematics."
        )
    else:
        verdict = "new_to_this_corpus"
        summary = (
            "Not found in Mathlib, this corpus, the open-problem catalog, or the sources "
            "that were searched. That is new to this system, not a claim of a new mathematical truth."
        )
    return NoveltyReport(verdict, summary, problem_name, titles)
