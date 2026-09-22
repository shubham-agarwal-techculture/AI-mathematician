"""A solver ladder, then a ranked beam of tactic scripts. Failures are remembered."""

from __future__ import annotations

from aimath.agents.loop import ProveOutcome
from aimath.agents.personalities import SYSTEM_PROMPT, get_personality
from aimath.lean.sandbox import render_proof, render_typecheck
from aimath.textutil import find_banned, is_trivial, parse_json_blob

EQUATION_LADDER = ("ring", "omega", "norm_num", "simp", "linarith", "rfl", "aesop", "decide")
GENERAL_LADDER = ("rfl", "simp", "aesop", "omega", "decide", "norm_num", "ring", "linarith")


def rank_scripts(statement: str, extra: list[str], avoided: list[str], beam: int) -> list[str]:
    """Equation goals try closed-form tactics first. Failed scripts are skipped.

    When the model proposed scripts, part of the beam is kept for those scripts
    so the ladder cannot fill every slot.
    """
    ladder = EQUATION_LADDER if "=" in statement else GENERAL_LADDER
    room = max(1, beam)
    proposed = [item.strip() for item in extra if item and item.strip()]
    ladder_budget = room if not proposed else max(1, room - min(len(proposed), max(1, room // 2)))
    banned = set(avoided)
    ranked: list[str] = []

    def add(tactic: str, limit: int) -> None:
        if (
            not tactic
            or tactic in banned
            or tactic in ranked
            or find_banned(tactic)
            or len(ranked) >= limit
        ):
            return
        ranked.append(tactic)

    for tactic in ladder:
        add(tactic.strip(), ladder_budget)
    for tactic in proposed:
        add(tactic, room)
    return ranked


def search_proof(math, statement: str, *, personality: str = "formula", beam: int = 4, system: str = "mathlib") -> ProveOutcome:
    """Try a tactic beam. The ladder does not call the model. Later scripts can."""
    style = get_personality(personality)
    statement = statement.strip()
    if not statement or is_trivial(statement) or find_banned(statement):
        return ProveOutcome("rejected", statement, "empty, trivial, or uses sorry/admit", system)
    if system == "mathlib":
        known = math.retriever.known_in_mathlib(statement)
        if known is not None:
            detail = f"Mathlib already declares {known.title} in {known.module}"
            math.corpus.add_statement(system, statement, "known", personality, detail)
            return ProveOutcome("known", statement, detail, system)
    imports = math.retriever.modules_for(statement)
    type_src = render_typecheck(statement, imports)
    type_result = math.checker(type_src)
    if not type_result.accepted and imports != ["Mathlib"]:
        imports = ["Mathlib"]
        type_result = math.checker(render_typecheck(statement, imports))
    if not type_result.accepted:
        detail = (type_result.stderr or type_result.reason)[-2000:]
        math.corpus.add_statement(system, statement, "rejected", personality, detail)
        return ProveOutcome("rejected", statement, detail, system)
    avoided = math.corpus.failed_tactics(system, statement)
    extra: list[str] = []
    scripts = rank_scripts(statement, extra, avoided, beam)
    outcome = _try_scripts(math, statement, scripts, imports, personality, system, ask_model=False)
    if outcome.status == "theorem":
        return outcome
    raw = math.completer(
        SYSTEM_PROMPT + "\n" + style.bias,
        _search_prompt(statement, style.name, imports, avoided),
        style.temperature,
    )
    try:
        data = parse_json_blob(raw)
        proposed = data.get("scripts") if isinstance(data, dict) else data
        extra = [str(item) for item in proposed] if isinstance(proposed, list) else []
    except (ValueError, TypeError):
        extra = []
    avoided = math.corpus.failed_tactics(system, statement)
    scripts = rank_scripts(statement, extra, avoided, beam)
    return _try_scripts(math, statement, scripts, imports, personality, system, ask_model=True)


def _try_scripts(math, statement, scripts, imports, personality, system, *, ask_model: bool) -> ProveOutcome:
    statement_id = math.corpus.add_statement(
        system, statement, "conjecture", personality, "search has not accepted a proof"
    )
    last = None
    for tactic in scripts:
        src = render_proof(statement, tactic, imports)
        if find_banned(src):
            math.corpus.add_attempt(statement_id, "search", src, False, f"tactic:{tactic}\nbanned")
            continue
        result = math.checker(src)
        output = f"tactic:{tactic}\n{(result.stderr or result.reason)[-2000:]}"
        math.corpus.add_attempt(statement_id, "search", src, result.accepted, output)
        last = src
        if result.accepted:
            detail = "Lean accepted this proof from the tactic beam."
            math.corpus.set_status(statement_id, "theorem", detail)
            return ProveOutcome("theorem", statement, detail, system, src)
    if ask_model:
        math.corpus.set_status(statement_id, "conjecture", "The tactic beam did not find a proof.")
    return ProveOutcome(
        "conjecture",
        statement,
        "The tactic beam did not find a proof.",
        system,
        last,
    )


def _search_prompt(statement: str, personality: str, imports: list[str], avoided: list[str]) -> str:
    premises = ", ".join(imports) or "Mathlib"
    skip = ", ".join(avoided) or "(none)"
    return (
        f"Personality: {personality}.\n"
        f"Goal: {statement}\n"
        f"Premises to import: {premises}\n"
        f"Do not repeat these failed tactics: {skip}\n"
        'Return JSON only: {"scripts": ["simp", "ring"]}. '
        "Each script is a Lean tactic block with no sorry and no admit."
    )
