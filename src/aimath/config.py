"""Load aimath.yaml. Paths in the file are relative to the file's directory."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_TOOLCHAIN_URL = (
    "https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain"
)


@dataclass
class LLMConfig:
    provider: str
    base_url: str
    model: str
    api_key_env: str


@dataclass
class HostConfig:
    ram_reserve_ratio: float = 0.25
    lean_worker_gb: float = 3.0
    max_llm_inflight: int = 2


@dataclass
class LeanConfig:
    workspace: Path
    timeout_seconds: int
    toolchain_url: str


@dataclass
class KnowledgeConfig:
    arxiv: bool
    web: bool
    db: Path
    notes: Path
    foreign: Path


@dataclass
class DistributedConfig:
    host: str
    port: int
    token: str


@dataclass
class AppConfig:
    llm: LLMConfig
    host: HostConfig
    lean: LeanConfig
    knowledge: KnowledgeConfig
    distributed: DistributedConfig
    root: Path
    path: Path


def _section(data: dict, name: str) -> dict:
    value = data.get(name) or {}
    if not isinstance(value, dict):
        raise ValueError(f"config section {name!r} must be a mapping")
    return value


def load_config(path: Path) -> AppConfig:
    path = path.resolve()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    root = path.parent
    llm = _section(raw, "llm")
    host = _section(raw, "host")
    lean = _section(raw, "lean")
    knowledge = _section(raw, "knowledge")
    distributed = _section(raw, "distributed")
    provider = str(llm.get("provider") or "openai_compatible")
    if provider not in {"openai_compatible", "anthropic"}:
        raise ValueError(
            f"unknown llm.provider {provider!r}; use openai_compatible or anthropic"
        )
    return AppConfig(
        llm=LLMConfig(
            provider=provider,
            base_url=str(llm.get("base_url") or "https://api.openai.com/v1"),
            model=str(llm.get("model") or "gpt-4o-mini"),
            api_key_env=str(llm.get("api_key_env") or ""),
        ),
        host=HostConfig(
            ram_reserve_ratio=float(host.get("ram_reserve_ratio", 0.25)),
            lean_worker_gb=float(host.get("lean_worker_gb", 3)),
            max_llm_inflight=int(host.get("max_llm_inflight", 2)),
        ),
        lean=LeanConfig(
            workspace=(root / str(lean.get("workspace") or "lean_ws")).resolve(),
            timeout_seconds=int(lean.get("timeout_seconds", 180)),
            toolchain_url=str(lean.get("toolchain_url") or DEFAULT_TOOLCHAIN_URL),
        ),
        knowledge=KnowledgeConfig(
            arxiv=bool(knowledge.get("arxiv", False)),
            web=bool(knowledge.get("web", False)),
            db=(root / str(knowledge.get("db") or "aimath.sqlite")).resolve(),
            notes=(root / str(knowledge.get("notes") or "notes")).resolve(),
            foreign=(root / str(knowledge.get("foreign") or "foreign")).resolve(),
        ),
        distributed=DistributedConfig(
            host=str(distributed.get("host") or "127.0.0.1"),
            port=int(distributed.get("port") or 8765),
            token=str(distributed.get("token") or ""),
        ),
        root=root,
        path=path,
    )


def find_config(explicit: str | None, cwd: Path | None = None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f"config not found: {path}")
        return path.resolve()
    env = os.environ.get("AIMATH_CONFIG")
    if env:
        path = Path(env)
        if not path.is_file():
            raise FileNotFoundError(f"AIMATH_CONFIG not found: {path}")
        return path.resolve()
    candidate = (cwd or Path.cwd()) / "aimath.yaml"
    if not candidate.is_file():
        raise FileNotFoundError(
            "aimath.yaml was not found. Run `aimath init` in this directory."
        )
    return candidate.resolve()
