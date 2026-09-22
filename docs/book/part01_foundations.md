# Part I — Foundations from absolute zero

## I.1 Who this book is for

This book assumes **nothing**.

It does not assume you know Lean, Mathlib, theorem provers, large language models, Python packaging, PowerShell, or the history of Leibniz. When a technical word appears for the first time, it is defined in ordinary language, then again in the precise sense used by this project. When a command appears, the book says what you type, what you should see, what can go wrong, and what the machine is doing underneath.

If you already know formal mathematics, do not skip Part I. The later parts depend on the **trust model** stated here. Many failures of AI-for-math systems are not failures of cleverness; they are failures of saying clearly who is allowed to call something a theorem.

## I.2 The one rule that never changes

> **A language model never decides that something is a theorem in aimath. Lean does. Mathlib is the trusted library. Everything else is a hint.**

Memorize that sentence. Every feature in the system is designed either to obey it or to make it visible when something is only a hint.

Consequences of the rule:

1. Impressive-looking English from the model is not a theorem.
2. A tactic script that contains `sorry` or `admit` is not a theorem, even if Lean would otherwise elaborate the file.
3. A match on Wikipedia, arXiv, OEIS, or your notes is not a theorem.
4. A statement that is “new to this corpus” is not automatically new to mathematics.
5. A proof that uses extra axioms you loaded is a theorem **relative to those axioms**, not a theorem of ordinary mathematics by itself.

## I.3 What “mathematics on a computer” can mean

People use computers for mathematics in several different ways. Mixing them up causes confusion.

### I.3.1 Numerical calculation

Example: compute digits of π, simulate a differential equation, multiply large matrices. The computer approximates or calculates with floating-point or exact arithmetic. Correctness is about numerical error, stability, and algorithms.

aimath is **not primarily** this.

### I.3.2 Symbolic calculation

Example: expand `(x+1)^2`, compute an indefinite integral symbolically. Computer algebra systems (Mathematica, SymPy, Maple) rearrange expressions by rewrite rules. Correctness depends on the rewrite system and the domain assumptions.

aimath may use Lean tactics that feel symbolic (`ring`, `omega`, `norm_num`), but the certificate is still a Lean proof object, not a CAS transcript.

### I.3.3 Informal AI explanation

Example: a chatbot explains the quadratic formula. Useful for learning; not a machine-checked proof. The model can be confidently wrong.

aimath **uses** informal AI as a proposer. It does **not** treat the explanation as a proof.

### I.3.4 Formal proof checking

Example: Lean, Coq, Isabelle, Metamath. You write statements and proofs in a precise language. A small trusted kernel checks that each inference is allowed. If the checker accepts the file, the statement follows from the definitions and axioms in that environment.

aimath’s **only** notion of theorem is this one, via Lean 4.

## I.4 Leibniz’s dream, translated carefully

Gottfried Wilhelm Leibniz (1646–1716) imagined:

1. A **universal characteristic** — a language so precise that reasoning becomes calculation.
2. A **repository** of human knowledge encoded in that language.
3. A **calculus of reason** — a method to decide disputes by computing.

Historians debate how literally to take the dream. For this project, the mapping is practical, not mystical:

| Dream piece | Modern piece in aimath | What it does **not** claim |
| --- | --- | --- |
| Universal characteristic | Lean 4 | That Lean can express all human meaning |
| Repository | Mathlib first; optional notes/web second | That Mathlib is all of mathematics |
| Calculus of reason | LLM proposes; Lean decides | That the LLM is a reliable reasoner by itself |

Leibniz hoped machines might settle philosophy. aimath settles only this question: **does this Lean file check in this environment?**

That is already enormous. It is still smaller than “discover new mathematical truths” in the journal sense.

## I.5 What Lean is (from zero)

**Lean** is a software system with two faces:

1. A **programming language** (you can write programs in Lean).
2. An **interactive theorem prover** (you can state mathematical claims and build proofs that a kernel checks).

aimath cares about the second face.

### I.5.1 Statements

A **statement** (also: proposition, claim, goal) is something that can be true or false in a theory. Example in English: “For every natural number n, n + 0 equals n.”

In Lean-like text you might write:

```text
forall n : Nat, n + 0 = n
```

or a full declaration:

```lean
theorem add_zero (n : Nat) : n + 0 = n := by
  rfl
```

### I.5.2 Proofs

A **proof** in Lean is not a paragraph of persuasion. It is a piece of code (often tactics in a `by` block) that constructs a formal evidence object. The kernel checks that evidence.

### I.5.3 `sorry` and `admit`

