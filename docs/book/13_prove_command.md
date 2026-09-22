# Chapter 13 — `prove` in exhaustive detail

This chapter follows `Mathematician.prove` and `cmd_prove` line by line in spirit. If you change the loop, change this chapter.

## Invocation

```text
aimath prove --statement TEXT [--personality NAME] [--attempts N] [--system NAME]
```

Defaults: personality `curious`, attempts `3`, system `mathlib`.

`--config` is a global option before the subcommand: `aimath --config D:\x\aimath.yaml prove ...`

## CLI prelude

The command calls `_open_math(..., need_llm=True)`.

That function:

1. Loads config.
2. Refuses if Mathlib is not ready (elan help if `lake` missing).
3. Probes the host (and lowers priority).
4. Computes the raw budget.
5. Opens the corpus and records library system.
6. Senses disk, GPU, temperature, model TCP latency.
7. Reads recent timings; if both lean and llm averages exist, builds a `Timings`.
8. Steers the budget.
9. Builds the LLM client (required here).
10. Starts a `Scheduler` with a process pool for Lean and a thread pool for LLM.
11. Builds a `Retriever` with arxiv/web/notes/foreign flags.
12. Wraps `lean_check_job` so each check records a lean timing.
13. Wraps `client.complete` so each call records an llm timing.

If the client cannot be built, you never enter the loop.

On the way out, `finally` closes scheduler and corpus even if prove threw.

Exit code 0 if status is `theorem` or `known`. Otherwise 1. Conjecture is a non-zero exit. That is correct for scripts: “not proved” is a failure of the command’s hope, not a crash.

## Enqueue

The first thing `prove` does is enqueue a `WorkItem` of kind `prove` with the statement, system, and personality. The local scheduler’s backlog is a list. In 0.1.x this backlog is mostly observational: the prove loop itself is synchronous. The item exists so a future worker or a log can see the same shape. Swarm and tests assert that enqueue happened.

## Rejection before Lean

The statement is stripped.

If it is empty, or `is_trivial` (`True`, `False`, `trivial` after compacting whitespace, case-insensitive), or `find_banned` sees `sorry`/`admit` in the statement itself, the corpus records **rejected** and the function returns. No model call.

## Already recorded

If the same system + normalized text already has status `theorem` or `known`, prove returns that status with detail “already recorded in this corpus.” It does not prove again. Delete the sqlite row if you truly want a redo (advanced; backup first).

## Mathlib known

If system is `mathlib`, `known_in_mathlib` runs. On a hit, status **known**, detail names title and module, no model call.

## Imports and typecheck

`modules_for` returns up to four Mathlib modules or `["Mathlib"]`.

If `--system` is not `mathlib`, `_system_import` requires that system’s status to be `accepted` and adds `Aimath.User.<LeanIdent>`. If you pass a name that is not accepted, `ValueError` bubbles to the CLI.

Typecheck source is built. If the typecheck source somehow contains a banned token (should be rare), rejected.

The checker runs. If it fails and imports were not already `["Mathlib"]`, imports become `["Mathlib"]` and typecheck runs again. If it still fails, rejected with truncated stderr.

On success, a statement row is stored as **conjecture** with detail that it typechecks.

## The attempt loop

`attempts` is at least 1.

Each iteration:

1. Enqueues `prove` or `critique` (if there was feedback).
2. Calls the model with `SYSTEM_PROMPT + personality.bias` and a user prompt that lists imports and any previous error.
3. Extracts tactics.
4. Renders a proof file.
5. If banned tokens, records an attempt failure and sets feedback asking to rewrite without sorry/admit. Continues.
6. Otherwise checks Lean. Records the attempt with the output.
7. If accepted: status **theorem**, detail mentions relativity if needed, returns with `lean_src`.
8. If not: feedback is the error, truncated.

If the loop ends, status stays **conjecture** with detail that no proof was accepted in the attempt budget.

## What is stored on each attempt

`add_attempt` stores the full Lean source and a short output. Failed search attempts (other command) prefix `tactic:name` so `failed_tactics` can skip them. The prove path stores raw Lean errors. Search and prove share the attempts table.

## Personalities

An unknown personality raises `ValueError` listing the known names. The CLI prints that and exits 1.

## `--system` besides mathlib

You must have loaded and accepted the system. The proof file imports Mathlib modules plus `Aimath.User.Name`. The User file must exist from `install_system`. If you deleted the Lean file but left sqlite accepted, checks may fail with unknown import. Reload the yaml.

## Performance notes

The first typecheck after init may compile a huge cone. Subsequent checks in the same process do not keep a warm Lean server: each check is a **new** `lake env lean` process. That is simple and slow. A persistent `lean --server` would be faster and is not 0.1.x. Timeouts of 180 seconds are for the cold case.

## After this chapter

You can draw the prove flowchart on paper. Chapter 14 is the other ways to look for a proof.
