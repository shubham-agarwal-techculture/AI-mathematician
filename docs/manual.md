# User manual

This manual covers day-to-day use of aimath after you have completed [Getting started](getting-started.md). It explains every command, every result status, configuration fields, personalities, knowledge sources, and honesty rules.

If you want the **ultimate** explanation — from what a proof is, through every branch of `prove`, to the sqlite schema and the original request’s gaps — read the numbered [Reference Book](book/README.md) in order (Chapters 1–25 plus appendices). This manual is the hypertext companion: same facts, arranged for lookup. When a sentence here is shorter than the book, the book wins.

**The rule.** The model proposes. Lean decides. Mathlib is the trusted library. Everything else is a hint. Local novelty is not world novelty. Extra axioms make **relative** theorems.

## 1. The trust model

Aimath separates three roles:

1. **Proposal.** A language model (or a hard-coded tactic ladder) invents text: statements, tactics, axioms, definitions.
2. **Verification.** Lean 4 elaborates and checks that text inside a Mathlib workspace.
3. **Recording.** SQLite stores outcomes for this installation only.

A row becomes a **theorem** only when Lean accepts the source and the source contains neither `sorry` nor `admit`. Invented axioms create a **formal system**. Theorems proved using those axioms are **relative to that system**, not theorems of ordinary mathematics.

## 2. Files the system creates

| Path | Role |
| --- | --- |
| `aimath.yaml` | Your configuration (copied from `config.example.yaml`) |
| `lean_ws/` | Lake project that requires Mathlib |
| `aimath.sqlite` | Local corpus of systems, statements, attempts |
| `notes/` | Optional local notes (untrusted hints) |
| `foreign/` | Optional Isabelle/Coq/Metamath excerpts (untrusted) |
| `reports/` | Markdown and Lean export from `aimath report` |
| `lean_ws/Aimath/User/` | Accepted user formal systems as Lean namespaces |
| `lean_ws/Aimath/Research/` | Kept research definitions |

## 3. Commands overview

| Command | Needs Mathlib? | Needs LLM? | Purpose |
| --- | --- | --- | --- |
| `init` | downloads it | no | Create workspace + Mathlib cache |
| `resources` | no | no | Show host budget and sensors |
| `status` | checks readiness | no | Config, corpus counts, resources |
| `prove` | yes | yes | Typecheck + prove one statement |
| `explore` | yes | yes | Propose and try several conjectures |
| `search` | yes | yes* | Tactic beam; ladder may succeed without LLM |
| `swarm` | yes | yes | Many logical agents, stop at first proof |
| `research` | yes | yes | Keep a definition only if a consequence proves |
| `curious` | yes | yes | Idle curiosity across rotating fields |
| `system load` | yes | no | Install a user YAML theory |
| `system propose` | yes | yes | Ask the model for a small axiom system |
| `report` | no | no | Write ranked markdown + Lean export |
| `serve` | no | no | Share a check queue on a port |
| `worker` | usually yes | no | Pull Lean checks from a coordinator |

\* `search` calls the model after the ladder fails; if the ladder succeeds, you still need a configured client when the CLI opens the mathematician, so keep a model configured.

Global option:

```text
aimath --config path\to\aimath.yaml <command> ...
```

Or set `AIMATH_CONFIG` to a yaml path.

## 4. `aimath init`

```powershell
aimath init
aimath init --force
```

Without `--force`, an existing non-empty `lean_ws` is left alone and the command errors rather than deleting your Mathlib checkout. With `--force`, the workspace is replaced.

Failure modes:

- `lake` missing → prints elan install instructions and exits.
- Network failure mid-cache → fix network, retry (`--force` if the tree is half-written).

## 5. `aimath resources`

Shows:

- Logical CPU count
- Total and available RAM
- Approximate load
- Free disk
- GPU name if `nvidia-smi` works
- Temperature if sensors exist
- Latency to the model host (TCP connect)
- Computed Lean worker count and LLM in-flight cap
- Whether memory pressure is active

The budget always leaves one core (when more than one exist) and a RAM reserve. Each Lean worker is assumed to need about `host.lean_worker_gb` (default 3). Steering may shrink workers further if disk is nearly full, temperature is high, or recent Lean timings dwarf LLM timings.

## 6. `aimath prove`

```powershell
aimath prove --statement "forall n : Nat, n = n" --personality elementary --attempts 3 --system mathlib
```

Pipeline:

1. Reject empty / trivial / `sorry` / `admit` statements.
2. If already a theorem or known in this corpus, return that.
3. If Mathlib already declares it, return `known`.
4. Retrieve module imports; typecheck via a Prop dummy that does not prove the goal.
5. Ask the model for tactics; check each attempt with Lean; record failures.
6. On success, store `theorem` with the accepted Lean source.

`--system` must be `mathlib` or an **accepted** user system name.

## 7. `aimath explore`

