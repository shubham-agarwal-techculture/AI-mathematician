# Chapter 4 — Leibniz’s three pieces, and the tools we used for them

This chapter is the only historical chapter. It exists so that the words “language,” “library,” and “reasoner” in the README are not slogans.

## What Leibniz wanted

Gottfried Wilhelm Leibniz (1646–1716) imagined, at different times and in different texts:

- a **characteristica universalis**: a written language in which ideas could be expressed without the fog of ordinary speech;
- a **calculus ratiocinator**: a way of calculating with those signs so that disputes could be settled by “let us calculate”;
- an organized **encyclopedia** of human knowledge.

Historians argue about how systematic the dream was. This book does not need the argument. It needs the three-part shape: a language, a store of what is already known, and a process that computes with both.

Leibniz did not have Lean. He did not have Mathlib. He did not have GPUs. He had a hope that disagreement could be made mechanical. Formal proof assistants are one of the few places that hope became a daily tool rather than a metaphor.

## What we did not inherit

We did not inherit a language that settles philosophy, theology, or politics. Lean will not tell you whether a definition is the right definition for a research program. It will not tell you whether a theorem is interesting. It will not tell you whether a paper should be published.

We did not inherit an encyclopedia of all mathematics. Mathlib is large and incomplete. Papers, books, and other provers contain work that is not in Mathlib. aimath can peek at some of that work as untrusted text. Peeking is not inclusion.

We did not inherit a reasoner that is a calculus in Leibniz’s sense. A language model is not a decision procedure. It is a proposal engine. The calculus, such as it is, is Lean’s kernel plus tactics like `ring` and `omega`.

If you come to this project hoping for the full Leibniz machine, you will be disappointed unless you keep the mapping honest:

| Leibniz’s piece | What we actually have |
| --- | --- |
| Universal language | Lean 4, which is a specific type theory, not a language of all thought |
| Encyclopedia | Mathlib first; a local notebook; optional clippings |
| Calculator of reasons | Tactics and a kernel; an LLM only to guess the next line |

That mapping is already ambitious. It is not the dream completed.

## Why Lean 4, not a private language

We could have invented a toy syntax. That would make demos easy and mathematics impossible.

Lean 4 is a living language with:

- a small trusted kernel;
- an industrial tactic framework;
- Mathlib;
- a package manager (Lake) and a toolchain pin (`lean-toolchain`);
- a community that already argues about the right way to state lemmas.

aimath is parasitic on that community in the good sense. It does not fork Lean. It writes files and runs `lake env lean`.

## Why Mathlib is required, not optional

An earlier plan sketched Mathlib as optional. That was wrong for this project’s stated aim. A “library of mathematics” that is an empty folder plus Wikipedia is a scrapbook.

Mathlib is the primary library. Init creates a Lake project that `require`s `leanprover-community` / `mathlib`. Search looks there first. User axioms import Mathlib. The local database does **not** copy Mathlib into SQLite. Copying would waste space and go stale. Mathlib lives on disk under `lean_ws/.lake/packages/mathlib`.

## Why a language model at all

Because guessing the next tactic is a place where fluent pattern-matching helps, and because stating a conjecture in Lean syntax is also a place where fluent pattern-matching helps.

The project’s original request asked for thousands or millions of agents, curiosity, and personalities. Those are proposal-side ideas. They are implemented as **queues of tasks** and **prompt styles**, not as millions of operating-system processes. Chapter 15 and Chapter 20 explain that without romance.

If you have no model configured, you can still init, inspect resources, load a system, and write a report. You cannot usefully `prove` in 0.1.x, because the prove loop asks the model for tactics after typecheck. `search` may close some goals with the tactic ladder alone, but the CLI still builds a mathematician that expects a client. Configure a model, even a small local one.

## Why Python around Lean

Lean is the examiner. Python is the laboratory technician: it probes RAM, talks HTTP to model servers, writes SQLite, parses YAML, opens sockets, and offers a CLI. This is not because Python is a foundation for mathematics. It is because the glue around a prover is ordinary systems work.

The trust boundary is the Lean file. Python can be buggy. If Python stores a theorem without Lean accepting the file, that is a bug you should treat as a crisis. The tests exist to make that crisis less likely. They do not make it impossible.

## Why Windows is mentioned so often

This repository was developed on Windows as well as designed to be portable. Windows PowerShell aliases `curl` to `Invoke-WebRequest`. `irm` against some GitHub raw URLs fails with a closed connection. elan’s current documented installer lives at `https://elan.lean-lang.org/elan-init.ps1`. Those are not philosophical facts. They are the minutes that stop a beginner. Chapter 10 writes them down in order.

## The original request, restated without hype

Someone asked for a system that would find new mathematical truths, using Lean, a library of all mathematics, an LLM reasoner, a huge agent prover, host-aware use of the machine, concurrent and distributed work, new formal systems, user systems, curiosity, and personalities from many fields.

What you can hold in your hands is the subset that can be defended:

- Lean-checked theorems new to **this corpus**, not certified new to the world;
- Mathlib as the library, plus optional untrusted extras;
- a host-capped swarm of **logical** agents;
- a real but small distributed check protocol;
- personalities as prompts;
- curiosity as a rotating command, not a soul;
- formal systems that stay labeled.

Chapter 29 lists what is still missing. The rest of the book teaches what is present so thoroughly that you will not confuse the two.

## Transition

You now have the idea of a proof, the idea of a formal language, and the historical mapping. The next chapter is Lean from zero as a user of aimath needs it: enough to read a file, not enough to write a compiler.
