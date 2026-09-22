# What counts as a proof

In informal mathematics, a proof is an argument that convinces a competent reader. In aimath, a proof is a Lean source that:

(For school-level explanation of claims, examples, induction, and why “a computer printed True” is not a proof, start at book [Chapter 2](../book/02_vision.md). For the status contract, [Chapter 17](../book/17_statuses.md).)

1. Elaborates in the Mathlib workspace (plus any accepted user system imports).
2. Completes with Lean exit code 0.
3. Contains neither `sorry` nor `admit` as live identifiers.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| theorem | Kernel-accepted proof stored in this corpus |
| known | Already present as Mathlib text / declaration |
| conjecture | Well-typed, unproved within budget |
| rejected | Ill-typed, trivial, or banned tokens |
| accepted / proposed | Formal system statuses |

## Relative theorems

If you prove something using axioms in system `S`, the report should say it is a theorem **relative to S**. That is not a cheat; it is accurate bookkeeping. Hilbert-style formal systems always relativize results to axioms.

## Failed attempts matter

Failed tactic attempts are stored. Search skips them later. This is a small form of learning from failure—not neural fine-tuning, but corpus memory.
