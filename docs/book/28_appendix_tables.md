# Appendix C — Command, config, and ladder tables

## Commands

| Command | Mathlib | LLM | Purpose |
| --- | --- | --- | --- |
| init | downloads | no | yaml + lean_ws + cache |
| resources | no | no | probe + sensors + caps |
| status | checks | no | readiness + counts |
| prove | yes | yes | typecheck + tactic attempts |
| explore | yes | yes | invent + prove(attempts=1) |
| search | yes | maybe | ladder then beam |
| swarm | yes | yes | N logical agents |
| research | yes | yes | keep def iff consequence |
| curious | yes | yes | rotate field, explore 1 |
| system load | yes | no | YAML axioms |
| system propose | yes | yes | model axioms |
| report | no | no | markdown + Lean export |
| serve | no | no | bind protocol |
| worker | yes for checks | no | pull checks |

Global: `--config PATH`. Env: `AIMATH_CONFIG`.

## prove flags

`--statement` required. `--personality` default curious. `--attempts` default 3. `--system` default mathlib.

## search flags

`--statement` required. `--personality` default formula. `--beam` default 4. `--system` default mathlib.

## swarm flags

`--statement` required. `--agents` default 8. `--personality` default curious.

## Equation ladder

ring, omega, norm_num, simp, linarith, rfl, aesop, decide

## General ladder

rfl, simp, aesop, omega, decide, norm_num, ring, linarith

## Personalities (sorted)

cross-field, curious, elementary, erdos, euler, formula, grothendieck, nerd, noether, ramanujan, structural

## Curiosity fields

algebra, combinatorics, number theory, geometry, analysis, physics, music, computation

## Work kinds

prove, conjecture, check, critique, formalize, solve, search, research

## Novelty verdicts

known_in_mathlib, already_in_corpus, adjacent_to_open_problem, literature_hits_untrusted, new_to_this_corpus

## Budget sketch

```text
cores_cap = 1 if cpu==1 else cpu-1
reserve = total_ram * ram_reserve_ratio
pressure = available < reserve
usable = max(0, available - reserve)
by_ram = 1 if pressure or usable < footprint else usable // footprint
lean_workers = max(1, min(cores_cap, by_ram))
llm_inflight = 1 if pressure else max(1, max_llm_inflight)
```

Then steer: disk < 5GB → lean=1; temp≥90 → lean=1,llm=1; lean_ms > 3*llm_ms → llm=1.
