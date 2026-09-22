# Chapter 11 — Configuration, key by key

The file is YAML. A tab in the wrong place will break it. Use spaces. If load fails, the message will say the file must be a mapping or a section must be a mapping. Fix the yaml before suspecting Lean.

Paths in the file are relative to the yaml’s directory.

Unknown `llm.provider` values are rejected. Only `openai_compatible` and `anthropic` exist in 0.1.x.

## Section `llm`

**provider.** `openai_compatible` or `anthropic`.

**base_url.** For OpenAI-compatible, typical values:

- `https://api.openai.com/v1`
- `http://127.0.0.1:11434/v1` (Ollama)
- A Groq or OpenRouter base that already ends in `/v1`

The router will append `/chat/completions` if you gave a `/v1` root. If you already gave the full chat URL, it leaves it.

For Anthropic, `https://api.anthropic.com` is enough; the router appends `/v1/messages` as needed.

**model.** A string the server understands. `llama3.1` is not `gpt-4o-mini`. Wrong names produce HTTP 404 or a model-specific error. aimath surfaces the first 800 characters of the body.

**api_key_env.** Name of an environment variable, or empty. Empty is correct for many local servers. For Anthropic, empty will fail when the client is built.

The secret is never read from yaml. If you paste a key into yaml, you will eventually commit it. Do not.

## Section `host`

**ram_reserve_ratio.** Default `0.25`. Fraction of **total** RAM that should remain “for the rest of the machine.” If **available** RAM is below that reserve, the budget sets `memory_pressure` and collapses to one Lean worker and one LLM call.

Worked example, also in the tests: 8 logical cores, 32 GB total, 24 GB available, reserve 25%, 3 GB per Lean worker.

- Reserve = 8 GB.
- Pressure? 24 > 8, no.
- Usable = 24 − 8 = 16 GB.
- By RAM: 16 // 3 = 5.
- By cores: 8 − 1 = 7.
- Lean workers = min(5, 7) = 5.
- LLM in-flight = 2 if you asked for 2.

If available is 4 GB on the same 32 GB machine, pressure is true (4 < 8), Lean workers = 1, LLM = 1.

If the machine has 1 core, cores_cap is 1, not 0. A single-core machine still gets one worker.

**lean_worker_gb.** Default `3`. If usable RAM is less than one footprint, you still get one worker (so you can try), unless other steering shrinks you later. That one worker may still swap. Free memory.

**max_llm_inflight.** Default `2`. Ignored down to 1 under pressure.

Steering after the raw budget (disk, temperature, timings) is Chapter 21 in spirit; it lives in `steer_budget`:

- Disk free under 5 GB: one Lean worker.
- Temperature ≥ 90 C if a sensor exists: one Lean and one LLM.
- Recent Lean ms > 3 × recent LLM ms: LLM cut to 1.
- Recent LLM much slower: Lean caps stay; a note is recorded. We do not add Lean workers beyond the host cap just because the model is slow.

GPU name is displayed. It does not start CUDA work. Lean 4’s ordinary checks are CPU.

## Section `lean`

**workspace.** Default `lean_ws`. This is where Lake lives.

**timeout_seconds.** Default `180`. A single `lake env lean` beyond this is a timeout (reason includes the number of seconds). Increase for huge imports on a cold cache. Do not increase instead of fetching the cache.

**toolchain_url.** Default is Mathlib’s `lean-toolchain` on GitHub master. Init downloads the first line. If you need an air-gapped pin, you can change the URL to something you host, or you can write `lean-toolchain` by hand after a template copy — but then you are off the paved road.

## Section `knowledge`

**arxiv.** Default false in the loader. Example file may show false. When true, explore/search retrieval may fetch abstracts from `export.arxiv.org`. Abstracts are untrusted. Full PDFs are not downloaded in 0.1.x.

**web.** Example file may set true. The loader defaults false if the key is missing. When true, Wikipedia search API and OEIS JSON search are queried. Network, untrusted, never proofs.

**db.** Default `aimath.sqlite`.

**notes.** Default `notes`.

**foreign.** Default `foreign`.

## Section `distributed`

**host.** Default `127.0.0.1`.

**port.** Default `8765`. `serve` may pass `--port 0` only if you change code; the CLI uses the configured port. The coordinator binds and reports the actual port if the OS assigns one — in tests we bind port 0. The production CLI uses the yaml port.

**token.** Empty allowed only on loopback (`127.0.0.1`, `localhost`, `::1`). Any other host without a token raises: a token is required.

## Finding the file

Order: `--config` argument, else `AIMATH_CONFIG`, else `./aimath.yaml` from the current working directory. There is no search up the parent chain in 0.1.x. If you run the command from the wrong folder, you will be told to init. `cd` first.

## After this chapter

You can change a knob and know which subsystem you touched. Chapter 12 is the first session of actual mathematics-shaped commands.
