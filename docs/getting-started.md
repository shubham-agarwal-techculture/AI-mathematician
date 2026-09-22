# Getting started with aimath

This guide assumes you have never used Lean, Mathlib, a theorem prover, or aimath. It is slower than a typical README on purpose. If you want the full explanation of every idea, read the [Aimath Reference Book](book/README.md) from Chapter 1. If you want to be running a command today, stay here and do not skip the minutes.

By the end you will have:

1. Python 3.11+ in a virtual environment.
2. The `aimath` command.
3. `lake` on your PATH (via elan).
4. A Mathlib workspace (`lean_ws/`) with cache.
5. A language model configured in `aimath.yaml`.
6. At least one `prove` or `search` attempt on a tiny statement about natural numbers.

## 0. The rule you must not skip

A language model never decides that something is a theorem.

**Lean** decides, and only when the file contains neither `sorry` nor `admit`.

**Mathlib** is the trusted library.

Wikipedia, OEIS, arXiv abstracts, your notes, and the model’s English are hints.

A result that is new in `aimath.sqlite` is new **to this notebook**, not certified new to mathematics.

If that paragraph is confusing, read book Chapters 2, 3, and 8 before installing. The install will wait.

## 1. What you are installing (the picture)

Leibniz imagined a precise language, a library, and a calculator of reasons. In this program:

| Piece | Concrete thing |
| --- | --- |
| Language | Lean 4, invoked as `lake env lean` |
| Library | Mathlib, required, downloaded by `aimath init` |
| Reasoner | An LLM that proposes statements and tactics |

Python is glue: CLI, HTTP, SQLite, RAM probe. Python is not the examiner.

Think of a desk: a talkative intern (the model), a refereed encyclopedia (Mathlib), a pedantic examiner (Lean), a lab notebook for this room only (SQLite). You choose the question.

## 2. Words a complete beginner needs

**Terminal.** A text window where you type commands. On Windows, PowerShell is fine. The prompt looks like `PS D:\...>`.

**PATH.** The list of folders the system searches for programs. If `aimath` or `lake` is “not recognized,” PATH does not include that program **in this terminal**.

**Virtual environment (venv).** A private Python folder so this project’s libraries do not break other projects. After you activate it, the prompt shows `(.venv)`.

**Environment variable.** A named string the process can read. API keys live here, not in yaml. In PowerShell: `$env:OPENAI_API_KEY = "..."`. It lasts for that window unless you set it permanently.

**Process.** A running program. Lean checks run as **separate** processes. That is why RAM adds up.

**Proposition.** A sentence that can be true or false, such as “for all natural numbers n, n + 0 = n.”

**Natural number.** In Lean, `Nat` is 0, 1, 2, … (Lean includes 0).

**Tactic.** A command inside a Lean `by` block, such as `rfl` or `ring`, that tries to finish a proof.

**sorry.** A Lean hole. aimath will not call a file with live `sorry` a theorem.

## 3. Prerequisites checklist (do not start init until these are true)

1. **Python 3.11 or newer** (`python --version`).
2. A terminal you can reopen (PATH changes need a new window after elan).
3. Network for the first Mathlib download.
4. **Tens of gigabytes** free on a **local** disk. Avoid OneDrive/Dropbox work trees.
5. A model: Ollama/LM Studio locally, or a cloud API key.
6. Optional: [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) for faster Mathlib search.
7. Optional: git, if you clone the repository.

SSD is strongly preferred. Mathlib on a spinning disk or a USB stick will feel broken even when it is merely slow.

## 4. Step-by-step install

### 4.1 Get the source and a venv

```powershell
cd D:\work
python -m venv .venv-aimath
.\.venv-aimath\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again. You must see `(.venv...)`.

Install from the repository directory:

```powershell
cd path\to\AI_mathematician
python -m pip install -e ".[dev]"
aimath --help
```

If `aimath` is not found:

```powershell
python -m aimath --help
```

That form is the reliable one. Use it whenever PATH is confusing.

### 4.2 Install elan so `lake` exists

aimath refuses to pretend to verify without Lake.

**Windows — do this, not the old GitHub `irm` one-liner.** PowerShell’s `irm` often fails with “The underlying connection was closed.” PowerShell’s `curl` is often **not** curl; it is `Invoke-WebRequest`. Type `curl.exe`.

```powershell
curl.exe -L -o elan-init.ps1 https://elan.lean-lang.org/elan-init.ps1
powershell -ExecutionPolicy Bypass -File .\elan-init.ps1
Remove-Item .\elan-init.ps1
```

Accept defaults. **Close the terminal. Open a new one. Activate the venv again.**

```powershell
lake --version
```

If `lake` is still unknown, add `%USERPROFILE%\.elan\bin` to your user PATH, new terminal, retry.

Linux/macOS: see elan’s README (`curl https://elan.lean-lang.org/elan-init.sh -sSf | sh`), new shell.

### 4.3 Initialize Mathlib (the long download)

Pick a work directory (can be the repo, or a sibling). Then:

```powershell
aimath init
```

This copies `config.example.yaml` to `aimath.yaml` if needed, creates `lean_ws/`, pins `lean-toolchain` to **Mathlib’s current pin**, runs `lake update` and `lake exe cache get`.

