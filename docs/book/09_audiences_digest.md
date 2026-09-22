# Chapter 9 — Anatomy of an aimath directory

After `aimath init`, a working directory is not “the Python package.” It is a small world. This chapter names every important path.

## Two trees you must not confuse

**The source tree** is where you cloned or unpacked the aimath project: `src/aimath/`, `docs/`, `templates/lean_project/`, `pyproject.toml`. You install that tree with pip. You read this book from `docs/`.

**The work tree** is wherever you run `aimath init`. It may be the same folder. It may be another folder. It contains `aimath.yaml`, `lean_ws/`, and later `aimath.sqlite`.

If you init inside the source tree, `.gitignore` already ignores `lean_ws/`, `aimath.yaml`, and `*.sqlite`, because those are local state, not the program.

## `aimath.yaml`

This is the configuration. Paths inside it are relative to the directory that contains the file, not relative to your current working directory if you passed `--config` from elsewhere. `load_config` resolves that on purpose.

If the file is missing, commands that need it tell you to run init. `AIMATH_CONFIG` can point at a file. `--config` can too.

`aimath init` copies `config.example.yaml` from the project if `aimath.yaml` does not exist. It does not overwrite an existing yaml unless you are thinking of `--force` (force replaces `lean_ws`, not the yaml; the CLI keeps an existing yaml even on `--force`).

## `lean_ws/`

A Lake project created from `templates/lean_project/`:

- `lakefile.toml` — package name `aimath_ws`, requires `mathlib` from `leanprover-community`, a Lean lib named `Aimath`.
- `lean-toolchain` — overwritten at init from Mathlib’s current pin URL.
- `Aimath.lean` — an empty root module so `lake build` does not elaborate the universe.
- `.lake/packages/mathlib` — after a successful update.
- `.aimath_scratch/` — temporary `Job_<uuid>.lean` files. They are deleted after each check in the happy path. If a process is killed, a stray file may remain. You may delete the scratch folder.

Under `Aimath/User/` the installer of a formal system writes `Name.lean`.

Under `Aimath/Research/` a kept research definition is written.

These Lean files are artifacts. Back them up if you care. They are how a later human reads what the machine kept.

## `aimath.sqlite`

Created on first use of the corpus (prove, status if the file exists, etc.). Tables:

**systems.** `name`, `lean_src`, `status`, timestamps. One row named `mathlib` is ensured with status `library`.

**statements.** The claim text, a content hash of `system + normalized text`, status, personality, detail, foreign key to systems.

**attempts.** Every check: kind (`prove`, `search`, …), the Lean source, whether it was accepted, the output (often including `tactic:ring` so failures can be skipped later).

**timings.** Recent `lean` and `llm` durations in milliseconds. Steering uses a short average of the last five.

The hash means that whitespace-only changes of a statement are the same statement. That is usually what you want.

## `notes/` and `foreign/`

These directories do not have to exist. If they do, retrieval walks them for `.txt`, `.md`, `.lean`, `.v`, `.thy`, `.mm`, `.ml` and returns untrusted snippets when tokens match.

`notes/` is for your papers and markdown.

`foreign/` is for excerpts from Coq (`.v`), Isabelle (`.thy`), Metamath (`.mm`), and similar. Presence of a Coq theorem does not create a Lean theorem.

## `reports/`

Created by `aimath report`.

- `report.md` — human ranking: theorems first, then conjectures, then known, then rejected. Relative systems are labeled.
- `Report.lean` — concatenation of accepted Lean sources, or a comment that none exist.

These files are overwritten when you report again.

## The Python package (source tree)

You will not need this until Part V, but names help:

| Path | Job |
| --- | --- |
| `src/aimath/cli.py` | All commands |
| `src/aimath/config.py` | YAML |
| `src/aimath/textutil.py` | Hash, sorry scan, JSON |
| `src/aimath/host/` | Probe, budget, sensors |
| `src/aimath/runtime/` | Protocol, scheduler, sockets |
| `src/aimath/llm/router.py` | HTTP to models |
| `src/aimath/lean/` | Init + sandbox |
| `src/aimath/knowledge/` | Corpus, retrieve, sources |
| `src/aimath/agents/` | Loop, search, swarm, research, curiosity, report |
| `src/aimath/formal/` | YAML systems |

## Environment variables

`AIMATH_CONFIG` — yaml path.

Whatever `llm.api_key_env` names — the secret. Do not commit it. Do not put the secret in yaml. yaml names the env var, not the key.

## Permissions and priority

On start of a probe, aimath tries to lower its own process priority. This does not lower Lean children on all operating systems in all cases, but it is the intent: do not steal the mouse. Lean children are still heavy. Close games.

## After this chapter

You can look at a folder and know whether it is a work tree. Chapter 10 walks through creating one, including the Windows minutes.
