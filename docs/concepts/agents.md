# Agents as the reasoner

An agent in aimath is not a free-running chatbot. It is a role with:

- A system prompt that states the trust rules.
- A personality bias and temperature.
- Tools that call Lean and the corpus.
- A work item recorded in the scheduler backlog.

## Roles in the loop

| Role | Job |
| --- | --- |
| Conjecture | Propose candidate propositions |
| Prove | Propose tactic scripts |
| Critique | Repair after Lean errors |
| Formalize | Propose axiom systems |
| Research | Propose definitions with consequences |
| Search beam | Rank tactics without or with the model |

## Logical agents vs live processes

Commands like `swarm --agents 1000` enqueue **one thousand logical agents**. At most `llm_inflight` model calls and `lean_workers` Lean processes run at once. This matches the original ambition of “many agents” without melting the host.

## Backend routing

`llm.provider` may be:

- `openai_compatible` — OpenAI, Groq, OpenRouter, Ollama, LM Studio, vLLM, …
- `anthropic` — Anthropic Messages API

The model proposes. Lean accepts or rejects. That separation is intentional.
