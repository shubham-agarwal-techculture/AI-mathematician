# Chapter 14 — `search`, `explore`, and `swarm`

These commands look similar in a README table. They are not the same algorithm.

## `search` — a beam of tactics

```text
aimath search --statement TEXT [--personality NAME] [--beam N] [--system NAME]
```

Defaults: personality `formula`, beam `4`, system `mathlib`.

### Ladder

If the statement contains the character `=`, the equation ladder is used:

`ring`, `omega`, `norm_num`, `simp`, `linarith`, `rfl`, `aesop`, `decide`

Otherwise:

`rfl`, `simp`, `aesop`, `omega`, `decide`, `norm_num`, `ring`, `linarith`

`rank_scripts` skips tactics that already failed for this statement (from attempts whose output lines start with `tactic:`), skips banned tokens, and de-duplicates.

If the model later proposes extra scripts, the function **reserves beam slots** for them so the ladder cannot fill every slot. That is why a proposed `custom` tactic still appears in tests when `ring` already failed.

### Phase 1: no model

`search_proof` typechecks like prove (including fallback to `import Mathlib`). Then it tries the ladder with `ask_model=False`. If a script is accepted, it returns **theorem** and never calls the completer. The unit test `test_solver_accepts_without_calling_the_model` locks that behavior.

### Phase 2: model scripts

If phase 1 failed, the model is asked for JSON `{"scripts": ["simp", "ring"]}`. Failed tactics are refreshed. The beam is rebuilt. Phase 2 runs with `ask_model=True`, which writes conjecture if nothing works.

### Novelty print

The CLI prints `assess_novelty` after the search. Read it.

### What search is not

It is not Aesop’s tree search.

It is not a hammer that selects all Mathlib lemmas by Bayesian premise selection.

It is not learning a new neural tactic model. Memory is the sqlite list of failed tactic names.

It is still the most “prover-like” command in 0.1.x.

## `explore` — invent candidates, then prove them thinly

```text
aimath explore --domain TEXT [--personality NAME] [--steps N]
```

Defaults: curious, 5 steps.

### Prompt

The model sees the domain, the personality, and a catalog of retrieval hits (Mathlib, corpus, open problems, notes, foreign, maybe web). Untrusted hits are labeled. It is told to return JSON `{"conjectures": ["...", "..."]}`.

### Filters

Each candidate is dropped if:

- we already kept enough (`steps`);
- the normalized text was already seen in this run;
- it is trivial;
- it contains banned tokens;
- the corpus already has it (any status) for mathlib;
- Mathlib known-match: recorded as **known**, counted as an outcome, not proved.

Survivors are passed to `prove(..., attempts=1)`. One attempt each. That is why explore produces conjectures often. It is a net, not a siege.

### Exit code

The CLI returns 0 if any outcomes were kept, even if none proved. “No conjectures were kept” is the failure. That is different from prove. Explore’s job is to produce candidates.

## `swarm` — many logical agents, first proof wins

```text
aimath swarm --statement TEXT [--agents N] [--personality NAME]
```

Defaults: 8 agents, seed personality `curious`.

### Expansion

`expand_agents` builds N `WorkItem`s. Personalities rotate through the sorted roster starting at the seed. Agent 0 is the seed if the seed is a known name. Agent 1 is the next name alphabetically, wrapping.

A thousand agents means a thousand queue items, not a thousand Python processes.

### Execution

Items are enqueued (visible backlog).

`run_swarm` then runs them with a thread pool whose width is `max(1, scheduler.budget.llm_inflight)` from the CLI.

Each worker:

1. Calls `prove` with attempts=1 and that personality.
2. If not a theorem, calls `prove` again with `switch_personality`.
3. If a theorem appears, stores it as winner.

When width is 1, the loop breaks early after a win. When width is greater, `pool.map` may still start extra work already submitted. There is a `winner` check at the start of `run_one` to skip if someone else already won. This is best-effort, not a formal barrier. Extra model calls after a win are possible. They should be uncommon on width 1.

### What to tell your grant report

“We queued 10,000 agents” is true if you passed `--agents 10000`.

“We ran 10,000 concurrent models” is false unless your budget said so (it will not).

“We proved it with a swarm” is true only if Lean accepted a file.

## Choosing among the three

| Situation | Command |
| --- | --- |
| You have one goal and want cheap tactics first | `search` |
| You have one goal and want the model to talk, with retries | `prove` |
| You have a topic and want candidates | `explore` |
| You have one goal and want many styles in a queue | `swarm` |

Do not swarm an explore. That is a product of the sizes.

## After this chapter

Chapter 15 covers curiosity, research, systems, and reports — the commands that are not “try to prove this string.”