Lean allows unfinished proofs marked with `sorry` (or related admission forms). That is useful while developing. It is **fatal** for aimath’s notion of theorem: aimath rejects sources that contain these as live identifiers. Comments and string literals do not count; a real unfinished proof does.

### I.5.4 Why aimath chooses Lean

- A large library (Mathlib) already exists.
- The ecosystem has `lake` (build tool) and `elan` (version manager).
- A file-in, accept/reject-out loop fits agents: write text, run checker, read errors, retry.

## I.6 What Mathlib is (from zero)

**Mathlib** is a huge collaborative library of mathematics formalized in Lean 4: definitions, theorems, and notation across many fields.

In aimath:

- Mathlib is **required**, not optional.
- Search looks in Mathlib before your local notebook.
- Proof attempts import Mathlib modules (or fall back to `import Mathlib`).
- User axiom systems **extend** Mathlib; they do not replace it.

Mathlib is not “all mathematics.” Papers and other provers contain results not yet in Mathlib. aimath can look at some of those texts as **untrusted hints**.

## I.7 What a language model is (from zero)

A **large language model (LLM)** predicts text. Given a prompt, it continues with plausible tokens. It can draft Lean tactics, invent conjectures, and imitate styles.

Properties that matter here:

1. **Fluency ≠ truth.** Plausible Lean can be nonsense.
2. **No built-in kernel.** The model does not formally check itself unless an outside tool does.
3. **Stochasticity.** Temperature and sampling change outputs.
4. **Cost and latency.** Cloud calls cost money; local calls cost electricity and time.

aimath’s design answer: the model proposes; Lean disposes.

## I.8 What aimath is as a product

aimath is a **Python package and command-line tool** that:

1. Creates a Lean project that depends on Mathlib.
2. Talks to an LLM through configurable backends.
3. Runs Lean checks in a sandbox with timeouts and sorry rejection.
4. Stores outcomes in a local SQLite database (“the corpus”).
5. Searches Mathlib and optional untrusted sources.
6. Offers modes: prove, explore, search, swarm, research, curious, systems, report, serve/worker.
7. Sizes concurrency from your machine’s CPU/RAM (and optional sensors).

It runs primarily on one machine. It can share Lean **check** jobs with workers on a network socket. It does not claim to be a planetary supercluster out of the box.

## I.9 Vocabulary you will see constantly

| Word | Plain meaning in aimath |
| --- | --- |
| theorem (status) | Lean accepted a proof; stored in this corpus |
| known | Already found in Mathlib; not a new local theorem |
| conjecture | Looks well-typed; no accepted proof yet |
| rejected | Trivial, uses sorry/admit, or failed typecheck |
| corpus | This installation’s SQLite notebook |
| personality | Prompt style that biases proposals |
| swarm | Many logical agents queued; few run at once |
| beam | Ordered list of tactic scripts to try |
| formal system | Extra axioms on top of Mathlib |
| relative theorem | Valid given those extra axioms |
| untrusted hit | A literature/note match; never a proof by itself |
| budget | How many Lean/LLM workers may run live |
| lake | Lean’s build/package tool |
| elan | Installs and selects Lean versions |

## I.10 A tiny mental simulation

You type:

```powershell
aimath prove --statement "forall n : Nat, n + 0 = n"
```

Roughly:

1. aimath loads `aimath.yaml`.
2. It checks Mathlib is present.
3. It measures CPU/RAM and picks worker caps.
4. It may notice Mathlib already has this lemma → status `known`, stop.
5. Otherwise it builds a typecheck file and runs Lean.
6. If that fails, status `rejected`.
7. If it succeeds, it asks the LLM for tactics (or later modes try a ladder).
8. Each attempt is written to a temp Lean file and checked.
9. On success, SQLite stores a theorem and the Lean source.
10. On repeated failure, SQLite stores a conjecture and the attempts.

At no point does step “model sounded confident” create a theorem.

## I.11 What “new mathematical truth” would require (and what aimath refuses to fake)

To claim a **new mathematical truth** in the strong sense, a careful human typically needs:

1. A precise statement.
2. A correct proof (or a reduction to known results).
3. A literature check showing it is not already known.
4. Often: peer review, exposition, and context.

aimath can help with (1) and (2) **inside Lean**, and with a **local** part of (3) (Mathlib + local corpus + shallow web hints). It will not pretend that local absence equals global novelty. When a statement names a famous open problem, aimath labels adjacency and refuses the fantasy that a tactic script solved it.

## I.12 How the rest of this book uses Part I

Every later part assumes:

- You accept the trust model.
- You know theorem/known/conjecture/rejected.
- You know Mathlib is primary.
- You know LLMs propose only.

If a later chapter says “run prove,” it means the pipeline in I.10, not “ask a chatbot.”
