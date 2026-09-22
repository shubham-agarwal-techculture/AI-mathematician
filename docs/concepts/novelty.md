# Novelty and honesty

aimath can truthfully say:

> This statement is not in Mathlib under the searches we ran, and it is not already a theorem in this corpus.

It cannot truthfully say, from that fact alone:

> This is a new mathematical discovery unknown to humanity.

## Verdicts

The novelty helper returns one of:

1. **known_in_mathlib** — stop calling it new.
2. **already_in_corpus** — already recorded here.
3. **adjacent_to_open_problem** — names a catalogued open problem; do not treat scripts as solutions.
4. **literature_hits_untrusted** — notes/web mention related text; still not a proof.
5. **new_to_this_corpus** — local novelty only.

## Open problems catalog

Bundled names include the Riemann hypothesis, Goldbach, Collatz, twin primes, BSD, Hodge, Navier–Stokes regularity, Yang–Mills mass gap, P vs NP, and others. Matching is lexical and cautious. Absence from the catalog does **not** mean a statement is easy or settled.

## Practice

When writing for humans (`aimath report`, papers, talks):

- Separate **formal status** from **historical novelty**.
- Cite Mathlib when the result is known there.
- Treat web hits as pointers for reading, not as verification.
