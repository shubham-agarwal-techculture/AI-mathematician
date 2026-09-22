# Expert practitioner guide

Assumes fluency with Lean 4, Mathlib, and LLM tooling.

## Mental model

```text
CLI → Mathematician loop → (LLM thread pool | Lean process pool)
                ↓
         Retriever (Mathlib → corpus → open problems → notes/foreign → web)
                ↓
              Corpus (SQLite)
```

Budgeting happens before pools are sized; steering may shrink caps using disk, temperature, and timing EWMA-like averages of recent lean/llm timings.

## Extension points you will actually touch

| Concern | Module |
| --- | --- |
| Prompt / personality | `agents/personalities.py` |
| Prove loop | `agents/loop.py` |
| Tactic beam | `agents/search.py` |
| Swarm | `agents/swarm.py` |
| Definition research | `agents/research.py` |
| Curiosity | `agents/curiosity.py` |
| Retrieval | `knowledge/retrieve.py`, `knowledge/sources.py` |
| Lean I/O | `lean/sandbox.py`, `lean/project.py` |
| Distribution | `runtime/distributed.py`, `runtime/protocol.py` |
| CLI surface | `cli.py` |

## Performance notes

- Prefer narrow imports; `import Mathlib` is a latency cliff.
- Process pool uses `spawn` (Windows-safe). Keep Lean jobs picklable (`lean_check_job`).
- Retrieval without `rg` walks files; install ripgrep in production.

## Evaluation ideas

- Hold-out set of Lean goals with known short proofs.
- Measure: success rate, attempts to success, wall time, $ cost / local joules.
- Track false “theorem” rate should be ~0 if sorry rejection holds; fuzz for unicode lookalikes if you harden further.

## What “expert mode” is not

There is no hidden flag that relaxes Lean. Expertise is better statements, better retrieval, better budgets, and better evaluation—not bypassing the kernel.
