# PhD researcher guide

For doctoral students who already know what a proof assistant is and care about research workflow, trust, and limits.

## What aimath buys you

- A local loop that couples LLM proposal with Lean checking against Mathlib.
- Corpus memory of attempts and failures.
- Optional literature hints (arXiv abstracts, Wikipedia, OEIS, notes, foreign prover excerpts) that remain untrusted.
- Swarm/search modes for breadth without claiming completeness of proof search.
- Export suitable for human review (`report`).

## What it does not buy you

- Automatic literature completeness.
- Publication-ready novelty claims.
- A substitute for Isabelle/HOL, Coq, or Metamath libraries (those are hint folders only).
- Guarantees about model honesty; models hallucinate tactics constantly.

## Suggested research workflow

1. Keep a research notes directory synced into `notes/`.
2. Maintain `foreign/` excerpts when translating from another prover.
3. Run `curious` or `explore` on a tightly scoped domain string, not “all of math.”
4. Use `research` to keep definitions only when they prove a consequence.
5. Weekly: `aimath report`, then triage conjectures into “drop”, “human prove”, “needs better statement.”
6. Before any public claim, manually search Mathlib, papers, and textbooks far beyond aimath’s heuristics.

## Formal systems in research

Use YAML systems for:

- Working in a theory with explicit extra axioms you are studying.
- Teaching examples of relativization.

Do not use them to smuggle unproved claims into “theorems” of ordinary mathematics.

## Swarm ethics

Large `--agents` values spend money (cloud APIs) or electricity (local GPUs). Cap agents by experimental design, not by the largest integer that fits in a flag.
