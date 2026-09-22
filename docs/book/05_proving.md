# Chapter 5 — Lean from zero, as aimath uses it

This chapter is not a Lean textbook. It is the minimum Lean a person must know to read aimath’s output and to write a `--statement` that means what they think it means.

## What Lean is

Lean 4 is an interactive theorem prover and a functional programming language. In the same file you can write programs that run and theorems that are checked. aimath cares almost entirely about the second use.

When this book says “Lean accepted the file,” it means: the Lean executable, running in the Mathlib workspace through Lake, processed the file and exited with code 0, and the file did not contain a live `sorry` or `admit`.

## The toolchain, said slowly

You do not download “a Lean” once and forget it. You install **elan**, which is a version manager. elan reads a file named `lean-toolchain` in a project directory. That file contains one line such as:

```text
leanprover/lean4:v4.35.0-rc2
```

When you run `lake` or `lean` inside that directory, elan makes sure that exact version is present. Mathlib is extremely sensitive to this pin. If your toolchain and Mathlib disagree, you get mysterious errors. `aimath init` rewrites `lean-toolchain` from Mathlib’s current pin on purpose.

**Lake** is the build tool. `lake update` fetches packages listed in `lakefile.toml`. `lake exe cache get` downloads prebuilt artifacts so you do not compile all of Mathlib from scratch. `lake env lean myfile.lean` runs Lean with the package environment (so `import Mathlib` works).

aimath never asks you to click a GUI. It shells out to `lake`.

## A file Lean can check

A minimal file in the aimath workspace looks like this:

```lean
import Mathlib

theorem aimath_result : (∀ n : Nat, n = n) := by
  intro n
  rfl
```

Line 1 makes Mathlib’s declarations visible.

The theorem has a name (`aimath_result`), a statement after the colon, and a proof after `:= by`.

If you already wrote a full `theorem ... := by ...` as your statement, aimath will use your text as the declaration instead of wrapping it. That is an advanced convenience. Beginners should pass only the proposition.

## How aimath wraps your statement

If you type:

```text
aimath prove --statement "forall n : Nat, n = n"
```

and the model returns the tactics `intro n` and `rfl`, the sandbox writes approximately:

```lean
import Mathlib
-- or a narrower import if retrieval found one

theorem aimath_result : (forall n : Nat, n = n) := by
  intro n
  rfl
```

The extra parentheses around the statement are deliberate. They keep precedence from surprising you.

If retrieval found `Mathlib.Data.Nat.Basic`, the import line may be that module instead of all of Mathlib. Narrower imports start faster. If typecheck fails with a narrow import, the prove loop falls back to `import Mathlib` and tries again.

## Typecheck without proving

Before wasting model calls on a sentence that is not a proposition, aimath writes a dummy:

```lean
import Mathlib

theorem aimath_typecheck_dummy : (YOUR_STATEMENT) ∨ True := Or.inr trivial
```

Why this trick?

- `YOUR_STATEMENT` must be a `Prop` or Lean will not accept the `∨`.
- `Or.inr trivial` proves the right disjunct, `True`, without proving your statement.
- The file contains no `sorry`.

If this file fails, your statement did not elaborate. There is nothing to prove yet. Status: rejected.

If this file succeeds, your statement is a well-typed proposition. It is still unproved. The loop then asks for tactics.

This dummy is **not** a proof of your claim. If you ever see it in a report as if it were, that is a misunderstanding. The report should only export accepted proofs of the real goal.

## Tactics you will see constantly

`rfl` — reflexivity of equality after definitional unfolding.

`intro` / `intros` — introduce hypotheses and bound variables.

`simp` — rewrite with a database of “simp lemmas.” Powerful and sometimes too powerful.

`ring` — equalities in rings (including many numeral and polynomial identities).

`omega` — linear arithmetic on integers and naturals, in the modern Lean sense.

`norm_num` — close numeric goals.

`linarith` — linear inequalities.

`aesop` — a general automation tactic; may or may not be available depending on imports.

`decide` — try to close a decidable proposition by computation.

`skip` — do nothing. aimath inserts `skip` if the model returns an empty tactic block, so the file is still syntactically a `by` block. `skip` almost never finishes a real goal.

The `search` command tries a **ladder** of these before it asks the model. Equation-shaped goals (a `=` in the statement) try `ring` and `omega` earlier. That is a heuristic, not a theorem about tactics.

## Imports

`import Mathlib` imports the umbrella module. It is convenient and heavy.

`import Mathlib.Data.Nat.Basic` imports one slice.

aimath’s retriever looks at file names and declaration names under the Mathlib package. It is not a full semantic premise selector. It will miss the right import often. The fallback exists because of that.

If you know the right import, you still cannot pass it on the CLI in 0.1.x. You can put related text in the statement or domain string so retrieval has tokens to find. That is clumsy. It is the truth of this version.

## Unicode versus ASCII

Lean loves `∀`, `∃`, `→`, `ℕ`. Windows consoles sometimes hate them.

aimath accepts `forall`, `exists`, and `Nat`. Prefer ASCII on the command line if your terminal mangles Unicode. Inside Lean files, Unicode is fine.

If you paste `∀` into PowerShell and the program sees a different character, you will get a confusing Lean error. Try ASCII.

## Comments and the sorry scanner

Lean line comments start with `--`.

Block comments are `/- ... -/`.

aimath’s `find_banned` walks the source and ignores those comments and string literals. It still forbids the identifiers `sorry` and `admit` in live code.

Do not try to hide a hole as `s!orry` or a unicode lookalike and then call the result a theorem. The kernel is the real defense. The scanner is courtesy and a second fence.

## What you do not need yet

You do not need to write macros.

You do not need to understand reducibility, universe levels, or the equation compiler.

You do not need VS Code, though the Lean extension is the best way to learn if you outgrow the CLI.

You do need to read errors. A Lean error is a gift. A model apology is not.

## After this chapter

You can look at a generated file and know what each part is for. The next chapter explains the library that file is trying to speak.
