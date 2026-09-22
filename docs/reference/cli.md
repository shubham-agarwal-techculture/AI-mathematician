# CLI reference

All commands: `aimath [--config PATH] <command> ...`

Also: `python -m aimath ...`

## `init`

```text
aimath init [--force]
```

Create `aimath.yaml` (if missing) and Mathlib workspace `lean_ws/`.

## `resources`

```text
aimath resources
```

Print host probe, sensors, and budget.

## `status`

```text
aimath status
```

Config path, Mathlib readiness, LLM identity, arxiv flag, statement counts, systems, then resources.

## `prove`

```text
aimath prove --statement TEXT [--personality NAME] [--attempts N] [--system NAME]
```

Defaults: personality `curious`, attempts `3`, system `mathlib`.

Exit code 0 on `theorem` or `known`, else 1.

## `explore`

```text
aimath explore --domain TEXT [--personality NAME] [--steps N]
```

Defaults: personality `curious`, steps `5`.

## `search`

```text
aimath search --statement TEXT [--personality NAME] [--beam N] [--system NAME]
```

Defaults: personality `formula`, beam `4`, system `mathlib`.

## `swarm`

```text
aimath swarm --statement TEXT [--agents N] [--personality NAME]
```

Defaults: agents `8`, personality `curious`.

## `research`

```text
aimath research [--steps N] [--personality NAME]
```

Defaults: steps `1`, personality `structural`.

## `curious`

```text
aimath curious [--steps N] [--personality NAME]
```

Defaults: steps `1`, personality `curious`.

## `system load`

```text
aimath system load FILE.yaml
```

## `system propose`

```text
aimath system propose [--personality NAME]
```

Default personality `structural`.

## `report`

```text
aimath report
```

Writes `reports/report.md` and `reports/Report.lean`.

## `serve`

```text
aimath serve [--host HOST] [--port PORT] [--token TOKEN]
```

Defaults come from `distributed` config. Non-loopback host requires token.

## `worker`

```text
aimath worker [--host HOST] [--port PORT] [--token TOKEN]
```

Defaults: host `127.0.0.1`, port `8765`, empty token.
