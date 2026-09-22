"""JSON work messages for the local pool and for a future remote worker.

A remote worker would read one JSON object per line (a work item) and write one
JSON object per line (a work result). This package runs only the local worker.
It does not open a network listener.

Example item::

    {"id":"1","kind":"check","payload":{"source":"import Mathlib"},"budget_ms":180000}

Example result::

    {"id":"1","ok":true,"lean_accepted":false,"artifact":{"reason":"sorry is not a proof"}}
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

WORK_KINDS = ("prove", "conjecture", "check", "critique", "formalize")


@dataclass
class WorkItem:
    id: str
    kind: str
    payload: dict[str, Any]
    budget_ms: int

    def __post_init__(self) -> None:
        if self.kind not in WORK_KINDS:
            raise ValueError(f"unknown work kind {self.kind!r}; expected one of {WORK_KINDS}")

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> WorkItem:
        data = json.loads(raw)
        return cls(
            id=str(data["id"]),
            kind=str(data["kind"]),
            payload=dict(data.get("payload") or {}),
            budget_ms=int(data.get("budget_ms") or 0),
        )


@dataclass
class WorkResult:
    id: str
    ok: bool
    lean_accepted: bool | None
    artifact: dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> WorkResult:
        data = json.loads(raw)
        accepted = data.get("lean_accepted")
        return cls(
            id=str(data["id"]),
            ok=bool(data["ok"]),
            lean_accepted=None if accepted is None else bool(accepted),
            artifact=dict(data.get("artifact") or {}),
        )
