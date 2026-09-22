# Chapter 6 — Mathlib from zero, as the primary library

Mathlib is the reason aimath is heavy, slow to initialize, and worth using.

## What Mathlib is

Mathlib is a collaborative library of formalized mathematics for Lean 4. It is developed in the open. It contains definitions and proofs across algebra, topology, analysis, number theory, category theory, combinatorics, and more. It changes. New lemmas appear. Names move. Toolchain pins move.

aimath does not vendor a frozen private copy inside the Python package. It asks Lake to fetch the community library when you init.

## What Mathlib is not

It is not “all of mathematics.”

It is not a textbook. The lemmas are written for machines and for people who already know the mathematics.

It is not automatically the same as a paper’s theorem even when the English looks similar. Formalization chooses a precise statement. The paper may have meant a stronger or weaker one.

It is not copied into `aimath.sqlite`. The database stores **this system’s** attempts and results. Mathlib remains files on disk.

## Where it lives after init

```text
lean_ws/
  lakefile.toml          -- require mathlib
  lean-toolchain         -- pin matching Mathlib
  .lake/packages/mathlib -- the library itself
```

`workspace_ready` in the Python code is a simple check: `lakefile.toml` exists and `.lake/packages/mathlib` is a directory. If someone deletes the package folder, prove refuses. That is better than running without a library and pretending.

## How search uses Mathlib

The retriever:

1. Takes tokens from your query (words of length at least 3).
2. Prefers the longest token as a needle.
3. If `rg` (ripgrep) is on PATH, it lists Lean files containing that literal needle.
4. If not, it walks Lean files under `Mathlib/` (skipping nested `.lake` and `.git`).
5. It extracts a declaration name if a `theorem`/`lemma`/`def`/`abbrev`/`axiom` line matches.
6. It returns hits with a module path such as `Mathlib.Data.Nat.Basic`.

This is **name and text search**, not understanding. If you search `add_zero`, you may find `Nat.add_zero`. If you search a paraphrased English sentence, you may find nothing.

`known_in_mathlib` has two extra behaviors:

- If your whole statement is a single identifier, a hit whose title is that identifier (or ends with `.identifier`) counts as known.
- If the compact form of your statement (whitespace removed) appears inside a Mathlib file, that counts as known.

So `n + 0 = n` may not be “known” merely because a lemma’s *type* is `n + 0 = n` after pretty-printing, if the file writes it differently. `forall n : Nat, n + 0 = n` may match if that exact compact string exists. This is imperfect on purpose: we would rather miss a known lemma (and try to prove it again) than mark a new wording as known when it is not there.

When a hit is known, aimath records status **known** and does not call it a new theorem. That is honesty, not failure.

## Why imports hurt

Opening `import Mathlib` can use gigabytes of RAM and many seconds. That is why the host budget assumes about 3 GB per Lean worker by default. You can change `host.lean_worker_gb` if you measure a different footprint on your machine. If you set it too low, you will over-subscribe RAM and the machine will swap. Swapping feels like death. Prefer fewer workers.

## Cache

`lake exe cache get` downloads precompiled oleans. Without the cache, the first checks compile huge dependency cones. With a cold cache, a trivial proof can take minutes. With a warm cache, it can take seconds. Init tries to fetch the cache. If the fetch fails, you may still have sources and a miserable first build. Re-run the cache command inside `lean_ws` when you have a better network.

## Contributing back

aimath does not submit lemmas to Mathlib. If you prove something that belongs there, you do the ordinary human work: check it is not already present under another name, write a PR, follow style. This book will not walk through a Mathlib PR. The Mathlib documentation does.

## After this chapter

You should treat Mathlib as the floor you stand on, not as an optional rug. The next chapter explains the talkative intern: the language model.
