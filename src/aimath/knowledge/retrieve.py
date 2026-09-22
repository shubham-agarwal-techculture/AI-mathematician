"""Search Mathlib first, then this corpus, then optional untrusted arXiv abstracts."""

from __future__ import annotations

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from aimath.knowledge.corpus import Corpus
from aimath.textutil import compact, normalize

_ATOM = {"a": "http://www.w3.org/2005/Atom"}
_DECL = re.compile(
    r"^(?:@\[.*?\]\s*)*(theorem|lemma|def|abbrev|axiom)\s+([A-Za-z_][A-Za-z0-9_'.]*)",
    re.M,
)
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_'.]*")


@dataclass(frozen=True)
class Hit:
    source: str
    title: str
    text: str
    module: str | None
    untrusted: bool


def mathlib_root(workspace: Path) -> Path | None:
    root = workspace / ".lake" / "packages" / "mathlib"
    return root if root.is_dir() else None


def module_name(package_root: Path, file: Path) -> str:
    rel = file.resolve().relative_to(package_root.resolve())
    return ".".join(rel.with_suffix("").parts)


def _tokens(query: str) -> list[str]:
    return [tok.lower() for tok in re.findall(r"[A-Za-z0-9_'.]+", query) if len(tok) >= 3]


def _lean_files(root: Path) -> list[Path]:
    base = root / "Mathlib"
    if not base.is_dir():
        base = root
    files: list[Path] = []
    for path in base.rglob("*.lean"):
        rel = path.relative_to(root)
        if any(part in {".lake", ".git"} for part in rel.parts):
            continue
        files.append(path)
    return files


