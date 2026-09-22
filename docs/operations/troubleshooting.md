# Troubleshooting

The long list of failures (install, PATH, `irm`, OneDrive, model HTTP codes, typecheck, swarm cost, worker tokens, sqlite locks, Unicode) is **Appendix A** of the book: [Failure encyclopedia](../book/26_appendix_failures.md). This page is the short desk card.

## `lake` not found

Install elan. On Windows use `curl.exe` to fetch `https://elan.lean-lang.org/elan-init.ps1`, then open a new terminal.

## `irm` connection closed

Known Windows PowerShell issue with some GitHub raw downloads. Prefer `curl.exe` and the elan.lean-lang.org URL.

## Mathlib not ready

Run `aimath init`. Ensure disk space and network. Check `lean_ws/.lake/packages/mathlib` exists.

## Model returned 401 / key errors

Export the env var named in `llm.api_key_env`. For Ollama, clear `api_key_env` and point `base_url` at `http://127.0.0.1:11434/v1`.

## Every prove is slow

Narrow imports help; full `import Mathlib` is heavy. Lower `lean_workers` via higher RAM reserve. Increase timeout only if checks are legitimately long.

## Out of memory

Raise `ram_reserve_ratio`, lower concurrency, close other apps. Mathlib imports are large.

## Swarm spends too much money

Lower `--agents` and `max_llm_inflight`. Prefer local models for large swarms.

## Worker denied

Token mismatch or missing token on non-loopback serve.

## Tests skipped live Mathlib

Expected until `lean_ws` is initialized. Unit tests should still pass.
