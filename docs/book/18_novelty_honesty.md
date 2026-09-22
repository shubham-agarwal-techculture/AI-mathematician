# Chapter 18 — Novelty, literature, and what you may claim

This chapter is ethics with a function name.

## The temptation

A model writes a file. Lean accepts it. You feel the history of mathematics move. Almost always, it did not. You formalized a lemma Mathlib search missed, or a tautology, or a restatement.

The software cannot know the history of mathematics. It can know:

- whether a compact string or identifier showed up in the local Mathlib tree;
- whether this sqlite already has the row;
- whether the text names a catalogued famous problem;
- whether untrusted sources mentioned related titles.

That is all. `assess_novelty` turns those bits into a verdict and a **mandatory** explanatory sentence.

## Verdicts, at length

**known_in_mathlib.** Stop. Do not tweet discovery.

**already_in_corpus.** You are repeating yourself.

**adjacent_to_open_problem.** The matcher found enough tokens of a catalog name (a long token of length ≥ 6, or two shorter name tokens). The catalog includes Riemann hypothesis, Goldbach, Collatz, twin primes, BSD, Hodge, Navier–Stokes regularity, Yang–Mills mass gap, P versus NP, Hadwiger, Jacobian, Sendov. The list is incomplete on purpose and dangerous if treated as complete. The summary says a tactic script is not a solution.

**literature_hits_untrusted.** Wikipedia or notes or arXiv mentioned something. Useful for reading. Not a proof. Not a priority search.

**new_to_this_corpus.** The honest leftover. The summary must include that this is not a claim of a new mathematical truth.

## How matching works (so you can distrust it)

`match_open_problem` tokenizes the query at length ≥ 4. It compares to tokens of the problem name. “a note on the Riemann hypothesis” hits because `riemann` is long and present. “prime” alone should not hit twin primes. If it does, tighten the matcher and add a test.

Mathlib known-matching is similarly mechanical. It will both miss and over-fire. Humans remain the literature review.

## Sources you can turn on

**notes/** — your files.

**foreign/** — other provers’ text.

**arxiv: true** — abstracts only, `export.arxiv.org`.

**web: true** — Wikipedia `action=query&list=search`, OEIS `fmt=json`. Need network. Failures are swallowed in `Retriever.search` so a down encyclopedia does not crash explore.

None of these become theorems.

## Sentences you may use

Allowed:

> Lean accepted this proof in our Mathlib workspace. We did not find the compact statement in our Mathlib checkout or in our local corpus.

> This is a theorem relative to the axiom system Parity.

> The model proposed a proof of a statement that names the Riemann hypothesis. We treated that as adjacency to an open problem, not as a solution.

Forbidden:

> We solved an open problem.

> This is new to mathematics.

> Wikipedia confirms the proof.

> The AI is sure.

## Coursework and publication

Disclose the tool. Your institution’s rules win. A Lean file is still machine-assisted work if the tactics came from a model. Understanding the file is the part that might be yours.

## After this chapter

Chapter 19 is personalities: the costumes the proposer wears, not extra authority.
