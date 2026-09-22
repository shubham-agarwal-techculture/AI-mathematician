# Chapter 7 — Language models as proposers, never as judges

This chapter explains the third piece of the machine at the level of mechanism, not marketing.

## What a language model does

A modern large language model takes a list of messages (a system prompt, a user prompt) and predicts a continuation. The continuation is text. The text may look like Lean. Looking like Lean is not being accepted by Lean.

aimath sends roughly:

- A **system prompt** that states the trust rules: only Lean counts; local novelty is not world novelty; axioms are not ordinary theorems.
- A **personality bias** (more in Chapter 20 of the reading order; in this book’s later personality chapter).
- A **user prompt** that includes the goal, imports, and sometimes a previous Lean error.

The model returns a string. aimath then tries to extract tactics or JSON from that string.

## Extraction is suspicious on purpose

Models wrap answers in markdown fences. They write `{"tactics": "rfl"}`. They write prose and then a block. `textutil.extract_tactics` and `parse_json_blob` try to find a fenced block or a JSON object. If they fail, the raw text is treated as a tactic script.

That means garbage can become a `by` block. Lean will reject garbage. Good.

If the model writes `sorry`, the scanner rejects the file before Lean is even a hero. Also good.

## Providers

Two families are implemented.

**openai_compatible.** HTTP POST to `{base_url}/chat/completions` (the router is careful about whether you already included `/v1` or `/chat/completions`). The body is the usual `messages` array. Authorization is `Bearer` plus the API key if one is set.

This family includes OpenAI, Groq, OpenRouter, many proxies, **Ollama** at `http://127.0.0.1:11434/v1`, **LM Studio**, and **vLLM**. They are not the same product. They share a shape of HTTP.

**anthropic.** HTTP POST to a `/v1/messages` style URL with `x-api-key` and `anthropic-version: 2023-06-01`. A key is required. There is no “empty key for local Anthropic” path in 0.1.x.

If `provider` is `openai_compatible`, `api_key_env` is non-empty, the env var is unset, and the base URL is not localhost or 127.0.0.1, aimath refuses to start the client. That saves you from sending keyless requests to a cloud and reading a useless 401 after a long Lean init.

If you use Ollama, set `api_key_env` to the empty string.

## Temperature

Each personality has a default temperature. Higher temperature means more variety and more nonsense. The prove loop uses the personality’s temperature. You cannot set temperature on the CLI in 0.1.x. Change personality or change the code.

## What the model is not told

It is not given the entire Mathlib. Retrieval injects a few module names and short hits. The model will invent the rest.

It is not given a guarantee that its previous proof almost worked. It is given a truncated error string. Truncation is bounded so prompts do not explode.

It is not given permission to skip Lean. The system prompt says so. Models ignore system prompts often. Lean does not ignore holes.

## Cost and energy

Every prove attempt after typecheck is at least one model call unless you are on a path that does not need one. Swarm multiplies calls. Cloud providers charge. Local models burn electricity and GPU memory.

The host budget caps **in-flight** calls, not total calls. A swarm of 1000 logical agents with `max_llm_inflight: 2` still makes many sequential calls. It just does not make 1000 at once.

If you are teaching a lab, forbid huge swarms. If you are paying a bill, set a personal maximum before you start.

## Failure modes that look like philosophy

The model emits a correct informal proof and a wrong tactic script. Students believe the informal proof. Teach them that aimath did not accept the informal proof.

The model emits a script that works by accident on a weaker goal than you intended. Check the statement.

The model claims the problem is open and then “solves” it. The open-problem catalog may warn. You must still not believe a script.

## After this chapter

You should be unable to say “the AI proved it” without adding “Lean accepted the file.” The next chapter writes the trust model as a specification.
