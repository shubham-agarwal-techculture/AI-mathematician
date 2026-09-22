# Architecture

## Package map

```text
src/aimath/
  cli.py              user entry
  config.py           yaml loader
  textutil.py         hashing, sorry scan, JSON extraction
  host/               probe, budget, sensors
  runtime/            protocol, scheduler, distributed
  llm/                OpenAI-compatible + Anthropic
  lean/               Mathlib project + sandbox checker
  knowledge/          corpus, retrieve, sources, open problems
  agents/             loop, search, swarm, research, curiosity, report, personalities
  formal/             user formal systems
templates/lean_project/   Lake + Mathlib require
```

## Data flow (prove)

1. CLI loads config, probes host, steers budget, opens scheduler + corpus + retriever.
2. `Mathematician.prove` enqueues a work item.
3. Novelty / Mathlib known checks may return early.
4. Typecheck source is built and checked via process pool.
5. LLM proposes tactics via thread pool.
6. Each attempt is checked; corpus stores attempts.
7. Success → `theorem` (+ optional relative labeling).

## Concurrency model

- **Lean:** `ProcessPoolExecutor` with spawn context (picklable `lean_check_job`).
- **LLM:** `ThreadPoolExecutor`.
- Caps from `Budget`, optionally steered by `steer_budget`.

## Trust boundary

Everything above Lean may hallucinate. The sandbox is the trust boundary for theorem status. Retrieval outside Mathlib is advisory.
