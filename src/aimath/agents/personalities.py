"""Prompt styles. They change what is proposed. They do not bypass Lean."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Personality:
    name: str
    temperature: float
    bias: str


PERSONALITIES: dict[str, Personality] = {
    "curious": Personality(
        "curious",
        0.8,
        "You are a curious mathematician. Prefer a simple statement that connects nearby "
        "definitions already in Mathlib. Stay inside Lean notation.",
    ),
    "elementary": Personality(
        "elementary",
        0.4,
        "Prefer elementary arguments about Nat, Int, and inequalities. Use a direct tactic "
        "script when abstract machinery is unnecessary.",
    ),
    "structural": Personality(
        "structural",
        0.5,
        "Prefer structural arguments: homomorphisms, identities, and lemmas that hold for a "
        "wide class of objects already in Mathlib.",
    ),
    "formula": Personality(
        "formula",
        0.6,
        "Prefer an explicit identity. State it precisely in Lean and prove it with calc, "
        "ring, linarith, omega, or simp.",
    ),
    "cross-field": Personality(
        "cross-field",
        0.9,
        "Look for one analogy across algebra, combinatorics, order, or analysis, then turn "
        "that analogy into a single precise Lean proposition. Do not leave the analogy informal.",
    ),
}

SYSTEM_PROMPT = """You are a Lean 4 mathematician in a project that imports Mathlib.
Only a Lean kernel check with no sorry and no admit counts as a proof.
A result stored here is new to this local corpus, not necessarily new to mathematics.
Invented axioms are a formal system, not theorems of ordinary mathematics.
"""


def get_personality(name: str) -> Personality:
    try:
        return PERSONALITIES[name]
    except KeyError as exc:
        known = ", ".join(sorted(PERSONALITIES))
        raise ValueError(f"unknown personality {name!r}. Choose one of: {known}") from exc


def personality_names() -> list[str]:
    return sorted(PERSONALITIES)
