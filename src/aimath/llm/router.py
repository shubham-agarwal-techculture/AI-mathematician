"""OpenAI-compatible and Anthropic chat clients."""

from __future__ import annotations

import os
from typing import Protocol

import httpx

from aimath.config import LLMConfig


class LLMError(RuntimeError):
    pass


class Completer(Protocol):
    def complete(self, system: str, user: str, temperature: float = 0.2) -> str: ...


def _openai_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def _anthropic_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/v1"):
        return base + "/messages"
    return base + "/v1/messages"


def _message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get("text") or block.get("content") or ""))
        return "".join(parts)
    return str(content or "")


class OpenAICompatible:
    def __init__(self, base_url: str, model: str, api_key: str, timeout: float = 120) -> None:
        self.url = _openai_url(base_url)
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, system: str, user: str, temperature: float = 0.2) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = httpx.post(self.url, headers=headers, json=body, timeout=self.timeout)
        except httpx.HTTPError as exc:
            raise LLMError(f"model request failed: {exc}") from exc
        if response.status_code >= 400:
            raise LLMError(f"model returned {response.status_code}: {response.text[:800]}")
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"model response had no message: {str(data)[:800]}") from exc
        return _message_text(content)


class Anthropic:
    def __init__(self, base_url: str, model: str, api_key: str, timeout: float = 120) -> None:
        if not api_key:
            raise LLMError("Anthropic requires an API key. Set the env var named in llm.api_key_env.")
        self.url = _anthropic_url(base_url)
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, system: str, user: str, temperature: float = 0.2) -> str:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        body = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        try:
            response = httpx.post(self.url, headers=headers, json=body, timeout=self.timeout)
        except httpx.HTTPError as exc:
            raise LLMError(f"model request failed: {exc}") from exc
        if response.status_code >= 400:
            raise LLMError(f"model returned {response.status_code}: {response.text[:800]}")
        data = response.json()
        try:
            blocks = data["content"]
        except (KeyError, TypeError) as exc:
            raise LLMError(f"model response had no content: {str(data)[:800]}") from exc
        return _message_text(blocks)


def build_client(cfg: LLMConfig) -> Completer:
    api_key = os.environ.get(cfg.api_key_env, "") if cfg.api_key_env else ""
    if cfg.provider == "anthropic":
        return Anthropic(cfg.base_url, cfg.model, api_key)
    if cfg.provider == "openai_compatible" and cfg.api_key_env and not api_key:
        # Cloud endpoints need a key. Local servers (Ollama) leave api_key_env empty.
        if "localhost" not in cfg.base_url and "127.0.0.1" not in cfg.base_url:
            raise LLMError(
                f"environment variable {cfg.api_key_env} is not set. "
                "Export it, or point base_url at a local server and clear api_key_env."
            )
    return OpenAICompatible(cfg.base_url, cfg.model, api_key)
