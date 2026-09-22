# Maintainer / operations guide

For people who install, upgrade, backup, and keep aimath healthy on a machine or lab fleet.

The long recipes are book [Chapter 23](../book/23_maintenance_extension.md). Budget arithmetic is [Chapter 11](../book/11_reference_tables.md) and [Chapter 20](../book/20_host_budget.md). Failures: [Appendix A](../book/26_appendix_failures.md). Remember: `aimath serve` in 0.1.x is a protocol endpoint; it does not by itself drain the prove queue.

## Inventory of stateful data

Back up these if you care about them:

- `aimath.yaml` — configuration
- `aimath.sqlite` — corpus
- `notes/`, `foreign/` — local knowledge
- `reports/` — exports
- `lean_ws/Aimath/User/`, `lean_ws/Aimath/Research/` — accepted Lean artifacts

You may omit regenerating:

- `.lake/` packages and cache (re-downloadable via `aimath init`, costly in time/bandwidth)

## Health checks

```powershell
aimath status
aimath resources
lake --version
pytest
```

`mathlib ready: yes` is the critical gate for proving commands.

## Upgrades

1. Snapshot sqlite + yaml.
2. Decide whether to upgrade Mathlib (toolchain pin changes).
3. `aimath init --force` only when intentional.
4. Re-run tests.
5. Smoke-test `aimath prove` on a trivial goal.

## Resource policy

Tune in yaml:

- `host.ram_reserve_ratio`
- `host.lean_worker_gb`
- `host.max_llm_inflight`
- `lean.timeout_seconds`

On shared lab machines, raise the RAM reserve and lower max LLM in-flight.

## Multi-machine verification

- Run `aimath serve` on a coordinator (localhost or tokenized host).
- Point workers with `aimath worker --host ... --port ... --token ...`.
- Monitor disconnect requeues; after three failures a job is dropped.

## Security basics

- Do not expose `serve` without a token off-loopback.
- Treat model API keys as secrets; they live in environment variables named by config.
- Untrusted web content can be fetched; it is never executed as Lean automatically, but do not paste untrusted Lean into trusted files without reading it.

## Logging and support bundle

When filing a bug, collect:

- `aimath status` output
- Relevant sqlite rows / report excerpt
- Lean stderr from a failed check
- Redacted config (no keys)