Wait. Do not interrupt a healthy cache download. If you interrupt and the folder is junk:

```powershell
aimath init --force
```

`--force` **deletes** `lean_ws`. Back up `lean_ws/Aimath/` first if you already saved systems there.

If `lake` is missing, init prints install text and **does not** enter an unverified mode.

Check:

```powershell
aimath status
```

You want `mathlib ready: yes`. That means `lean_ws/lakefile.toml` exists and `lean_ws/.lake/packages/mathlib` is a directory.

### 4.4 Configure a model

Edit `aimath.yaml` with a text editor. Paths in the file are relative to the file’s directory.

**Ollama (local).** In another window: `ollama serve` and `ollama pull llama3.1` (or your model name).

```yaml
llm:
  provider: openai_compatible
  base_url: http://127.0.0.1:11434/v1
  model: llama3.1
  api_key_env: ""
```

Empty `api_key_env` is correct for keyless local servers.

**OpenAI-compatible cloud**

```yaml
llm:
  provider: openai_compatible
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
```

In **this** terminal:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

**Anthropic**

```yaml
llm:
  provider: anthropic
  base_url: https://api.anthropic.com
  model: claude-sonnet-4-5
  api_key_env: ANTHROPIC_API_KEY
```

Wrong model names produce HTTP errors. aimath will print a clipped body. Fix the name; do not re-init Mathlib.

### 4.5 Look at the budget

```powershell
aimath resources
```

You should see CPU, RAM, disk, GPU (or none), temperature (or unavailable), model latency, Lean worker count, LLM in-flight cap, memory pressure.

Defaults leave one core free (if you have more than one) and 25% of RAM reserved. Each Lean worker is assumed to need about 3 GB because `import Mathlib` is large. This is arithmetic, not a suggestion to start twelve proofs for fun. Details: book Chapter 11 and 20.

## 5. Your first mathematical commands

Use **straight quotes** in PowerShell. If Unicode `∀` breaks, write `forall`.

### 5.1 prove

```powershell
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary --attempts 3
```

Read the **first word**:

| Status | Meaning | Is it a disaster? |
| --- | --- | --- |
| theorem | Lean accepted a proof, no sorry/admit | No. Read the Lean. |
| known | Already in Mathlib as we search it | No. Not a new local theorem. |
| conjecture | Typechecks; no proof in the attempt budget | No. Try search. |
| rejected | Trivial, sorry, or not a well-formed Prop | Fix the statement. |

Exit code 0 happens for theorem or known. Conjecture exits 1. That means “not proved,” not “the program crashed.”

### 5.2 search (ladder first)

```powershell
aimath search --statement "forall n : Nat, n = n" --beam 4
```

Tries cheap tactics (`ring`, `rfl`, …) before the model. May print a novelty paragraph. `new_to_this_corpus` still does **not** mean new to the world.

### 5.3 explore (candidates)

```powershell
aimath explore --domain nat --personality curious --steps 3
```

Invented lines, filtered, each proved with **one** attempt. Many conjectures is normal.

### 5.4 report

```powershell
aimath report
```

Open `reports/report.md`. Open `reports/Report.lean` if any theorem exists. If you see `sorry` in an exported theorem, that is a bug; do not publish it.

## 6. Optional first-day extras

```powershell
aimath system load examples\parity.yaml
```

(If your work tree is not the repo, copy the yaml.) **accepted** means Lean accepted **axioms**, which are assumptions. Theorems later proved with `--system Parity` are **relative to Parity**.

```powershell
aimath curious --steps 1
```

Rotates a field (algebra, …, music, computation) and explores one step. Not a daemon.

Do **not** in the first day: `swarm --agents 10000`, the Riemann hypothesis, `init --force` because prove was slow.

## 7. If something fails (short)

1. `lake` missing → elan, **new** terminal, `curl.exe` method on Windows.
2. Mathlib not ready → finish init; `--force` only if the tree is disposable.
3. Model errors → `base_url`, model name, env var in **this** window, Ollama actually running.
4. Disk/RAM → close other apps; raise `ram_reserve_ratio`; do not import Mathlib twelve times.
5. `irm` / `curl` confusion → book Chapter 10 and [troubleshooting](operations/troubleshooting.md).

## 8. What to read next

| Want | Open |
| --- | --- |
| Every command and flag | [User manual](manual.md) |
| Why Lean is the judge | [Book ch. 2–8](book/01_preface.md) |
| Minute-by-minute install again | [Book ch. 10](book/10_extension_maintenance.md) |
| First hour script | [Book ch. 12](book/12_afterword.md) |
| Your role (student, PhD, maintainer, …) | [audiences/](audiences/) or [Book ch. 22](book/22_audiences.md) |
| PDF of the whole book | `python scripts/build_docs_pdf.py` → `docs/dist/Aimath_Reference_Book.pdf` |

## 9. Mental model (keep this)

- The LLM suggests.
- Lean grades.
- Mathlib is the textbook the grader trusts.
- `aimath.sqlite` is this machine’s notebook.
- Wall clippings (web, notes) are never the grade.
- You still have to understand the sentence you asked about.
