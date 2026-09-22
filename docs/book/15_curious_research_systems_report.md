# Chapter 15 — `curious`, `research`, `system`, and `report`

## `curious` — scheduled wandering, not a mind

```text
aimath curious [--steps N] [--personality NAME]
```

For `step` in `0 .. steps-1`:

1. `next_question(step, seed)` picks a **field** from a fixed cycle: algebra, combinatorics, number theory, geometry, analysis, physics, music, computation.
2. It picks a personality from the roster advanced by `step`.
3. If the field lexically matches an open problem (the matcher is on the field string, which is usually too short to match “Riemann hypothesis”), a warning note may appear. The note always tells the model to ask for a nearby Lean lemma and not to claim an open problem.
4. Retrieval runs on the field.
5. `explore` is called with `steps=1` and a domain string that includes the note and hint titles.

Curiosity is therefore **explore with a rotating domain**. It does not run when you are idle unless you wrap it in Task Scheduler or cron. There is no daemon in 0.1.x.

Physics and music are in the cycle to satisfy “inspiration from widely different fields.” The inspiration is a prompt. If the model emits a precise Lean proposition, good. If it emits a poem, Lean rejects it.

## `research` — definitions that earn keep

```text
aimath research [--steps N] [--personality NAME]
```

Each step asks the model for JSON:

```json
{
  "name": "Double",
  "definition": "def double (n : Nat) : Nat := n + n",
  "goal": "forall n : Nat, double n = n + n",
  "tactics": "intro n; rfl"
}
```

Rules:

- `definition` must start with `def `.
- There must be a goal.
- Combined text must not contain banned tokens.
- The rendered file imports Mathlib, opens `namespace AimathResearch.Name`, includes the def, proves `theorem aimath_uses_def : (goal) := by tactics`, and closes the namespace.

If Lean rejects, any existing file for a failed new name is not kept; a previous kept file is not deleted just because a later step failed. The code unlinks the path if the check failed after write... actually it writes only after success for the happy path: it checks, and on failure it unlinks if the path exists. On success it writes. Read `research_step` if you change this; the test `test_research_keeps_only_a_proved_definition` requires that a failed Triple does not remain on disk.

A kept definition also stores a statement row as theorem with a detail that names the definition. That theorem is the consequence, not a claim that the definition was unknown to mathematics.

Research is how this project answers “come up with new systems” without filling the disk with unchecked axioms. Prefer `research` for definitions. Prefer `system` for explicit extra axioms you mean to study as assumptions.

## `system load`

```text
aimath system load FILE.yaml
```

Does **not** need an LLM (`need_llm=False`). Needs Mathlib, because the axiom file is checked with imports.

YAML shape:

```yaml
name: Parity
notes: optional commentary
axioms:
  - name: zero_even
    statement: "∃ k : Nat, 0 = 2 * k"
```

`name` is required. `axioms` must be a non-empty list of `{name, statement}`.

`render_system` always starts with `import Mathlib` (or other imports if you change code). It sanitizes the name to a Lean identifier (`lean_ident`). Notes are stuffed into a block comment with `-/` broken so they cannot escape the comment.

Axioms become `axiom ident : statement` inside `namespace User.Name`.

Lean checks that file. On success, status **accepted**, file written to `lean_ws/Aimath/User/Name.lean`. On failure, status **proposed**, still written so you can read the error, and `--system` will refuse it.

`sorry` in the rendered source forces proposed with a clear reason.

## `system propose`

```text
aimath system propose [--personality NAME]
```

Asks the model for the same JSON shape `load_system_data` understands, then `install_system`. Garbage JSON becomes rejected with a parse message. A well-formed but Lean-failing system is proposed.

Treat proposed axioms as fiction until accepted, and as **assumptions** even after accepted.

## `report`

```text
aimath report
```

Does not need Mathlib or an LLM. Needs a config so it knows where the sqlite and the work root are.

Ranking key: theorem (0), conjecture (1), known (2), rejected (3), then shorter statements first. The human report is for attention, not for mathematical importance. A short silly theorem outranks a long deep conjecture. That is a UI choice. Change `rank_records` if you hate it, but then say so in this chapter.

`Report.lean` includes only accepted sources from attempts. If you have a theorem row without a stored accepted attempt (should be unusual), the export may skip it.

Overwrite behavior: every report replaces the two files.

## After this chapter

You have the full command surface except distribution. Chapter 16 is serve/worker. Chapter 17 is the status words as a contract you can memorize.
