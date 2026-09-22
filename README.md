# aimath

**aimath** is a local AI mathematician. A language model proposes mathematical statements and Lean tactic scripts. **Lean 4** decides whether a proof is accepted. **Mathlib** is the required library. Optional notes, Wikipedia, OEIS, arXiv abstracts, and excerpts from other provers are hints only—they never become theorems by themselves.

If you know nothing about the system, start with [`docs/getting-started.md`](docs/getting-started.md) and the documentation hub at [`docs/index.md`](docs/index.md).

**The ultimate written source** is the Aimath Reference Book: twenty-five chapters plus appendices, from “what is a proof?” through every command, file, budget formula, and honesty rule. Read [`docs/book/README.md`](docs/book/README.md) in order, or build [`docs/dist/Aimath_Reference_Book.pdf`](docs/dist/Aimath_Reference_Book.pdf) with `python scripts/build_docs_pdf.py`. This README is the front door. The book is the house.

---

## Table of contents

1. [The idea in one page](#the-idea-in-one-page)
2. [What aimath is and is not](#what-aimath-is-and-is-not)
3. [Documentation map](#documentation-map)
4. [Install (basics)](#install-basics)
5. [Initialize Mathlib](#initialize-mathlib)
6. [Configure a language model](#configure-a-language-model)
7. [Your first proof attempt](#your-first-proof-attempt)
8. [Commands (complete)](#commands-complete)
9. [Personalities](#personalities)
10. [Knowledge sources and novelty](#knowledge-sources-and-novelty)
11. [Formal systems and research definitions](#formal-systems-and-research-definitions)
12. [Host awareness and distribution](#host-awareness-and-distribution)
13. [Interpreting results](#interpreting-results)
14. [Workflows by audience](#workflows-by-audience)
15. [Configuration reference summary](#configuration-reference-summary)
16. [Architecture summary](#architecture-summary)
17. [Maintenance](#maintenance)
18. [Extending aimath](#extending-aimath)
19. [Tests and PDF book](#tests-and-pdf-book)
20. [Limits you should remember](#limits-you-should-remember)

---

## The idea in one page

Leibniz imagined a precise language, a library of knowledge, and a machine that calculates with reasons. aimath maps that idea onto software that exists today:

| Leibniz | aimath |
| --- | --- |
| Language | Lean 4 |
| Library | Mathlib (primary); optional untrusted notes and web text |
| Reasoner | LLM agents that propose; Lean that accepts or rejects |

**A theorem in aimath is a Lean-accepted file with no `sorry` and no `admit`.** Local novelty means “not already in Mathlib under our search and not already in this corpus.” It does not mean “new to mathematics.”

The queue of work can hold thousands of logical agents. Live Lean processes and model calls stay inside a non-invasive host budget (leave a CPU core and a RAM reserve; assume ~3 GB per Mathlib-importing Lean worker). Optional `serve` / `worker` share Lean checks over a JSON-lines protocol.

---

## What aimath is and is not

**Is**

- A local theorem-proving assistant with an agent loop
- A Mathlib-first explorer and searcher
- A notebook (SQLite) of attempts, theorems, and relative formal systems
- A careful exporter of human-readable reports

**Is not**

- A guarantee of historical mathematical discovery
- A solver of famous open problems
- A replacement for learning Lean or reading papers
- An unbounded swarm that ignores your laptop’s RAM

---

## Documentation map

| Doc | Purpose |
| --- | --- |
| [`docs/index.md`](docs/index.md) | Hub for all docs |
| [`docs/getting-started.md`](docs/getting-started.md) | Zero to first proof |
| [`docs/manual.md`](docs/manual.md) | Full user manual |
| [`docs/concepts/`](docs/concepts/) | Explainer essays |
| [`docs/audiences/`](docs/audiences/) | High school → PhD → maintainer → master → extender |
| [`docs/reference/`](docs/reference/) | CLI, config, architecture, protocol, glossary |
| [`docs/operations/`](docs/operations/) | Troubleshooting, security, backups, PDF build |
| [`docs/book/`](docs/book/) | Reference book chapters |
| [`docs/dist/Aimath_Reference_Book.pdf`](docs/dist/Aimath_Reference_Book.pdf) | Built PDF (after running the script) |

Audience quick links: [high school](docs/audiences/high-school.md) · [student](docs/audiences/student.md) · [undergrad](docs/audiences/undergrad.md) · [PhD](docs/audiences/phd.md) · [mathematician](docs/audiences/mathematician.md) · [maintainer](docs/audiences/maintainer.md) · [expert](docs/audiences/expert.md) · [master](docs/audiences/master.md) · [extender](docs/audiences/extender.md) · [teacher](docs/audiences/teacher.md) · [hobbyist](docs/audiences/hobbyist.md)

---

## Install (basics)

Requirements:

- Python 3.11+
- [elan](https://github.com/leanprover/elan) so `lake` is on `PATH`
- Disk and network for Mathlib’s large cache
- Optional: [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) for faster Mathlib search
- A model endpoint (local or cloud)

```powershell
python -m pip install -e ".[dev]"
```

Optional docs tooling (PDF book):

```powershell
python -m pip install -e ".[docs]"
```

### Install elan on Windows

`irm` against some GitHub raw URLs often fails on Windows PowerShell (“underlying connection was closed”). Use `curl.exe`:

```powershell
curl.exe -L -o elan-init.ps1 https://elan.lean-lang.org/elan-init.ps1
powershell -ExecutionPolicy Bypass -File .\elan-init.ps1
Remove-Item .\elan-init.ps1
```

Open a **new** terminal, then check `lake --version`.

---

## Initialize Mathlib

```powershell
aimath init
```

This writes `aimath.yaml` (from [`config.example.yaml`](config.example.yaml) if needed), creates `lean_ws/`, pins `lean-toolchain` to Mathlib’s current pin, and runs `lake update` plus `lake exe cache get`.

`prove` / `explore` / most proving commands refuse to start until `.lake/packages/mathlib` exists. Check with:

```powershell
aimath status
```

---

## Configure a language model

Edit `aimath.yaml`.

**Ollama (local)**

```yaml
llm:
  provider: openai_compatible
  base_url: http://127.0.0.1:11434/v1
  model: llama3.1
  api_key_env: ""
```

**OpenAI-compatible cloud**

```yaml
llm:
  provider: openai_compatible
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
```

**Anthropic**

```yaml
llm:
  provider: anthropic
  base_url: https://api.anthropic.com
  model: claude-sonnet-4-5
  api_key_env: ANTHROPIC_API_KEY
```

Inspect the machine budget anytime:

```powershell
aimath resources
```

---

## Your first proof attempt

```powershell
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary --attempts 3
```

Then:

```powershell
aimath report
```

Read `reports/report.md`.

---

## Commands (complete)

| Command | Role |
| --- | --- |
| `aimath init` | Create yaml + download Mathlib |
| `aimath resources` | CPU/RAM/disk/GPU/temp/latency + worker caps |
| `aimath status` | Readiness + corpus counts |
| `aimath prove` | Typecheck + prove one statement |
| `aimath explore` | Propose conjectures and try them |
| `aimath search` | Tactic beam (solver ladder, then model) |
| `aimath swarm` | Many logical agents; stop at first proof |
| `aimath research` | Keep a definition only if a consequence proves |
| `aimath curious` | Rotate fields and ask nearby lemmas |
| `aimath system load` | Install a YAML formal system on Mathlib |
| `aimath system propose` | Ask the model for a small axiom system |
| `aimath report` | Ranked markdown + Lean export |
| `aimath serve` | Share Lean check queue |
| `aimath worker` | Pull checks from a coordinator |

Examples:

```powershell
aimath explore --domain nat --personality curious --steps 5
aimath search --statement "forall n : Nat, n = n" --beam 4
aimath swarm --statement "forall n : Nat, n = n" --agents 32
aimath research --steps 2 --personality noether
aimath curious --steps 3
aimath system load examples/parity.yaml
aimath system propose --personality structural
aimath serve
aimath worker --host 127.0.0.1 --port 8765
```

Full flag lists: [`docs/reference/cli.md`](docs/reference/cli.md) and [`docs/manual.md`](docs/manual.md).

---

## Personalities

Working styles (prompt bias + temperature). They never bypass Lean:

`curious`, `nerd`, `elementary`, `structural`, `formula`, `cross-field`, `euler`, `noether`, `erdos`, `grothendieck`, `ramanujan`

Failed swarm attempts can switch to the next style. Historical names are inspirations, not biographies.

---

## Knowledge sources and novelty

Search conceptually goes:

1. Mathlib (trusted library)
2. Local corpus
3. Open-problem catalog (warning labels)
4. `notes/` and `foreign/` (untrusted)
5. arXiv if enabled (untrusted)
6. Wikipedia / OEIS if `knowledge.web` (untrusted)

Novelty verdicts include `known_in_mathlib`, `already_in_corpus`, `adjacent_to_open_problem`, `literature_hits_untrusted`, and `new_to_this_corpus` (local only).

---

## Formal systems and research definitions

**YAML systems** extend Mathlib with axioms. Theorems under `--system Name` are **relative** to those axioms.

```yaml
name: Parity
notes: Toy assumptions.
axioms:
  - name: zero_even
    statement: "∃ k : Nat, 0 = 2 * k"
```

**Research** invents a `def` and a consequence; the definition is kept only when Lean accepts the consequence (`Aimath/Research/`).

---

## Host awareness and distribution

Defaults leave one CPU core (when possible) and 25% RAM free. Lean workers are also capped by an assumed Mathlib footprint. Steering may shrink work if disk is low, temperature is high, or Lean is much slower than the model.

`serve` binds to localhost by default. Non-loopback binds require a token. Workers that disconnect mid-job requeue up to three times.

---

## Interpreting results

| Status | Meaning |
| --- | --- |
| theorem | Lean accepted a proof with no sorry/admit |
| known | Already in Mathlib (not a new local theorem) |
| conjecture | Typechecks; no accepted proof in budget |
| rejected | Trivial, banned tokens, or failed typecheck |

Relative theorems must be labeled as relative. Open-problem names are not solutions.

---

## Workflows by audience

- **High school / hobbyist:** tiny Nat goals; learn statuses; read the high-school or hobbyist guide.
- **Student / undergrad:** prove → search → simplify proofs by hand; disclose AI use.
- **PhD / mathematician:** notes + explore + weekly report triage; literature beyond heuristics.
- **Maintainer:** backups of yaml/sqlite; shared-machine budgets; upgrade Mathlib deliberately.
- **Extender / expert / master:** see audience guides and architecture reference.

---

## Configuration reference summary

Sections in `aimath.yaml`: `llm`, `host`, `lean`, `knowledge`, `distributed`.

Important knobs: `ram_reserve_ratio`, `lean_worker_gb`, `max_llm_inflight`, `timeout_seconds`, `arxiv`, `web`, `notes`, `foreign`, `distributed.token`.

Full tables: [`docs/reference/config.md`](docs/reference/config.md).

---

## Architecture summary

```text
CLI → budget/steer → scheduler (Lean processes + LLM threads)
      → agents (prove/explore/search/swarm/research/curious)
      → retriever (Mathlib → corpus → sources)
      → Lean sandbox → SQLite corpus → reports
```

Details: [`docs/reference/architecture.md`](docs/reference/architecture.md).

---

## Maintenance

- Backup: `aimath.yaml`, `aimath.sqlite`, `notes/`, `foreign/`, `reports/`, `lean_ws/Aimath/`
- Health: `aimath status`, `aimath resources`, `pytest`
- Mathlib upgrade: intentional `aimath init --force` after backup

See [`docs/operations/`](docs/operations/).

---

## Extending aimath

Preserve invariants: Lean decides theorems; Mathlib stays primary; mark untrusted sources; respect host budgets.

Recipes for personalities, CLI commands, knowledge sources, and work kinds: [`docs/audiences/extender.md`](docs/audiences/extender.md).

---

## Tests and PDF book

```powershell
pytest
python scripts/build_docs_pdf.py
```

Unit tests do not download Mathlib. A live Mathlib check runs only when `lean_ws` is initialized.

PDF output: `docs/dist/Aimath_Reference_Book.pdf` (also writes a concatenated `.md`).

---

## Limits you should remember

- Local novelty ≠ discovery priority.
- Web and notes are hints.
- Swarm agent counts are logical; live calls are capped.
- Relative axioms do not enlarge ordinary mathematics by themselves.
- The first Mathlib init is large and slow; that is normal.

**One sentence:** the model proposes; Lean decides; Mathlib anchors; you remain responsible for mathematical meaning.
