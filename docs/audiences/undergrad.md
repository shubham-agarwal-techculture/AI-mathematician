# Undergraduate guide

For students in calculus, linear algebra, discrete math, or a first proofs course.

Read [Appendix D](../book/29_how_to_write_a_statement.md) before you paste homework into `--statement`. Wrong quantifier order is a different theorem. Adding YAML axioms to finish an assignment is academic misconduct in spirit even if Lean says theorem relative to your axioms. Label relative results or do not use `--system`.

## Where aimath fits in a curriculum

| Course topic | How to use aimath |
| --- | --- |
| Discrete math / induction | Formalize Nat statements; prefer `elementary` |
| Linear algebra | Harder: need Mathlib modules; start with simple identities |
| Real analysis | Expect friction; many statements need careful Lean types |
| Abstract algebra | Use `structural` / `noether` personalities; still verify imports |

## Recommended workflow for a homework lemma

1. Write the statement in English.
2. Rewrite it closer to Lean (quantifiers explicit).
3. `aimath prove` with `--attempts 5`.
4. If stuck, `aimath search --beam 6`.
5. Paste the accepted Lean into your own Lean file and simplify tactics until you understand each line.
6. Optional: put course notes in `notes/` so retrieval can hint.

## Common undergraduate mistakes

- Treating `known` as failure. Known means Mathlib already has it—good news for learning, not a bug.
- Using `import Mathlib` mental model for everything: checks become slow; let retrieval suggest modules.
- Adding axioms to “make homework true.” That changes the formal system.

## Projects

- Formalize all exercises from one textbook section that are about Nat/Int.
- Compare personalities on the same goal; write a short report.
- Build a tiny YAML theory of “classroom axioms” and prove relative lemmas.
