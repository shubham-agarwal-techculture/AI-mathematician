# Search, swarm, and research

## Search (prover scale, local)

`aimath search` is the tactic-beam prover:

- Ladder first (cheap, no model if success comes early).
- Remember failures.
- Ask the model for more scripts.
- Reserve beam slots for model proposals so the ladder cannot monopolize every slot.

This is not Aesop’s full search tree and not a hammer over all of Mathlib. It is a practical beam with premise imports from retrieval.

## Swarm (many agents)

`aimath swarm` expands a large backlog of logical agents. Live concurrency is host-capped. First theorem wins.

## Research (new systems that earn their keep)

`aimath research` invents a definition and a consequence. The definition is kept only when the consequence checks. Useless inventions are dropped. That is the project’s answer to “come up with new equations and systems” without flooding the workspace with unchecked axioms.
