# Chapter 8 — The trust model (specification)

This chapter is the legal document of the project. Later chapters implement it. If a feature violates this chapter, the feature is wrong.

## Roles

**Proposer.** Anything that invents text: the language model, the tactic ladder, a human typing a statement, a YAML file of axioms, a curiosity prompt.

**Checker.** Lean 4, invoked as `lake env lean` in the Mathlib workspace, plus the `sorry`/`admit` scanner.

**Recorder.** SQLite, reports, Lean files written under `Aimath/User` and `Aimath/Research`.

Only the checker can authorize the recorder to store status **theorem**.

## Status contract

| Status | Who may assign it | Meaning |
| --- | --- | --- |
| theorem | Checker success, no banned tokens | This file is a proof of this statement in this system |
| known | Retriever + Mathlib text/name match | Already in Mathlib as we search it; not a new local theorem |
| conjecture | Typecheck success, proof failure or budget exhaustion | Well-formed, unproved here |
| rejected | Triviality, banned tokens, typecheck failure | Not a current candidate |
| accepted (system) | Lean accepted the axiom file | Extra axioms may be used with `--system` |
| proposed (system) | Stored but not Lean-clean | Do not prove against it |
| library | Built-in | The Mathlib row in `systems` |

`True` and `False` as entire statements are trivial and rejected. They are not deep philosophy. They are a filter against a model that shrugs.

## Relativity

If `--system` is not `mathlib`, a theorem must be spoken as **relative to that system**. The CLI prints that phrase. Reports should too. A relative theorem is a real formal object and a false advertisement if you drop the label.

## Novelty contract

The function `assess_novelty` may say:

- `known_in_mathlib`
- `already_in_corpus`
- `adjacent_to_open_problem`
- `literature_hits_untrusted`
- `new_to_this_corpus`

The last one **must** be explained as local. The UI and this book use the sentence: not a claim of a new mathematical truth.

Open-problem adjacency is lexical. It is a seatbelt, not a classification of all open problems in the world. Absence from `open_problems.json` means nothing.

## Untrusted sources

Hits from Wikipedia, OEIS, arXiv, `notes/`, `foreign/`, and the open-problem catalog are `untrusted=True` except Mathlib and the corpus’s own formal rows.

Untrusted text may appear in prompts. It must not appear as a proof.

## Host ethics

The default budget leaves one logical CPU core unused when the machine has more than one, and a fraction of RAM (default 25%) unused. Process priority is lowered once (below normal on Windows, `nice(5)` on Unix when it works). These are defaults, not a proof that you cannot still freeze a laptop if you set `lean_worker_gb` to 0.1 and import Mathlib twelve times.

## Distribution ethics

`serve` on a non-loopback address requires a token. A token is a shared secret, not a full security architecture. Do not expose the port to the internet and call it “a cluster.”

Workers in 0.1.x execute **check** jobs. They do not become remote prove oracles unless you extend them and keep the same checker rule on every node.

## What the notebook is allowed to forget

Mathlib itself. Re-download it.

What the notebook is not allowed to forget if you care about your work: `aimath.sqlite`, your yaml, your notes, your accepted User and Research Lean files.

## Forbidden future features (unless the contract changes in public)

- A flag that stores theorem on `sorry`.
- A flag that treats Wikipedia as Mathlib.
- A flag that marks open problems solved because a model said so.
- Silent axiom insertion to make a homework true.

If you add those, you forked a different project. Change the name.

## After this chapter

Installation can begin. You know what the files are *for* before you know where they sit. The next chapter is the anatomy of disk.
