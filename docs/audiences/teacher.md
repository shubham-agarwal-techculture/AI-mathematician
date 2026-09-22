# Teacher / instructor guide

## Classroom uses

- **Demo of formal verification:** show a wrong tactic rejected live.
- **Lab on quantifiers:** students formalize English statements; aimath checks types.
- **Discussion on AI honesty:** contrast model confidence with Lean outcomes.
- **Project week:** each team maintains a corpus and submits `reports/report.md`.

## Setup for a lab image

1. Pre-run `aimath init` so Mathlib cache is local (saves class time).
2. Pre-configure a local model (Ollama) to avoid API key distribution.
3. Set higher `ram_reserve_ratio` on shared machines.
4. Provide a short allow-list of statements that should succeed quickly.

## Assessment ideas

- Grade the quality of statements and student explanations of Lean proofs, not merely `theorem` status.
- Require disclosure of aimath use.
- Include a question: “Why is `known` not a discovery?”

## Pitfalls

- First-time Mathlib downloads will blow a 50-minute lab.
- Cloud API costs can spike with `swarm`.
- Students may over-trust chat explanations in model traces; teach them to read Lean errors.
