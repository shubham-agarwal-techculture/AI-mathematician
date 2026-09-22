# Chapter 12 — The first hour of use

You have a ready workspace and a model. This chapter is a script. Type the commands. Read the commentary even if you skip typing.

## Minute 0 — See the machine

```powershell
aimath resources
```

Read every line. If disk is low, stop and free space before Mathlib checks. If GPU is “none detected,” that is normal; you do not need a GPU for Lean. If model latency is unavailable, your `base_url` host may be down (Ollama not serving) or unreachable.

```powershell
aimath status
```

Confirm `mathlib ready: yes`. If no, do not continue to prove. Return to Chapter 10.

## Minute 5 — A statement you already believe

```powershell
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary --attempts 3
```

Possible first lines of output:

**known.** Mathlib already has this or the compact text. You did not fail. You learned the system will not invent priority. Read the detail line; it may name a module.

**theorem.** Lean accepted a script. The Lean source may be printed. Save it mentally: this is what a success looks like.

**conjecture.** Typecheck worked; three attempts did not. Look at the detail. If it is a Lean error, the model is writing bad tactics. Try `aimath search` on the same statement.

**rejected.** The statement did not elaborate, or it was trivial, or it contained `sorry`. If you typed a curly quote instead of a straight quote in PowerShell, the statement may be wrong. Retype with straight quotes.

If the process errors with a model HTTP failure, fix yaml and the env var. Lean never ran, or ran only the typecheck.

## Minute 20 — Search without trusting the first idea

```powershell
aimath search --statement "forall n : Nat, n = n" --beam 4 --personality formula
```

This tries `rfl` early on a non-equation-looking wait: the statement has `=`, so the **equation ladder** actually starts with `ring`, then `omega`, and so on. `forall n : Nat, n = n` contains `=`. The ladder may close it with `rfl` later in the beam, or `ring` may already succeed, or the dummy typecheck is the slow part.

Watch the novelty paragraph. `search` prints `assess_novelty` text. It will tell you if this is merely local.

## Minute 30 — Explore a domain

```powershell
aimath explore --domain nat --personality curious --steps 3
```

You will see `---` separated outcomes. Some may be known. Some rejected. Some conjectures. This is a successful explore. An explore that only prints brilliant English and no statuses would be a bug.

Do not raise `--steps` to 50 on a cloud key in the first hour.

## Minute 40 — A formal system that is obviously a toy

```powershell
aimath system load examples\parity.yaml
```

If you inited outside the repo, copy `examples/parity.yaml` from the repo or recreate it:

```yaml
name: Parity
notes: A toy extension. These axioms are assumptions.
axioms:
  - name: zero_even
    statement: "∃ k : Nat, 0 = 2 * k"
```

**accepted** means Lean accepted the axiom file on top of Mathlib. You have not proved anything interesting about parity. You have assumed something that is, in this case, even *true* in ordinary math (0 is even), but it is still an axiom in the file, not a derived theorem. The system’s point is the mechanism, not the depth.

Proving under `--system Parity` requires an accepted system and a non-trivial statement. `True` will be rejected as trivial. That is correct.

## Minute 50 — Write the lab notebook out

```powershell
aimath report
```

Open `reports/report.md` in an editor. Read it as if you were a skeptic. If it says theorem, look at `reports/Report.lean`. If the Lean looks like `sorry`, file a bug; that must not happen.

## Minute 55 — What not to do in the first hour

Do not run `swarm --agents 10000`.

Do not type the Riemann hypothesis.

Do not `--force` init because prove was slow.

Do not paste the model’s English into a homework without Lean and without disclosure.

## Minute 60 — Where the book goes next

The following chapters are the same commands, slower: every flag, every branch of the prove loop, every status. If the first hour felt like magic, those chapters unmagic it. If the first hour failed, those chapters plus the failure appendix are the map.
