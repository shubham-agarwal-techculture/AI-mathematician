# Appendix D — How to write a `--statement` (pedantic)

Most failed runs are not mysterious. The sentence you passed is not the sentence you meant, or it is not a Lean `Prop`. This appendix is a drill.

## Start from English, then refuse English

Write the claim in English on paper.

> Adding zero does nothing.

That is a slogan. It has no quantifier and no type. Rewrite:

> For every natural number n, n plus zero equals n.

Still not Lean. Rewrite:

```text
forall n : Nat, n + 0 = n
```

Now a kernel has a chance.

## Name the type every time

| You said | Lean may hear | Problem |
| --- | --- | --- |
| number | Nat, Int, Rat, Real, … | Different theorems |
| even | `Even n` for a specific type | Must import the right Even |
| prime | Nat prime vs other | Wrong lemmas |

If you do not know the type, you are not ready to prove. Learn the type first.

## Put the quantifiers in the right order

“There exists a number larger than every number” is false (no largest natural).

“For every number there exists a larger one” is true.

Those are `exists n, forall m, ...` versus `forall n, exists m, ...`. The model will swap them. You must not.

## Do not hide hypotheses

Bad: `n + n = 2 * n` with n untyped in your head as “obviously Nat.”

Better: `forall n : Nat, n + n = 2 * n`

If you need evenness: `forall n : Nat, Even n → ...` (only if `Even` elaborates in your imports). If it does not elaborate, the status is rejected, and that is the system working.

## Avoid slogans the triviality filter does not catch

The filter only rejects compact `true`, `false`, `trivial`. It will **not** reject `forall n : Nat, True` if you write that — wait, `True` as the whole statement is trivial, but `forall n : Nat, True` is a different string and may typecheck and even prove. That “theorem” is worthless. You are responsible for not asking worthless questions.

## ASCII on Windows

Use `forall`, `exists`, `->` or Lean arrows if your console is honest. If a paste inserts a fancy `∀` from a website and PowerShell corrupts it, you will get a parse error that looks like Lean is broken. It is not. Retype.

## Full declarations versus bare propositions

If your statement **starts a line** with `theorem`, `lemma`, `example`, or `def`, `render_proof` uses your text as the declaration and does not wrap `theorem aimath_result : (...) := by`. That is for people who already write Lean. Beginners should pass **only the proposition**. If you pass a half-written `theorem foo :` without `:= by`, the file will be nonsense and Lean will say so.

## When Mathlib already has it

If prove returns **known**, you wrote a sentence the retriever thinks is in the library. Celebrate the retrieval. Do not edit sqlite to force theorem. If you wanted the **practice** of proving it anyway, change the wording just enough that verbatim compact match fails — and understand you are then proving a possibly identical fact under a different string. That is training, not discovery.

## When you want a relative theorem

Load a system first. Wait for **accepted**. Then `--system ThatName`. If you skip that, you get ValueError. If you prove under Parity and then tell a friend it is ordinary number theory, you violated Chapter 8.

## A checklist before you press Enter

1. Did I name the type?
2. Did I write forall/exists in the order I mean?
3. Is this True/False/trivial? If yes, stop.
4. Did I type sorry? If yes, stop.
5. Am I naming an open problem as if I will solve it? If yes, stop.
6. Are my quotes straight?
7. Is Mathlib ready and is the model up?

Then run prove or search. Then read the first word of the output before you read the model’s vibes.