def _rg_files(root: Path, pattern: str, limit: int) -> list[Path]:
    rg = shutil.which("rg")
    if rg is None or not pattern:
        return []
    try:
        completed = subprocess.run(
            [rg, "-l", "-F", "-g", "*.lean", "--max-filesize", "1M", pattern, str(root)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    paths = []
    for line in completed.stdout.splitlines():
        if line.strip():
            paths.append(Path(line.strip()))
        if len(paths) >= limit:
            break
    return paths


def _files_touching(root: Path, needle: str, limit: int) -> list[Path]:
    if not needle:
        return []
    found = _rg_files(root, needle, limit)
    if found:
        return found
    low = needle.lower()
    squashed = compact(low)
    out: list[Path] = []
    for path in _lean_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        folded = text.lower()
        if low in folded or (squashed and squashed in compact(folded)):
            out.append(path)
        if len(out) >= limit:
            break
    return out


def _decl_before(text: str, statement: str) -> str | None:
    """Name of the last declaration that starts at or before `statement` in `text`."""
    target = compact(statement)
    blob = compact(text)
    start = blob.find(target)
    if not target or start < 0:
        return None
    count = 0
    cut = len(text)
    for index, char in enumerate(text):
        if char.isspace():
            continue
        if count == start:
            cut = index
            break
        count += 1
    last = None
    for match in _DECL.finditer(text):
        if match.start() <= cut:
            last = match.group(2)
        else:
            break
    return last


def _decl_in_text(text: str, needle: str) -> str | None:
    if not needle:
        return None
    low = needle.lower()
    for match in _DECL.finditer(text):
        name = match.group(2)
        if low in name.lower():
            return name
    return None


def search_mathlib(workspace: Path, query: str, limit: int = 8) -> list[Hit]:
    root = mathlib_root(workspace)
    if root is None:
        return []
    tokens = _tokens(query)
    if not tokens:
        return []
    needle = max(tokens, key=len)
    paths = _rg_files(root, needle, max(limit * 3, limit))
    if not paths:
        scanned = 0
        for path in _lean_files(root):
            scanned += 1
            if scanned > 4000:
                break
            hay = str(path).lower()
            if needle not in hay and needle not in path.stem.lower():
                try:
                    head = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if needle not in head.lower():
                    continue
            paths.append(path)
            if len(paths) >= limit:
                break
    hits: list[Hit] = []
    seen: set[str] = set()
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not any(tok in text.lower() or tok in str(path).lower() for tok in tokens):
            continue
        name = _decl_in_text(text, needle) or path.stem
        module = module_name(root, path)
        if module in seen:
            continue
        seen.add(module)
        hits.append(
            Hit(source="mathlib", title=name, text=name, module=module, untrusted=False)
        )
        if len(hits) >= limit:
            break
    return hits


def known_in_mathlib(workspace: Path, statement: str) -> Hit | None:
    root = mathlib_root(workspace)
    if root is None:
        return None
    ident = statement.strip()
    if _IDENT.fullmatch(ident):
        hits = search_mathlib(workspace, ident, limit=5)
        for hit in hits:
            if hit.title == ident or hit.title.endswith("." + ident):
                return hit
    squashed = compact(statement)
    if len(squashed) < 12:
        return None
    files = _files_touching(root, squashed[:80], 20)
    if not files:
        token = max(_tokens(statement) or [""], key=len)
        files = _files_touching(root, token, 20) if token else []
    for path in files[:30]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if squashed in compact(text):
            name = _decl_before(text, statement) or path.stem
            return Hit(
                source="mathlib",
                title=name,
                text=normalize(statement),
                module=module_name(root, path),
                untrusted=False,
            )
    return None


def parse_arxiv(xml_text: str) -> list[Hit]:
    root = ET.fromstring(xml_text)
    hits: list[Hit] = []
    for entry in root.findall("a:entry", _ATOM):
        title = " ".join((entry.findtext("a:title", default="", namespaces=_ATOM) or "").split())
        summary = " ".join((entry.findtext("a:summary", default="", namespaces=_ATOM) or "").split())
        hits.append(Hit(source="arxiv", title=title, text=summary, module=None, untrusted=True))
    return hits


def search_arxiv(query: str, limit: int = 3, http_get=None) -> list[Hit]:
    getter = http_get or _http_get
    url = "https://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "start": 0, "max_results": str(limit)}
    xml_text = getter(url, params)
    return parse_arxiv(xml_text)[:limit]


def _http_get(url: str, params: dict) -> str:
    import httpx

    response = httpx.get(url, params=params, timeout=30, follow_redirects=True)
    response.raise_for_status()
    return response.text


class Retriever:
    def __init__(
        self,
        workspace: Path,
        corpus: Corpus,
        *,
        arxiv: bool = False,
        web: bool = False,
        notes_dir: Path | None = None,
        foreign_dir: Path | None = None,
        http_get=None,
    ) -> None:
        self.workspace = workspace
        self.corpus = corpus
        self.arxiv = arxiv
        self.web = web
        self.notes_dir = notes_dir
        self.foreign_dir = foreign_dir
        self.http_get = http_get

    def search(self, query: str, limit: int = 8) -> list[Hit]:
        from aimath.knowledge.sources import (
            match_open_problem,
            search_folder,
            search_oeis,
            search_wikipedia,
        )

        hits = search_mathlib(self.workspace, query, limit=limit)
        for row in self.corpus.search(query, limit=limit):
            hits.append(
                Hit(
                    source="corpus",
                    title=str(row["status"]),
                    text=str(row["text"]),
                    module=None,
                    untrusted=False,
                )
            )
        problem = match_open_problem(query)
        if problem is not None:
            hits.append(
                Hit(
                    source="open-problem",
                    title=str(problem["name"]),
                    text=str(problem.get("note") or ""),
                    module=None,
                    untrusted=True,
                )
            )
        hits.extend(search_folder(self.notes_dir, query, "notes"))
        hits.extend(search_folder(self.foreign_dir, query, "foreign"))
        if self.arxiv:
            try:
                hits.extend(search_arxiv(query, limit=3, http_get=self.http_get))
            except Exception:
                pass
        if self.web:
            try:
                hits.extend(search_wikipedia(query, limit=2, http_get=self.http_get))
            except Exception:
                pass
            try:
                hits.extend(search_oeis(query, limit=2, http_get=self.http_get))
            except Exception:
                pass
        return hits[: limit + 8]

    def modules_for(self, query: str) -> list[str]:
        modules: list[str] = []
        for hit in search_mathlib(self.workspace, query, limit=4):
            if hit.module and hit.module not in modules:
                modules.append(hit.module)
        return modules or ["Mathlib"]

    def known_in_mathlib(self, statement: str) -> Hit | None:
        return known_in_mathlib(self.workspace, statement)
