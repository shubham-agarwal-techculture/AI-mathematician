"""Pick the next question from a rotating field. Idle curiosity does not solve open problems."""

from __future__ import annotations

from aimath.agents.personalities import field_for_step, roster
from aimath.knowledge.sources import match_open_problem


def next_question(step: int, seed: str = "curious") -> tuple[str, str, str]:
    """Return domain, personality, and a prompt note for this curiosity step."""
    field = field_for_step(step)
    personality = roster(seed, step + 1)[-1]
    problem = match_open_problem(field)
    if problem is not None:
        note = (
            f"Field {field} is near the open problem '{problem['name']}'. "
            "Ask for a nearby lemma in Lean. Do not claim to solve the open problem."
        )
    else:
        note = (
            f"Draw one precise Lean lemma from {field}. "
            "If the hint is from another subject, formalize the analogy. Do not leave it informal."
        )
    return field, personality, note


def curious_step(math, step: int, seed: str = "curious"):
    field, personality, note = next_question(step, seed)
    hints = math.retriever.search(field, limit=4)
    hint_text = "; ".join(f"{hit.source}: {hit.title}" for hit in hints[:4]) or "no external hits"
    domain = f"{field}. {note} Hints: {hint_text}"
    return math.explore(domain, personality, steps=1)
