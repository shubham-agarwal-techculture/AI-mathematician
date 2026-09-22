# Master / systems designer guide

This document is for people designing the next generation of aimath-like systems or integrating it into a larger research stack.

## Design invariants (do not break)

1. **Kernel supremacy.** No path stores `theorem` without Lean acceptance and sorry/admit rejection.
2. **Mathlib primacy.** Alternate libraries are hints until formalized.
3. **Relative honesty.** Axiomatic extensions remain labeled.
4. **Host non-invasion.** Default budgets leave headroom; priority stays polite.
5. **Logical scale ≠ process scale.** Queues may be huge; runtimes stay capped.
6. **Local novelty ≠ global novelty.** Language in UI and docs must keep that wedge open.

## Architectural evolution paths

| Direction | Sketch |
| --- | --- |
| Better proving | Premise selection, Aesop integration, hammer calls, learned tactic models |
| Better knowledge | Embeddings over Mathlib, full-text arXiv, curated open-problem DBs |
| Better distribution | Shared durable queue (Redis/NATS), auth, TLS, worker autoscaling |
| Better curiosity | Long-running daemon with human approval gates |
| Better reporting | PDF/LaTeX papers, Lean project export of a theory development |

## Interface contracts worth preserving

- `WorkItem` / `WorkResult` JSON lines.
- `CheckResult.to_dict` picklable job boundary.
- Config sections: `llm`, `host`, `lean`, `knowledge`, `distributed`.

## Philosophical stance

aimath is a **skeptical amanuensis**: prolific in proposals, stingy in certificates. Masters should resist the temptation to optimize for impressive demos that weaken the certificate.
