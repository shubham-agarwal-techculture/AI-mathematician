# High school guide

You do not need a university math degree to try aimath. You do need patience with installation and honesty about what the computer is doing.

If you want every minute of the install and every status word defined slowly, use [Getting started](../getting-started.md) and then book [Chapters 2](../book/02_vision.md), [10](../book/10_extension_maintenance.md), and [12](../book/12_afterword.md). This page is the short path.

## The big idea in plain words

Imagine three classmates:

1. One classmate invents statements and proof ideas (the AI).
2. One classmate owns a huge, carefully checked textbook (Mathlib).
3. One classmate is a strict grader who only accepts fully correct write-ups (Lean).

aimath is the classroom where those three work together. The AI can be creative and wrong. The grader never grades on confidence. The textbook is trusted; random websites are not.

## What you can safely try

Good first goals:

- Properties of natural numbers: adding zero, commutativity of addition (when formalized), simple inequalities.
- Statements written clearly: “for every natural number n, n + 0 = n”.

Avoid:

- Famous unsolved problems (“prove the Riemann hypothesis”). The tool will warn you; it will not magically solve them.
- Believing a chatty explanation without a Lean check.

## A tiny session

1. Finish [Getting started](../getting-started.md).
2. Run:

```powershell
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary
```

3. Read the status word: `theorem`, `known`, `conjecture`, or `rejected`.
4. Run `aimath report` and open `reports/report.md`.

## How this helps learning

- It forces precision: vague English becomes a precise proposition.
- It shows failure honestly: a wrong tactic is rejected.
- It connects to a real research library (Mathlib) used by professionals.

## How this does not replace learning

You still need to understand definitions. If you cannot explain what “for all n” means, a successful proof is a magic trick, not understanding. Use aimath as a lab, not as a substitute for thinking.
