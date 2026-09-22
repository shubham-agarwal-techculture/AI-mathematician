# Extension guide

How to extend aimath without breaking its trust model.

Read book [Chapter 8](../book/08_host_distribution.md) (trust specification) and [Chapter 21](../book/21_architecture_source.md) (every module) before you write code. If your feature stores `theorem` without Lean, you forked a different project. Chapter 24 lists absences you might be about to fill; fill them without violating Chapter 8.

## Before you write code

Ask:

1. Does this change what can be called a theorem? If yes, require Lean.
2. Does this add a knowledge source? If yes, mark trust level.
3. Does this add concurrency? If yes, respect host budget.

## Add a personality

Edit `src/aimath/agents/personalities.py`:

```python
"my_style": Personality("my_style", 0.5, "Your bias text..."),
```

Add a docs note and a test that `get_personality("my_style")` works.

## Add a CLI command

1. Implement a function in a module under `agents/` or `knowledge/`.
2. Wire `cmd_*` in `cli.py`.
3. Register a subparser in `build_parser`.
4. Add tests that do not download Mathlib.

## Add a knowledge source

1. Parse/search function in `knowledge/sources.py` returning `Hit` with `untrusted=True` unless it is Mathlib.
2. Call it from `Retriever.search` behind a config flag.
3. Document the flag in `config.example.yaml` and `docs/reference/config.md`.
4. Never promote hits to theorems directly.

## Add a work kind

1. Extend `WORK_KINDS` in `runtime/protocol.py`.
2. Teach workers/coordinator what to do (or keep local-only).
3. Update protocol docs and tests for round-trip JSON.

## Add a distributed job type beyond `check`

Today workers handle Lean checks. To add `prove` remotely:

1. Ensure the worker has Mathlib + model access as needed.
2. Pass enough payload (statement, personality, workspace path or source).
3. Return artifacts in `WorkResult.artifact`.
4. Keep sorry rejection on every node.

## Packaging Mathlib-free unit tests

Any new Lean integration test must skip unless `workspace_ready(Path("lean_ws"))`.

## Documentation obligation

Extensions that change user-visible behavior should update:

- `README.md` (brief)
- `docs/manual.md` or a reference page
- A book chapter if conceptual
- Tests

## Example: adding OEIS-like source checklist

- [ ] Config flag
- [ ] Parser + tests with fixture JSON
- [ ] Retriever hook
- [ ] Novelty interaction (still untrusted)
- [ ] Manual blurb
- [ ] Security note (network fetch)
