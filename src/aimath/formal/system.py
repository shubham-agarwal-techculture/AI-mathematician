"""Load a user theory and render it as a Lean namespace on top of Mathlib."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from aimath.lean.sandbox import render_imports

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class Axiom:
    name: str
    statement: str


@dataclass(frozen=True)
class FormalSystem:
    name: str
    notes: str
    axioms: list[Axiom]


def lean_ident(name: str, *, prefix: str = "S") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned or not cleaned[0].isalpha() and cleaned[0] != "_":
        cleaned = prefix + cleaned
    if not _IDENT.fullmatch(cleaned):
        cleaned = prefix
    return cleaned


def load_system(path: Path) -> FormalSystem:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a YAML mapping")
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError(f"{path} is missing name")
    notes = str(data.get("notes") or "")
    raw_axioms = data.get("axioms") or []
    if not isinstance(raw_axioms, list) or not raw_axioms:
        raise ValueError(f"{path} needs a non-empty axioms list")
    axioms: list[Axiom] = []
    for item in raw_axioms:
        if not isinstance(item, dict):
            raise ValueError("each axiom must be a mapping with name and statement")
        axiom_name = str(item.get("name") or "").strip()
        statement = str(item.get("statement") or "").strip()
        if not axiom_name or not statement:
            raise ValueError("each axiom needs name and statement")
        axioms.append(Axiom(axiom_name, statement))
    return FormalSystem(name=name, notes=notes, axioms=axioms)


def load_system_data(data: dict) -> FormalSystem:
    name = str(data.get("name") or "").strip()
    notes = str(data.get("notes") or "")
    axioms = []
    for item in data.get("axioms") or []:
        if not isinstance(item, dict):
            continue
        axiom_name = str(item.get("name") or "").strip()
        statement = str(item.get("statement") or "").strip()
        if axiom_name and statement:
            axioms.append(Axiom(axiom_name, statement))
    if not name or not axioms:
        raise ValueError("a formal system needs a name and at least one axiom")
    return FormalSystem(name=name, notes=notes, axioms=axioms)


def render_system(system: FormalSystem, imports: list[str] | None = None) -> str:
    """User axioms extend Mathlib. They do not replace it."""
    ns = lean_ident(system.name)
    lines = [render_imports(imports or ["Mathlib"]), ""]
    if system.notes.strip():
        note = system.notes.strip().replace("-/", "- /")
        lines.append(f"/- {note} -/")
    lines.append(f"namespace User.{ns}")
    for axiom in system.axioms:
        lines.append(f"axiom {lean_ident(axiom.name, prefix='ax')} : {axiom.statement.strip()}")
    lines.append(f"end User.{ns}")
    lines.append("")
    return "\n".join(lines)


def system_module(system: FormalSystem) -> str:
    return f"Aimath.User.{lean_ident(system.name)}"


def write_system_file(workspace: Path, system: FormalSystem, source: str) -> Path:
    folder = workspace / "Aimath" / "User"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{lean_ident(system.name)}.lean"
    path.write_text(source, encoding="utf-8")
    return path
