# Chapter 21 — Source architecture, module by module

This chapter is the map of `src/aimath/`. Read it before changing code.

## Entry

`python -m aimath` → `__main__.py` → `cli.main`.

`main` calls `freeze_support()` so Windows spawn works, touches `template_dir()` so a broken install fails immediately, parses argv, dispatches.

## config.py

Dataclasses: `LLMConfig`, `HostConfig`, `LeanConfig`, `KnowledgeConfig`, `DistributedConfig`, `AppConfig`.

`load_config` is strict about provider names and section types. Defaults apply per-key if a section exists but a key is missing. Missing sections become `{}`.

## textutil.py

`normalize` collapses whitespace. `compact` removes it. `content_hash` is sha256 of `system + newline + normalize(text)`.

`find_banned` is a small lexer: skip `--` lines, `/- -/` blocks, strings with backslash escapes; otherwise read identifiers. Only exact `sorry` and `admit`.

`extract_fenced`, `parse_json_blob`, `extract_tactics`, `parse_conjectures` are the model-output parsers. They are allowed to be imperfect. Lean is the backstop.

## host/

`probe.py`, `budget.py`, `sense.py` — Chapter 20.

## runtime/

`protocol.py` — WorkItem/WorkResult, kinds tuple.

`scheduler.py` — pools.

`distributed.py` — JobQueue, Coordinator, `require_token`, `worker_once`.

## llm/router.py

`OpenAICompatible`, `Anthropic`, `build_client`, `LLMError`. Timeouts default 120 seconds for HTTP, independent of `lean.timeout_seconds`.

## lean/

`project.py` — `ELAN_HELP`, `template_dir` (walks parents to find `templates/lean_project`), `lake_executable`, `workspace_ready`, `fetch_toolchain`, `init_workspace`.

`sandbox.py` — `CheckResult`, `render_imports`, `render_proof`, `render_typecheck`, `check_source`, `lean_check_job`. Output clipped at 16000 characters. Scratch files deleted in `finally`.

## knowledge/

`corpus.py` — sqlite, thread lock, schema, all queries.

`retrieve.py` — Mathlib walk, rg, hits, `Retriever.search` order.

`sources.py` — open problems, folders, Wikipedia/OEIS parsers, `assess_novelty`.

`open_problems.json` — the catalog.

## agents/

`personalities.py` — the table and roster.

`loop.py` — `Mathematician`, prove/explore/install/propose.

`search.py` — beam.

`swarm.py` — expand and run.

`research.py` — definitions.

`curiosity.py` — wheel.

`report.py` — markdown and Lean export.

## formal/system.py

YAML load, `lean_ident`, `render_system`, `write_system_file`.

## tests

Tests must not download Mathlib. `test_live_mathlib_accepts_a_trivial_proof` is skipped unless `lean_ws` is ready. New tests should follow that rule.

When you add a knowledge source, add a fixture parser test. When you add a status path, add a FakeRetriever test. When you change budget math, change `test_budget.py` first.

## Invariants to keep

1. No theorem without Lean + scanner.
2. Mathlib remains required for prove-like commands.
3. Untrusted hits stay untrusted.
4. Relative systems stay labeled.
5. Host caps remain caps.

## After this chapter

You can extend without wandering. Chapter 22 tells different humans how to use the same machine.
