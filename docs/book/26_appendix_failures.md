# Appendix A — Failure encyclopedia

## Install and environment

**`aimath` is not recognized.** The virtual environment is inactive, or scripts are not on PATH. Activate the venv. Use `python -m aimath`.

**`lake` is not recognized.** elan is missing or this terminal is older than the install. New terminal. Check `~/.elan/bin`. Windows: use `curl.exe` and `https://elan.lean-lang.org/elan-init.ps1`, not `irm` on GitHub raw.

**`irm`: underlying connection was closed.** Expected on some Windows PowerShell + GitHub raw combinations. Do not retry ten times. Change method.

**`curl` created a file named `--location`.** You used the PowerShell alias. Use `curl.exe`.

**init: workspace already exists.** Delete it only if you mean to, or use `--force` knowing it deletes `lean_ws`.

**init: lake failed.** Network, proxy, disk, antivirus. Read the `+ lake ...` line. Fix the environment, retry.

**status: mathlib ready: no.** `.lake/packages/mathlib` is missing. Init is not finished.

## Configuration and models

**unknown llm.provider.** Only `openai_compatible` and `anthropic`.

**environment variable X is not set.** Cloud endpoint with a named key. Export the var in this terminal, or switch to localhost and clear `api_key_env`.

**Anthropic requires an API key.** You chose anthropic with an empty key.

**model returned 401/403/404/429.** Key, model name, quota. The body is clipped to 800 characters in the exception.

**model request failed.** Connection refused: Ollama not running, wrong port, firewall.

**this command needs a configured language model.** A path used `need_llm=True` and you still somehow had no client — or you called a completer in a no-llm context.

## Proving

**rejected: empty, trivial, or uses sorry/admit.** Change the statement.

**rejected: Lean errors about unknown identifier.** Missing import or wrong name. Try a smaller statement. Put tokens Mathlib search can find.

**rejected: type mismatch.** The sentence is not a `Prop` as written.

**conjecture after prove.** Attempts exhausted. Try search, more attempts, another personality, or a smaller goal.

**known.** Not a failure.

**timeout after 180s.** Cold cache or huge import. Fetch cache. Narrow imports. Increase `timeout_seconds` only after that.

**sorry is not a proof.** The model (or you) used a hole. Good rejection.

## Swarm and money

Many sequential model calls with a small in-flight cap. Stop the process. Lower `--agents`.

## Distribution

**a token is required when the coordinator is not bound to localhost.** Set a token.

**coordinator rejected the token.** Mismatch.

**this worker only runs check.** You queued a prove item to a 0.1.x CLI worker.

**job requeued then dropped.** Worker died three times. Fix the worker machine’s Lean.

## Database

Locked sqlite if you copy the file while a command runs. Close aimath, then copy.

Corrupt yaml: tabs, bad indentation. Validate with a yaml linter.

## Unicode

PowerShell ate `∀`. Use `forall`.
