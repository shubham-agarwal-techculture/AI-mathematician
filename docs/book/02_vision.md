# Chapter 2 — What a proof is, beginning from school

Before this book talks about Lean, it talks about ordinary proofs. If you skip this chapter, later chapters will sound like a religion: “the kernel said so.” This chapter is why anyone should care what a kernel says.

## A claim

Here is a claim you may have seen in school:

> For every natural number n, n + 0 = n.

The natural numbers, in the school sense, are 0, 1, 2, 3, and so on. The claim says: if you take any one of those numbers and add zero, you get the same number back.

Is the claim true? Most people say yes. Why? Because “adding zero does nothing.” That is an explanation. It is not yet a proof in the sense this book needs, but it is the right kind of start: it tries to say why, not merely to repeat the claim more loudly.

## An argument that would pass in a classroom

A teacher might accept this:

> Zero is the additive identity of the natural numbers. By the definition of addition, n + 0 is n. Therefore the claim holds for every n.

A stricter teacher might want induction:

> Base case: 0 + 0 = 0.
> Inductive step: if k + 0 = k, then (k+1) + 0 = (k + 0) + 1 = k + 1.
> By induction the claim holds for all natural numbers.

Both arguments have the shape of a proof: they start from things the class has already agreed to (definitions, earlier lemmas, the induction principle) and they arrive at the claim by steps the class has already agreed are legal.

That last sentence is the whole subject of formal mathematics. A proof is not a feeling. It is a chain of allowed steps from allowed starting points.

## An argument that would not pass

> I asked a clever friend and the friend said it was true.

> I tried n = 0, 1, 2, 3, 4 and it worked, so it is always true.

> The equation looks balanced.

> A computer printed “True.”

The second of those is interesting. Checking examples is good science and good habit. It is not a proof of a “for all n” claim unless you have a theorem that says those examples are enough. Five examples are not every natural number.

The last of those is the trap this software exists to avoid. Computers print “True” for many reasons: a bug, a heuristic, a language model imitating a textbook, a test that only checked the first case. This book will not treat a printed word as a proof.

## What “allowed steps” means

In a classroom, allowed steps are social. The teacher and the textbook say what you may use. Different classrooms disagree. One class has already proved that addition is commutative. Another has not, and must not use that fact yet.

In a computer, allowed steps can be made mechanical. You fix:

1. A language in which claims and steps are written.
2. A list of starting sentences (axioms and definitions).
3. A list of rules that turn old sentences into new ones.
4. A program that checks that each step is one of those rules.

If the program accepts a text, then — relative to those axioms, definitions, and rules — the last sentence follows. That is a **formal proof**.

Formal is not a compliment. It means “according to a form.” A formal proof can be about a silly axiom system. It can prove things that are false in the physical world if you chose silly axioms. Its virtue is not wisdom. Its virtue is that the check does not depend on the author’s confidence.

## Why formal proofs matter if you already “know” the math

They matter when:

- The argument is long and humans lose track of cases.
- The definitions are delicate (what is a real number, a manifold, a scheme).
- Two people disagree and shouting will not settle it.
- A machine proposed the argument, and machines are fluent liars.

aimath is built for the last case especially. A language model can write a paragraph that looks like the inductive proof above and still be wrong in a way a tired human misses. A kernel does not get tired in that way. It also does not understand. It only checks form.

## Propositions

A **proposition** is a sentence that can be true or false.

“7 is prime” is a proposition.

“Hello” is not.

“n + 0 = n” is a proposition once n is given a type, or it is a proposition with a hidden “for all n” depending on how you write it. Precision about that is not pedantry. It is the difference between a statement Lean can elaborate and a string of English the model liked.

In Lean, the type of propositions is called `Prop`. You do not need to master type theory to use aimath, but you need this much: the software will try to treat your `--statement` as a `Prop`. If it cannot, the status will be rejected, and that rejection is a kindness. It means the sentence was not even a well-formed claim yet.

## Quantifiers, said slowly

**For all** (written `forall` or `∀`) says: no matter which object of this kind you pick, the rest is true.

**There exists** (written `exists` or `∃`) says: at least one object of this kind makes the rest true.

School English hides quantifiers. “The sum of two evens is even” means: for all integers a and b, if a is even and b is even, then a+b is even. If you forget the “for all,” you have a different sentence.

aimath does not fix your quantifiers for you. If you write a weaker sentence, it may prove a weaker sentence and you may think you proved the stronger one. That is a human error the kernel cannot catch, because the weaker sentence is still a real theorem.

## Equality

“=” in Lean is a proposition: `a = b` is something that can have a proof. It is not an assignment like `a = a + 1` in some programming languages. Lean is both a programming language and a proof language. In the proofs this book cares about, `=` is the mathematical relation.

`rfl` (reflexivity) proves `a = a` when both sides are already the same after Lean’s definitional computation. Many “obvious” equations are `rfl` once definitions unfold. Many others are not. The model loves to say `rfl` when it is not enough. Lean will refuse.

## Induction, informally

Induction is a legal way to prove “for all natural numbers n, P(n)” if you prove P(0) and you prove that P(k) implies P(k+1). School courses sometimes treat induction as a magic template. In Lean it is a lemma or a tactic arising from how `Nat` is defined: a natural number is zero or the successor of a natural number.

aimath may or may not invent a correct induction. You should still know what induction is, so that you can tell a good script from a cargo-cult script that mentions “induction” and then uses `sorry`.

## `sorry` as a moral object

In Lean, `sorry` fills a hole. It lets a file elaborate while a proof is unfinished. It is a wonderful tool for humans writing a development. It is a disaster if you call the hole a theorem.

aimath treats `sorry` and `admit` as banned identifiers in sources it is willing to accept. A comment containing the word is allowed. A string containing the word is allowed. A live tactic `sorry` is not a proof. This is not optional and not configurable in 0.1.x. If a later version adds a “draft mode,” it must not write the status theorem. That would be a betrayal of Chapter 1.

## Two kinds of certainty people confuse

**Mathematical certainty** (informal): the community of mathematicians is convinced.

**Kernel certainty** (formal): a specific checker accepted a specific file in a specific axiom system.

These can come apart.

A kernel-accepted file can formalize a statement nobody finds interesting.

A community-accepted theorem can wait years to be formalized.

A kernel-accepted file in a silly axiom system can “prove” almost anything.

aimath only ever offers the second kind, plus a notebook of what this machine has seen. When humans say “we proved it,” they usually mean the first kind. Do not launder the second into the first.

## What you should be able to say after this chapter

- A proof is a chain of allowed steps from allowed starts, not a vibe.
- Examples are not proofs of universal claims.
- Formal proofs make “allowed” mechanical.
- Formal proofs are relative to axioms.
- `sorry` is a hole.
- A chatbot’s fluency is not a checker.

The next chapter takes the same ideas into the language Lean actually uses, still slowly.
