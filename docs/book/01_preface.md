# Chapter 1 — How to read this book

This book is the long explanation of **aimath**: a program you run on your own computer that tries to do mathematics in a way a machine can check. The book is written for a reader who may never have heard of Lean, Mathlib, theorem provers, or language-model agents. It is also written for a reader who already lives in those worlds and wants every knob, file, status word, and invariant named without apology. Those two readers are not given two books. They are given one book that starts from the first idea and does not skip the minutes.

If you are completely new, read from this page forward and do not skip the chapters that look “too basic.” The later chapters use the vocabulary of the early ones on purpose. If you already know Lean, still read Part I until the trust rule is boring. Most mistakes with this system are not technical. They are mistakes about who is allowed to call something a theorem.

## What this book is

It is a reference book, a manual, and a course of explanation in one spine.

- A **reference** because later chapters list commands, configuration keys, files, protocol messages, and source modules in enough detail that you should not need to guess.
- A **manual** because it tells you what to type, what should appear, and what each outcome means.
- A **course** because it does not assume you already know what a formal proof is, what a type is, what Mathlib is, or why `sorry` is not a proof.

It is meant to be the **ultimate written source for this repository**. The short README at the root of the project is a front door. The audience pamphlets under `docs/audiences/` are invitations in different tones. This book is the place the pamphlets are allowed to point when a reader says “explain everything.”

## What this book is not

It is not a textbook of mathematics. It will use small facts about natural numbers because those facts are easy to state and easy for Lean to check. It will not teach you calculus, algebra, or analysis. If you do not already know what “for all natural numbers n” means, you can still install the software and run the examples, but you will be watching a machine check sentences you cannot yet interpret. That is allowed. It is not the same as understanding.

It is not a history of Leibniz, Lean, or artificial intelligence. Historical names appear because they explain design choices, not because this book is a biography.

It is not a promise that the software will discover new mathematics. The software can store a Lean-checked proof that is new **to this installation’s notebook**. That is a precise, small claim. The book will repeat that distinction until it is impossible to miss.

It is not a substitute for the Lean kernel. If this book and Lean disagree about whether a file is a proof, Lean is right and the book is wrong.

## The one rule the whole book exists to protect

A language model never decides that something is a theorem.

Lean decides.

Mathlib is the trusted library.

Everything else — Wikipedia, OEIS, arXiv abstracts, your notes, Isabelle or Coq excerpts, the model’s English, a personality named after Euler — is a hint.

If you remember only one paragraph, remember that one.

## How the parts fit together

The book has a plot, even though it is technical.

Part I answers: what would it even mean for a machine to do mathematics carefully? It starts with ordinary school proofs, moves to formal proofs, then to Lean, Mathlib, and language models. You should finish Part I able to say, in your own words, why a fluent paragraph from a chatbot is not a certificate.

Part II answers: what did we actually build? You meet the trust model, the files on disk, the install, and the configuration file. You should finish Part II able to point at `aimath.yaml`, `lean_ws/`, and `aimath.sqlite` and say what each is for.

Part III answers: what do I type? You work through the first hour, then every command. You should finish Part III able to choose among `prove`, `search`, `explore`, `swarm`, `curious`, `research`, `system`, `report`, `serve`, and `worker` without treating them as synonyms.

Part IV answers: what may I say after the machine runs? Novelty language, open problems, personalities. You should finish Part IV unwilling to tell a friend “we proved the Riemann hypothesis” because a model emitted tactics.

Part V answers: how does it use the machine, other machines, and the source tree? Budgets, sockets, SQLite, modules.

Part VI answers: how should different people use this, and how should it be changed without breaking the rule?

The appendices are for lookup after you have read the spine once.

## Typographical conventions

Commands you type appear like this:

```text
aimath prove --statement "forall n : Nat, n + 0 = n"
```

On Windows this is PowerShell unless the text says otherwise. On other systems the same command usually works in bash or zsh. Where Windows is special (elan install, `curl` versus `curl.exe`), the book says so.

File paths appear like `lean_ws/` and `aimath.yaml`. They are relative to the directory where you ran `aimath init`, unless the text says they live inside the source repository.

Status words are written in roman type when they are outcomes: theorem, known, conjecture, rejected. Those four words are not informal English. They are the machine’s vocabulary. Chapter 18 treats them as a contract.

When the book quotes Lean, it uses Lean’s own keywords: `theorem`, `lemma`, `def`, `axiom`, `sorry`, `admit`, `by`, `import`.

When the book says **relative to system S**, it means the proof used extra axioms that are not part of ordinary Mathlib mathematics. That phrase is not decoration. It is a warning label.

## How to work while you read

You can read the whole book before installing anything. Part I is designed that way. From Part II onward, a machine helps. The intended loop is:

1. Read a section.
2. Type the command it names, if you have the tools.
3. Compare what you see with what the book said you would see.
4. If they differ, believe the program’s output about your machine, then read the troubleshooting appendix.

If you cannot install Lean yet, still read. The trust rule does not require a download.

## Voice and pedantry

This book is deliberately slow. It will define “terminal,” “PATH,” “environment variable,” “process,” and “JSON line” when those words first become necessary. It will also define “proposition,” “quantifier,” and “axiom.” The author would rather bore an expert for a page than leave a beginner stranded for a chapter.

Experts are asked to treat the slow pages as a specification of what the project believes a new user must be told. If a later contributor shortens the install chapter until a beginner cannot finish it, that is a documentation regression, not a cleanup.

## Version

The software described is aimath 0.1.x as it exists in this repository: a Python package, a Lake project template that requires Mathlib, SQLite storage, optional web hints, and a localhost-first worker protocol. Features that were explicitly left out of the first plan (full literature search, Aesop-scale proof search, a daemon that researches while you sleep, a paper-quality PDF of original theorems) are named as absences in Chapter 29. The book does not pretend they are present.

## A note on names

**aimath** is the command and the Python package. **Lean 4** is the proof assistant. **Mathlib** is the community library. **elan** is the version manager that puts `lean` and `lake` on your PATH. **Lake** is Lean’s build tool. **An LLM** is a language model: a program that predicts text. In this project it predicts Lean text and English justifications. It is not a kernel.

Named personalities (`euler`, `noether`, `erdos`, `grothendieck`, `ramanujan`) are prompt styles. They are not simulations of those people and they confer no historical authority on a file.

## If you are in a hurry anyway

The honest short path is:

1. Chapter 2 (what a proof is) and Chapter 8 (the trust model).
2. Chapter 10 (install).
3. Chapter 12 (first hour).
4. Chapter 18 (status words).
5. Chapter 19 (what you may claim).

Then come back and read the rest. The short path is not the book. It is a concession.

## Dedication of attention

This book is dedicated to the difference between a sentence that sounds like mathematics and a sentence that has been checked. The software exists to keep that difference visible. The book exists so that a human being, looking at the software, does not blur it again.