```powershell
aimath explore --domain nat --personality curious --steps 5
```

The model proposes JSON conjectures. Duplicates of Mathlib, trivial goals, banned tokens, and statements already in the corpus are dropped. Each survivor is sent through `prove` with a small attempt budget. Failures remain conjectures.

## 8. `aimath search`

```powershell
aimath search --statement "forall n : Nat, n + 0 = n" --beam 4 --personality formula
```

Order of attack:

1. Equation-shaped goals prefer a closed-form ladder: `ring`, `omega`, `norm_num`, …
2. General goals prefer `rfl`, `simp`, `aesop`, …
3. Failed tactics recorded in SQLite are skipped.
4. If needed, the model proposes more scripts; part of the beam is reserved for them.

## 9. `aimath swarm`

```powershell
aimath swarm --statement "forall n : Nat, n = n" --agents 32 --personality curious
```

`--agents` is the **logical** queue size. Live model concurrency stays inside the host LLM cap. Agents rotate personalities from a roster; a failed attempt may switch styles. The first accepted proof stops the swarm.

## 10. `aimath research`

```powershell
aimath research --steps 2 --personality noether
```

Asks for a Lean `def`, a goal that uses it, and tactics. The definition is written under `Aimath/Research/` **only** if Lean accepts the consequence. Otherwise the proposal is dropped.

## 11. `aimath curious`

```powershell
aimath curious --steps 3 --personality curious
```

Rotates fields (algebra, combinatorics, number theory, geometry, analysis, physics, music, computation). Open-problem adjacency generates a warning note; the step asks for a nearby lemma, not a solution of the open problem.

## 12. Formal systems

### Load YAML

```powershell
aimath system load examples/parity.yaml
```

Example shape:

```yaml
name: Parity
notes: Toy assumptions.
axioms:
  - name: zero_even
    statement: "∃ k : Nat, 0 = 2 * k"
```

The renderer always imports Mathlib and places axioms in `User.<Name>`.

### Propose with the model

```powershell
aimath system propose --personality structural
```

Status `accepted` means Lean accepted the axiom file. Status `proposed` means it is stored but not usable for `--system` proofs yet.

## 13. Reports

```powershell
aimath report
```

Writes:

- `reports/report.md` — ranked for humans (theorems, then conjectures, …)
- `reports/Report.lean` — accepted Lean sources only

## 14. Distribution

Localhost coordinator (no token required):

```powershell
aimath serve
```

Worker on the same machine:

```powershell
aimath worker --host 127.0.0.1 --port 8765
```

Binding to a non-loopback host **requires** a shared token. A worker that disconnects mid-job requeues the item up to three times, then drops it with a failure result.

Workers currently execute `check` jobs (Lean source verification). The JSON line protocol is documented in [Worker protocol](reference/protocol.md).

## 15. Personalities

Personalities change temperature and prompt bias. They never bypass Lean.

| Name | Character |
| --- | --- |
| `curious` | Adjacent simple lemmas |
| `nerd` | Definitions, edge cases, exact notation |
| `elementary` | Nat/Int inequalities, direct tactics |
| `structural` | Morphisms, identities, wide classes |
| `formula` | Explicit identities, calc/ring/omega |
| `cross-field` | One analogy made precise |
| `euler` | Examples → identity → proof |
| `noether` | Invariants and structure |
| `erdos` | Elementary counting |
| `grothendieck` | Maps and universal properties |
| `ramanujan` | Explicit numerical identities |

## 16. Knowledge sources and novelty

Search order (conceptually):

1. Mathlib declarations (trusted library)
2. Local corpus
3. Open-problem catalog (warning labels)
4. Local `notes/` and `foreign/`
5. arXiv abstracts if enabled
6. Wikipedia / OEIS if `web: true`

Novelty verdicts from `assess_novelty`:

- `known_in_mathlib`
- `already_in_corpus`
- `adjacent_to_open_problem`
- `literature_hits_untrusted`
- `new_to_this_corpus` — **not** “new to mathematics”

## 17. Interpreting honesty language

Say:

> Lean accepted this proof; it is new to this corpus.

Do not say:

> We discovered a new mathematical truth.

Say:

> Relative to system Parity, Lean accepted …

Do not say:

> Therefore ordinary number theory now includes …

## 18. Suggested workflows

**Student homework formalization**

1. Write the goal carefully in Lean-like English or Lean syntax.
2. `aimath prove` with `elementary` or `formula`.
3. If stuck, `aimath search`.
4. Export with `aimath report` and study the Lean file.

**Research exploration**

1. Put notes in `notes/`.
2. Enable `web` / `arxiv` as desired.
3. `aimath explore` or `aimath curious`.
4. `aimath research` for definitions that earn their keep.
5. Review `reports/report.md` weekly.

**Operator**

