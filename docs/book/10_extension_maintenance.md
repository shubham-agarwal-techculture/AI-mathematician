# Chapter 10 — Installation, minute by minute

This chapter assumes you have never installed a proof assistant. It is long on purpose. If an expert is bored, good: a beginner can finish without a chat window.

## 10.1 Decide where the work tree will live

Pick a directory with tens of gigabytes free. Mathlib’s cache is the large object. SSD is strongly preferred. Network filesystems and synced folders (OneDrive, Dropbox) cause mysterious locking. Prefer a local disk path such as `D:\work\aimath-work` or `~/aimath-work`.

You may init inside the cloned repository. That is convenient for developers. For a clean life, clone the repo, install the package, init in a sibling folder.

## 10.2 Python

You need Python 3.11 or newer.

On Windows, from PowerShell:

```powershell
python --version
```

If that fails, install Python from python.org and tick “Add python.exe to PATH.” Open a new terminal after installing.

Create a virtual environment so aimath’s dependencies do not fight other projects:

```powershell
cd D:\work\aimath-work
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks the activate script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again. You should see `(.venv)` in the prompt.

On Unix:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 10.3 Install the aimath package

If you have the source:

```powershell
python -m pip install -e ".\path\to\AI_mathematician[dev]"
```

From inside the repo:

```powershell
python -m pip install -e ".[dev]"
```

`.[dev]` adds pytest. `.[docs]` adds reportlab for the PDF book. You can write `.[dev,docs]`.

Confirm:

```powershell
aimath --help
```

If `aimath` is not found, the venv is not active, or your PATH does not include the venv scripts directory. Use `python -m aimath --help` as a fallback. That form uses the current interpreter and is the more reliable teaching command.

## 10.4 Install elan (Lean’s version manager)

aimath needs `lake` on PATH.

### Windows, the way that works

Do not use `irm https://raw.githubusercontent.com/leanprover/elan/master/elan-init.ps1 | iex` if you have seen “The underlying connection was closed.” Windows PowerShell’s `irm` often fails that download.

Do not type `curl` unless you are sure it is `curl.exe`. In Windows PowerShell, `curl` is often an alias for `Invoke-WebRequest`, which will not save the installer the way the official instructions expect.

Type this:

```powershell
curl.exe -L -o elan-init.ps1 https://elan.lean-lang.org/elan-init.ps1
powershell -ExecutionPolicy Bypass -File .\elan-init.ps1
Remove-Item .\elan-init.ps1
```

The installer asks questions. The defaults are sensible: install to `~\.elan`, modify PATH. Accept the default toolchain if asked; aimath init will pin the project anyway.

**Close the terminal and open a new one.** PATH changes do not always apply to the window that ran the installer. Activate your venv again in the new window.

Check:

```powershell
lake --version
elan --version
```

If `lake` is still unknown, the PATH modification failed. Add `%USERPROFILE%\.elan\bin` to your user PATH by hand, new terminal, try again.

### Other platforms

Official elan README:

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
```

Then open a new shell.

## 10.5 Optional: ripgrep

Install `rg` from https://github.com/BurntSushi/ripgrep. Without it, Mathlib search walks files. With a full Mathlib tree that walk is slower. aimath still works.

## 10.6 Optional: a local model

If you do not want a cloud key, install Ollama, then:

```text
ollama serve
ollama pull llama3.1
```

Wait until the model is actually pulled. Then use the yaml snippet in the next section.

LM Studio and vLLM also work if they speak the OpenAI chat completions shape.

## 10.7 `aimath init`

In the work directory, with venv active and `lake` visible:

```powershell
aimath init
```

What should happen, in order:

1. `aimath.yaml` is written if missing (copy of the example).
2. `lean_ws/` is copied from the template.
3. The toolchain pin is downloaded from `lean.toolchain_url` (Mathlib master pin by default).
4. `lake update` runs inside `lean_ws`.
5. `lake exe cache get` runs.
6. The program checks that `.lake/packages/mathlib` exists.

This can take a long time and a lot of bandwidth. Do not interrupt the first successful cache if you can help it. If you do interrupt, the tree may be half-written. Then `aimath init --force` replaces `lean_ws`. `--force` deletes that folder. Do not `--force` if you have precious files only in `lean_ws/Aimath/` unless they are backed up.

If `lake` is missing, init prints the elan help and exits. It does **not** enter an “unverified mode.” That is a feature.

## 10.8 Configure the model

Edit `aimath.yaml` with a text editor.

Ollama:

```yaml
llm:
  provider: openai_compatible
  base_url: http://127.0.0.1:11434/v1
  model: llama3.1
  api_key_env: ""
```

OpenAI:

```yaml
llm:
  provider: openai_compatible
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
```

Then in the same terminal session:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

On Unix: `export OPENAI_API_KEY=sk-...`

The variable must be set in the terminal that runs aimath. Setting it in a different window does nothing.

Anthropic: provider `anthropic`, base `https://api.anthropic.com`, `api_key_env: ANTHROPIC_API_KEY`.

## 10.9 Confirm readiness

```powershell
aimath status
aimath resources
```

You want `mathlib ready: yes`. You want a Lean worker count of at least 1. On a large Windows machine you may see many workers; that is the budget math, not a command to use them all at once for fun.

## 10.10 Common install failures

**`aimath` not found.** Venv, PATH, or `python -m aimath`.

**`lake` not found after elan.** New terminal; check `~\.elan\bin`.

**`irm` failed.** You used the old GitHub one-liner. Use `curl.exe` and elan.lean-lang.org.

**Init failed mid-lake.** Network, proxy, disk. Fix, then `--force` if the folder is junk.

**Antivirus locks files under `.lake`.** Exclude the work tree, or wait, or retry.

**OneDrive.** Move the work tree out of a synced folder.

**Python 3.10.** Upgrade. The package requires 3.11+.

## 10.11 What you still have not done

You have not proved anything. Chapter 12 is the first hour of use. Chapter 11 explains every yaml key before you change them at random.
