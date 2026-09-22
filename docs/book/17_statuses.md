# Chapter 17 — Status words as a contract

These words appear in CLI output, sqlite, and reports. They are not mood.

## theorem

Lean accepted a proof file. The scanner found no live `sorry` or `admit`. The statement is stored with this status.

If the system is not `mathlib`, speak and write: **theorem relative to system S**.

A theorem can be trivial in the ordinary sense (for example `n = n`) and still be a theorem in the formal sense. The triviality filter only rejects the exact compact strings `true`, `false`, and `trivial`, not all easy lemmas.

A theorem can be uninteresting. The software does not measure interest.

A theorem can already be known to the world’s mathematicians. The software does not measure that unless Mathlib search said **known** first. If search missed, you may have a local theorem that is an old fact. That is why reports exist for humans.

## known

Mathlib search believes this is already in the library: identifier match or compact verbatim match. The prove/search loops do not try to one-up Mathlib. They record known and move on.

known is a success of retrieval. Exit code of prove is 0.

If you disagree with a known verdict, the matcher may have been too eager (verbatim compact string appeared in a comment). File a careful bug. Do not “just call it a theorem anyway” by editing sqlite.

## conjecture

The statement elaborated as a `Prop`. No accepted proof is stored. Attempts may exist and they failed.

A conjecture in this corpus is not the Collatz conjecture. It is an open row. It may be false. Lean did not say it is true. It also did not say it is false (we do not search for disproofs as a first-class command).

explore and curious produce many conjectures. That is their job.

## rejected

One of:

- empty statement;
- trivial statement;
- banned tokens in the statement or in the typecheck wrapper;
- typecheck failed (not a `Prop` in this environment, unknown identifiers, parse error);
- research/system parse failure (different command, similar idea: we will not keep garbage).

rejected is a kindness. It stops you from spending money on a sentence that is not a claim.

## System statuses

**library.** The built-in Mathlib row.

**accepted.** Extra axiom file checked. `--system Name` allowed.

**proposed.** Stored, not allowed for prove.

## Attempt rows are not statuses of statements

An attempt can be accepted=false while the statement remains conjecture. Many attempts, one statement. The statement status changes when the loop decides (set_status).

## Printing rules

`_print_outcome` prints the status word (or the relative phrase), then the detail, then the Lean source if status is theorem and source exists.

Do not add adjectives in wrappers (“amazing theorem”). The word is enough.

## After this chapter

You can read a report without translating. Chapter 18 is what you may say to other humans.
