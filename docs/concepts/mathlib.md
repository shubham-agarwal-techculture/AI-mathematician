# Mathlib as the library

Mathlib is the community library of formalized mathematics for Lean 4. In aimath it is **primary and required**.

## What “primary” means here

- `aimath init` creates a Lake project that `require`s `leanprover-community` / `mathlib`.
- Search looks in `.lake/packages/mathlib` before the local corpus.
- Proof files import Mathlib modules (or fall back to `import Mathlib`).
- User formal systems **extend** Mathlib; they do not replace it.

## Size and cost

Mathlib’s cache is large. The first download needs network and disk. Full imports are memory-heavy; that is why the host budget assumes roughly 3 GB per Lean worker by default.

## What Mathlib is not

Mathlib is not all of mathematics. Papers, textbooks, and other prover libraries may contain results not yet formalized. aimath can search some of those as **untrusted hints**, but they never become theorems until formalized and checked in Lean.