1. `aimath resources` after hardware changes.
2. Backup `aimath.sqlite` and `aimath.yaml`.
3. Re-run `aimath init` only when upgrading Mathlib deliberately.

## 19. Where to go next

- Concepts: [concepts/index.md](concepts/index.md)
- Audience guides: [audiences/](audiences/)
- Reference: [reference/cli.md](reference/cli.md)
- Book PDF: [operations/building-the-book.md](operations/building-the-book.md)

## 20. prove, search, explore, swarm — do not treat them as synonyms

| Need | Command | What actually happens |
| --- | --- | --- |
| One statement, model retries | `prove` | Typecheck dummy `(P) ∨ True`; then up to `--attempts` tactic files |
| One statement, cheap tactics first | `search` | Equation ladder if `=` appears; skip failed `tactic:` rows; model only if ladder fails |
| A topic, several candidates | `explore` | JSON conjectures; drop trivial/sorry/duplicates/Mathlib-known; `prove` with **1** attempt each |
| Many styles on one statement | `swarm` | `--agents` **logical** items; live calls = `llm_inflight`; first theorem wins; may switch personality |

`serve` does **not** drain the prove backlog in 0.1.x. It speaks the JSON-line protocol. Workers only run `kind=check`. See book Chapter 16.

`curious` is explore with a rotating field list (algebra … music, computation). It is not a background daemon.

`research` keeps a `def` only when Lean accepts a consequence. Failed definitions are not left on disk (see tests).

## 21. Typecheck dummy (read this before you misread a file)

```lean
theorem aimath_typecheck_dummy : (YOUR_STATEMENT) ∨ True := Or.inr trivial
```

Success means YOUR_STATEMENT elaborated as a `Prop`. It is **not** a proof of YOUR_STATEMENT. Reports must not export this dummy as a theorem of the goal.

## 22. Configuration keys (lookup)

| Key | Default | Meaning |
| --- | --- | --- |
| `llm.provider` | openai_compatible | or `anthropic` |
| `llm.base_url` | api.openai.com/v1 | router appends chat/messages as needed |
| `llm.model` | gpt-4o-mini | must exist on that server |
| `llm.api_key_env` | OPENAI_API_KEY | empty string for local keyless servers |
| `host.ram_reserve_ratio` | 0.25 | fraction of **total** RAM reserved |
| `host.lean_worker_gb` | 3 | assumed footprint of one Mathlib import |
| `host.max_llm_inflight` | 2 | concurrent model calls, not total calls |
| `lean.workspace` | lean_ws | Lake project |
| `lean.timeout_seconds` | 180 | one `lake env lean` |
| `lean.toolchain_url` | Mathlib master pin | fetched at init |
| `knowledge.arxiv` | false | untrusted abstracts |
| `knowledge.web` | false if omitted | Wikipedia + OEIS, untrusted |
| `knowledge.db` | aimath.sqlite | corpus |
| `knowledge.notes` / `foreign` | notes / foreign | untrusted folders |
| `distributed.host/port/token` | 127.0.0.1 / 8765 / "" | token required off-loopback |

Budget arithmetic is locked in `tests/test_budget.py`. Worked example: 8 cores, 32 GB total, 24 GB available, 25% reserve, 3 GB/worker → 5 Lean workers. Pressure (available < reserve) → 1 and 1.

## 23. Files and tables

Work tree: `aimath.yaml`, `lean_ws/` (Mathlib under `.lake/packages/mathlib`, scratch under `.aimath_scratch/`, `Aimath/User`, `Aimath/Research`), `aimath.sqlite` (systems, statements, attempts, timings), `notes/`, `foreign/`, `reports/`.

Statement identity: sha256 of `system + "\n" + whitespace-normalized text`.

## 24. Honesty sentences you may actually use

Allowed: “Lean accepted this file in our Mathlib workspace. We did not find it in our checkout or our sqlite.”

Allowed: “Theorem relative to system Parity.”

Forbidden: “We solved an open problem.” “This is new to mathematics.” “Wikipedia confirms the proof.”

Open-problem catalog is lexical and incomplete (Riemann, Goldbach, Collatz, twins, BSD, Hodge, Navier–Stokes, Yang–Mills, P vs NP, Hadwiger, Jacobian, Sendov). Absence from the list means nothing.

## 25. Book chapter index (for when this manual is not enough)

1 How to read the book · 2 What a proof is · 3 Formal language · 4 Leibniz mapping · 5 Lean as aimath uses it · 6 Mathlib · 7 LLMs as proposers · 8 Trust specification · 9 Disk anatomy · 10 Install minutes · 11 Config keys · 12 First hour · 13 prove internals · 14 search/explore/swarm · 15 curious/research/system/report · 16 serve/worker · 17 Status contract · 18 Novelty · 19 Personalities · 20 Host budget · 21 Source map · 22 Audiences · 23 Maintenance/extension · 24 Limits · 25 Afterword · A Failures · B Glossary · C Tables
