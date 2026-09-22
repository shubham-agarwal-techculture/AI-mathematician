"""Invent a definition, try to use it, and keep it only when a consequence is proved."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from aimath.agents.personalities import SYSTEM_PROMPT, get_personality
from aimath.formal.system import lean_ident
from aimath.lean.sandbox import render_imports
from aimath.runtime.protocol import WorkItem
from aimath.textutil import find_banned, parse_json_blob


@dataclass
class ResearchOutcome:
    status: str
    name: str
    detail: str
    lean_src: str | None = None


def research_step(math, personality: str = "structural") -> ResearchOutcome:
    style = get_personality(personality)
    math.enqueue(
        WorkItem(
            id=uuid.uuid4().hex[:12],
            kind="research",
            payload={"personality": personality},
            budget_ms=math.budget_ms,
        )
    )
    raw = math.completer(SYSTEM_PROMPT + "\n" + style.bias, _prompt(style.name), style.temperature)
    try:
        data = parse_json_blob(raw)
    except (ValueError, TypeError) as exc:
        return ResearchOutcome("dropped", "", f"the model did not return a definition: {exc}")
    if not isinstance(data, dict):
        return ResearchOutcome("dropped", "", "the model did not return a definition object")
    name = lean_ident(str(data.get("name") or "discovery"))
    definition = str(data.get("definition") or "").strip()
    goal = str(data.get("goal") or "").strip()
    tactics = str(data.get("tactics") or "rfl").strip()
    if not definition.startswith("def ") or not goal or find_banned(definition + tactics + goal):
        return ResearchOutcome("dropped", name, "a kept definition needs a def, a goal, and no sorry or admit")
    source = (
        render_imports(["Mathlib"])
        + f"\n\nnamespace AimathResearch.{name}\n"
        + definition
        + f"\n\ntheorem aimath_uses_def : ({goal}) := by\n  {tactics}\nend AimathResearch.{name}\n"
    )
    result = math.checker(source)
    path = math.workspace / "Aimath" / "Research" / f"{name}.lean"
    if not result.accepted:
        if path.exists():
            path.unlink()
        math.corpus.add_statement(
            "mathlib", goal, "rejected", personality, "definition did not prove a consequence"
        )
        return ResearchOutcome(
            "dropped",
            name,
            (result.stderr or result.reason)[-2000:],
            source,
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    math.corpus.add_statement(
        "mathlib",
        goal,
        "theorem",
        personality,
        f"Kept definition {name} because Lean accepted a consequence.",
    )
    return ResearchOutcome(
        "kept",
        name,
        f"Kept {name}. Lean accepted a consequence, so the definition stays in the workspace.",
        source,
    )


def _prompt(personality: str) -> str:
    return (
        f"Personality: {personality}.\n"
        "Invent one Lean definition and one consequence that uses it. "
        "The consequence must be provable. This is a formal proposal, not a new truth until Lean accepts it.\n"
        "Return JSON only: "
        '{"name": "Double", "definition": "def double (n : Nat) : Nat := n + n", '
        '"goal": "forall n : Nat, double n = n + n", "tactics": "intro n; rfl"}'
    )
