# aimath

A local mathematician in the sense Leibniz sketched: a language to reason in, a library of mathematics, and a machine that calculates with them.

- **Language.** Lean 4. A statement is stored as a theorem only when `lean` accepts it and the file contains neither `sorry` nor `admit`.
- **Library.** Mathlib is primary. `aimath init` creates a Lake project that requires `leanprover-community` / `mathlib` and downloads the build cache. Search starts in Mathlib. The SQLite file stores only this system's own conjectures and theorems.
- **Reasoner.** An LLM proposes statements and tactic scripts. Backends: any OpenAI-compatible endpoint (OpenAI, Groq, OpenRouter, Ollama, LM Studio, vLLM) and Anthropic.

The queue can hold many tasks. The number of Lean processes and in-flight model calls follows this machine: one CPU core and a share of RAM (default 25%) stay free, and each Lean worker is assumed to need about 3 GB because a Mathlib import is heavy. Process priority stays at or below normal. The work message is the same shape a future remote worker would use. This build does not start a cluster.

An axiom system you load, or one the formalist step proposes, extends Mathlib. A theorem inside it is recorded as relative to that system. It is not a theorem of ordinary mathematics.

## Install

Python 3.11 or newer, plus [elan](https://github.com/leanprover/elan) so `lake` is on `PATH`. Ripgrep (`rg`) makes Mathlib search faster; without it, search walks Lean files directly.

```powershell
pip install -e ".[dev]"
```

On Windows, install elan with `curl.exe` (Command Prompt, or Windows PowerShell). `irm` against the GitHub script often fails there with “the underlying connection was closed.”

```powershell
curl.exe -L -o elan-init.ps1 https://elan.lean-lang.org/elan-init.ps1
powershell -ExecutionPolicy Bypass -File .\elan-init.ps1
Remove-Item .\elan-init.ps1
```

Open a new terminal after that. Use `curl.exe`, not `curl`: in Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`.

## Initialize

From the directory where you want `aimath.yaml` and the Lean workspace:

```powershell
aimath init
```

This copies [`config.example.yaml`](config.example.yaml) to `aimath.yaml` if you do not already have one, writes `lean_ws/`, pins `lean-toolchain` to the file currently on Mathlib master, then runs `lake update` and `lake exe cache get`.

The cache is many gigabytes and needs a network connection. `prove` and `explore` stop until `.lake/packages/mathlib` exists. If `lake` is missing, init prints install instructions and does not pretend to verify anything.

Set the model before proving. For a local Ollama server, `aimath.yaml` can look like:

```yaml
llm:
  provider: openai_compatible
  base_url: http://127.0.0.1:11434/v1
  model: llama3.1
  api_key_env: ""
```

For Anthropic:

```yaml
llm:
  provider: anthropic
  base_url: https://api.anthropic.com
  model: claude-sonnet-4-5
  api_key_env: ANTHROPIC_API_KEY
```

OpenAI-compatible cloud APIs use `provider: openai_compatible`, a `base_url` that ends in `/v1`, and an env var named by `api_key_env`.

## Commands

```powershell
aimath resources
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary --attempts 3
aimath explore --domain nat --personality curious --steps 5
aimath system load examples/parity.yaml
aimath system propose --personality structural
aimath status
```

Personalities are prompt styles: `curious`, `elementary`, `structural`, `formula`, `cross-field`.

A user system is YAML. It is typechecked on top of Mathlib:

```yaml
name: Parity
notes: A toy extension. These axioms are assumptions.
axioms:
  - name: zero_even
    statement: "∃ k : Nat, 0 = 2 * k"
```

`aimath prove --system Parity --statement "..."` is allowed only after that system has been accepted.

## What a result means

- **theorem.** Lean accepted a proof with no `sorry` or `admit`. If the active system is not `mathlib`, the theorem is relative to that system's axioms.
- **known.** The statement matches a Mathlib declaration or appears verbatim in a Mathlib file. It is not recorded as a new theorem.
- **conjecture.** The statement typechecked and no proof was accepted within the attempt budget.
- **rejected.** The statement is trivial (`True` / `False`), uses `sorry` or `admit`, or did not typecheck.
- **Novelty** means "not already a Mathlib declaration and not already in this corpus". It does not mean the result is unknown to mathematics.
- arXiv abstracts, when `knowledge.arxiv` is true, are labeled untrusted and are never proofs.

## Tests

```powershell
pytest
```

Unit tests do not download Mathlib. A live Lean check runs only when `lean_ws` has already been initialized.
