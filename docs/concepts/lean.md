# Lean as the language

Lean 4 is an interactive theorem prover and a programming language. In aimath it is the **only** authority for theorems.

## Why Lean

- It has a large modern library (Mathlib).
- It has a precise kernel: if Lean accepts a proof without `sorry`/`admit`, the statement follows from the axioms and definitions in the environment.
- It fits an agent loop: write a file, run `lake env lean`, read success or error.

## How aimath calls Lean

Proof attempts are written as temporary `.lean` files under `lean_ws/.aimath_scratch/`. The checker:

1. Rejects sources containing `sorry` or `admit` as identifiers (comments and strings do not count).
2. Runs `lake env lean` with a timeout.
3. Treats exit code 0 as acceptance.

Typechecking a statement without proving it uses a dummy:

```lean
theorem aimath_typecheck_dummy : (P) ∨ True := Or.inr trivial
```

That elaborates `P` as a `Prop`. Success means the statement is well-typed. It is **not** a proof of `P`.

## What you should learn first

For day-to-day aimath use, learn:

- How to write a proposition about `Nat`, `Int`, or simple structures.
- That tactics live in a `by` block.
- That Mathlib imports matter (`import Mathlib` is broad and slow; narrower modules are better when known).

You do not need to master the entire Lean metaprogramming stack to start.
