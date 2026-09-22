# Mathematician’s guide

Written for working mathematicians who may be new to Lean agents.

## The one-paragraph pitch

aimath is a lab notebook that refuses to lie about formal status. An LLM proposes Lean text; Mathlib is the ambient library; Lean is the referee. Local novelty is tracked carefully. Historical novelty is your job, as it always was.

## Mapping to familiar practice

| Your practice | aimath analogue |
| --- | --- |
| Scratch paper conjectures | `explore` / `curious` |
| Trying standard lemmas | `search` ladder |
| Asking a colleague for a trick | personality + model |
| Checking a write-up | Lean kernel |
| Reading literature | untrusted retrieval + your own reading |
| Working in an axiomatic setup | `system load` |

## Statement craft matters more than personalities

Garbage goals produce garbage loops. Spend time on:

- Correct quantifier order.
- The exact type (`Nat` vs `Int` vs a Mathlib structure).
- Whether the statement is already a Mathlib lemma under another name.

## Relative results and integrity

If you load axioms, label talks and notes clearly: “In the theory T = Mathlib + Axioms…” Relative formal theorems can still be insightful, just as relative consistency results are.

## Collaboration pattern

1. Human chooses the mathematical question.
2. aimath proposes formalizations and proofs.
3. Human audits Lean, Mathlib overlap, and literature.
4. Human decides significance.
