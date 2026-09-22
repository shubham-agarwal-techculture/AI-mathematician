# Chapter 3 — Formal mathematics and a language precise enough to check

Chapter 2 said a formal proof needs a language, starting sentences, rules, and a checker. This chapter names those pieces as they appear in the world aimath lives in.

## A language that is not English

English is a wonderful language for teaching and a bad language for kernels. The sentence “every space is compact if it is finite” is ambiguous until you say what a space is. The sentence “let G be a group” hides pages of definition.

A formal language fixes syntax. Lean’s syntax is closer to a programming language than to English. You write:

```lean
∀ n : Nat, n + 0 = n
```

or, in ASCII that aimath is happy to accept on the command line:

```text
forall n : Nat, n + 0 = n
```

That string has parts:

- `forall n` — a binder: we are speaking about every n.
- `: Nat` — n is a natural number in Lean’s sense, not a real, not an integer, not a school word.
- `,` — then the body.
- `n + 0 = n` — a proposition about that n.

If you write `forall n, n + 0 = n` without a type, Lean may or may not infer `Nat`. If it infers something else, you proved something else. Always think about types.

## Types, without a course in type theory

A **type** is a kind of object.

`Nat` is the type of natural numbers.

`Int` is the type of integers.

`n + 0` only makes sense if `+` is defined for the type of n.

`True` and `False` are propositions (in fact they are in `Prop`). They are not numbers.

Beginners lose hours because they write a true-sounding sentence at the wrong type. “Every number is even or odd” is false for real numbers and true for integers, with the usual definitions. Lean will not guess which number you meant.

aimath will import Mathlib and ask Lean to elaborate your statement as a `Prop`. If elaboration fails, you get rejected with Lean’s error. Read the error. It is often “unknown identifier” or a type mismatch. It is almost never “the AI is unwise.”

## Definitions are not theorems

A **definition** names a thing.

```lean
def double (n : Nat) : Nat := n + n
```

This does not claim a fact about the world. It says what `double` means.

A **theorem** claims a fact:

```lean
theorem double_eq (n : Nat) : double n = n + n := by rfl
```

aimath’s `research` command asks the model for a definition and a consequence. It keeps the definition only if the consequence checks. That is a design prejudice: new notation must earn its keep by proving something. A definition that merely exists is not a result.

## Axioms are not theorems either

An **axiom** is a starting sentence you are willing to assume.

Mathlib’s ordinary developments use a standard foundation (dependent type theory with the axioms Lean and Mathlib already commit to). You should treat “a Mathlib theorem” as a theorem in that foundation.

When you load a YAML file of extra axioms, you are adding starts. Anything you prove after that is a theorem **in Mathlib plus those axioms**. It may be false in ordinary mathematics. It may be consistent or inconsistent. Lean will not tell you that the axioms are wise. It will only tell you that the file checks.

Chapter 7 and Chapter 16 return to this until the word “relative” is automatic.

## Tactics

A Lean proof can be written as a term (a program that inhabits the proposition) or as a **tactic script** (instructions that build the term).

aimath almost always wants tactics, because language models are better at emitting `simp`, `ring`, `intro`, `rfl` than at emitting full proof terms.

A tiny script:

```lean
theorem demo : ∀ n : Nat, n = n := by
  intro n
  rfl
```

`intro n` moves the universal quantifier into a local hypothesis. `rfl` closes an equality that is definitionally true.

The `by` block is the proof. Everything after `:= by` is what aimath asks the model to write when you `prove`.

## The kernel and the elaborator

Lean is not one blob.

The **elaborator** turns the text you wrote — implicit arguments, tactics, notations — into a fully explicit term.

The **kernel** checks that the term is well-typed and that it has the claimed type (the proposition).

If a tactic is buggy in a way that produces a bad term, the kernel should refuse. aimath’s extra `sorry` scan is a belt in addition to the kernel: even if someone tried to smuggle an unfinished proof, the file is rejected before we celebrate.

You do not need to call the kernel yourself. `lake env lean file.lean` does the work. aimath runs that.

## What “Mathlib” is doing in this story

If Lean is the language and the checker, Mathlib is the enormous pile of already-checked definitions and theorems written in that language: groups, topology, analysis, number theory, and far more.

Without Mathlib, you can still write Lean, but you will reinvent numbers and struggle. aimath therefore **requires** Mathlib. It is not an optional plugin in 0.1.x. Init downloads it. Prove will not start without it.

That requirement has a cost: disk, time, RAM. The book will not hide the cost. It is the price of not working in a toy language.

## What a language model is doing in this story

A language model is a statistical machine that continues text. If you show it a lot of Lean and a lot of English, it will emit more Lean-shaped and English-shaped text.

It does not have a kernel inside it.

It will invent lemma names that do not exist.

It will emit `sorry` if you let it.

It will claim to have proved open problems.

It is still useful, the way a colleague who talks too fast is useful: you take notes, then you check.

aimath’s entire architecture is: let the model talk; let Lean grade; write down only what Lean passed.

## Why this is not “AI that does math” in the movie sense

Movies want a machine that announces new truths. This system announces:

- Lean accepted this file, or
- Lean did not, or
- we already had this in Mathlib or in the notebook, or
- this text names a famous open problem and we will not call a tactic script a solution.

That is a smaller machine. It is the one we can defend.

## A first complete picture

Imagine a desk.

On the left: a talkative intern (the model).

In the middle: a printed encyclopedia that was already refereed line by line (Mathlib).

On the right: a pedantic examiner who only reads Lean (the kernel).

In the drawer: a lab notebook for this room only (SQLite).

On the wall: newspaper clippings (Wikipedia, arXiv, your notes). They are not the encyclopedia.

aimath is the room. You are the person who decides what question is worth putting on the desk.

The next chapter says why anyone historically wanted such a room, and why we used these particular tools.
