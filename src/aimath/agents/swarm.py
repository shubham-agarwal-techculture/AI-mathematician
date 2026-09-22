"""Many logical agents, drained by the host's worker cap. The first proof stops the rest."""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor

from aimath.agents.loop import ProveOutcome
from aimath.agents.personalities import roster, switch_personality
from aimath.runtime.protocol import WorkItem


def expand_agents(statement: str, agent_count: int, seed: str, budget_ms: int) -> list[WorkItem]:
    """One work item per logical agent. The queue can be large. Live calls are capped elsewhere."""
    items = []
    for index, personality in enumerate(roster(seed, agent_count)):
        items.append(
            WorkItem(
                id=f"agent-{index}",
                kind="prove",
                payload={"statement": statement, "personality": personality, "switch": True},
                budget_ms=budget_ms,
            )
        )
    return items


def run_swarm(math, statement: str, *, agents: int = 8, seed: str = "curious", workers: int = 1) -> ProveOutcome:
    items = expand_agents(statement, agents, seed, math.budget_ms)
    for item in items:
        math.enqueue(item)
    if not items:
        return ProveOutcome("rejected", statement, "no agents were queued", "mathlib")
    winner: ProveOutcome | None = None

    def run_one(item: WorkItem) -> ProveOutcome | None:
        nonlocal winner
        if winner is not None and winner.status == "theorem":
            return None
        personality = str(item.payload["personality"])
        outcome = math.prove(statement, personality, attempts=1)
        if outcome.status != "theorem":
            outcome = math.prove(statement, switch_personality(personality), attempts=1)
        if outcome.status == "theorem":
            winner = outcome
        return outcome

    width = max(1, workers)
    if width == 1:
        for item in items:
            run_one(item)
            if winner is not None and winner.status == "theorem":
                break
    else:
        with ThreadPoolExecutor(max_workers=width) as pool:
            list(pool.map(run_one, items))
    if winner is not None:
        return winner
    return ProveOutcome("conjecture", statement, "The swarm did not accept a proof.", "mathlib")
