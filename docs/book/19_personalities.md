# Chapter 19 — Personalities, styles, and curiosity again

A personality is a name, a temperature, and a paragraph of bias. That is the entire object in `personalities.py`.

## The list, with what the bias is for

**curious** (0.8). Simple statements near Mathlib definitions.

**nerd** (0.7). Definitions, edge cases, exact names.

**elementary** (0.4). Nat, Int, inequalities, direct tactics.

**structural** (0.5). Homomorphisms, identities, wide classes.

**formula** (0.6). Explicit identities; calc, ring, linarith, omega, simp.

**cross-field** (0.9). One analogy, then a precise Lean proposition. High temperature: more chaos.

**euler** (0.6). Examples, then an identity, then a proof. Not Euler.

**noether** (0.4). Invariants, structure. Not Noether.

**erdos** (0.5). Elementary counting. Not Erdős.

**grothendieck** (0.5). Maps, universal properties. Not Grothendieck.

**ramanujan** (0.8). Explicit numeric identities. Not Ramanujan.

The historical names are a pedagogical risk. They make demos charming and claims sloppy. This book forbids “Ramanujan found” in any output you show a human unless you mean the human Ramanujan.

## Switching

`switch_personality` moves to the next name in **sorted** order, wrapping. Swarm uses this after a failed first prove. It is not a debate between agents. It is a second prompt.

`roster(seed, count)` is a cycle of names of length count. Unknown seed starts at index 0 (`cross-field` is first alphabetically, then `curious`, `elementary`, `erdos`, …). If you seed `curious`, agent 0 is curious.

## System prompt (shared)

Every completion is prefixed with a system paragraph that restates: Lean judges; local novelty is local; invented axioms are a formal system. Personalities cannot delete that paragraph. Models can ignore it. Lean cannot.

## Curiosity fields

`FIELDS` = algebra, combinatorics, number theory, geometry, analysis, physics, music, computation.

`field_for_step(n)` is `FIELDS[n % 8]`.

This is the implementation of “widely different fields.” It is a wheel, not a research program. To add a field, edit the tuple, add tests, and say in this chapter what you added.

## After this chapter

Chapter 20 is the host budget as arithmetic you can reproduce.
