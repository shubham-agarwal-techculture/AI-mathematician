"""Run a Lean file inside the Mathlib workspace. `sorry` and `admit` are not proofs."""

from __future__ import annotations

import re
import shutil
import subprocess
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from aimath.textutil import find_banned

_DECL = re.compile(r"^(theorem|lemma|example|def)\b", re.M)
_OUTPUT_CAP = 16000


@dataclass
class CheckResult:
    accepted: bool
    returncode: int
    stdout: str
    stderr: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CheckResult:
        return cls(
            accepted=bool(data["accepted"]),
            returncode=int(data["returncode"]),
            stdout=str(data.get("stdout") or ""),
            stderr=str(data.get("stderr") or ""),
            reason=str(data.get("reason") or ""),
        )


def render_imports(modules: list[str] | None) -> str:
    seen: list[str] = []
    for module in modules or ["Mathlib"]:
        if module and module not in seen:
            seen.append(module)
    if not seen:
        seen = ["Mathlib"]
    return "\n".join(f"import {module}" for module in seen)


def indent_tactics(tactics: str) -> str:
    lines = [line.rstrip() for line in tactics.strip().splitlines() if line.strip()]
    if not lines:
        lines = ["skip"]
    return "\n".join("  " + line.strip() for line in lines)


def render_proof(
    statement: str,
    tactics: str,
    imports: list[str] | None = None,
    extra_imports: list[str] | None = None,
) -> str:
    modules = list(imports or ["Mathlib"])
    for module in extra_imports or []:
        if module not in modules:
            modules.append(module)
    body = statement.strip()
    if _DECL.match(body):
        decl = body
    else:
        decl = f"theorem aimath_result : ({body}) := by\n{indent_tactics(tactics)}"
    return render_imports(modules) + "\n\n" + decl + "\n"


def render_typecheck(statement: str, imports: list[str] | None = None) -> str:
    """Elaborate `statement` as a Prop without proving it.

    `(statement) ∨ True` typechecks only when `statement` is a Prop. `Or.inr trivial`
    closes that goal, so success means the statement elaborated. It is not a proof
    of the statement, and the file contains neither `sorry` nor `admit`.
    """
    prop = statement.strip()
    src = (
        render_imports(imports)
        + "\n\ntheorem aimath_typecheck_dummy : ("
        + prop
        + ") ∨ True := Or.inr trivial\n"
    )
    return src


def _clip(text: str) -> str:
    if len(text) <= _OUTPUT_CAP:
        return text
    return text[:_OUTPUT_CAP] + "\n...[truncated]"


def check_source(workspace: Path, source: str, timeout: int) -> CheckResult:
    banned = find_banned(source)
    if banned:
        return CheckResult(
            accepted=False,
            returncode=1,
            stdout="",
            stderr="",
            reason=f"{banned} is not a proof",
        )
    if not re.search(r"\b(theorem|lemma|example|axiom|def)\b", source):
        return CheckResult(
            accepted=False,
            returncode=1,
            stdout="",
            stderr="",
            reason="the file has no Lean declaration",
        )
    lake = shutil.which("lake")
    if lake is None:
        return CheckResult(
            accepted=False,
            returncode=127,
            stdout="",
            stderr="",
            reason="lake was not found on PATH",
        )
    scratch = workspace / ".aimath_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    path = scratch / f"Job_{uuid.uuid4().hex}.lean"
    try:
        path.write_text(source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [lake, "env", "lean", str(path)],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            return CheckResult(
                accepted=False,
                returncode=124,
                stdout=_clip(exc.stdout or "" if isinstance(exc.stdout, str) else ""),
                stderr=_clip(exc.stderr or "" if isinstance(exc.stderr, str) else ""),
                reason=f"lean timed out after {timeout}s",
            )
        stdout = _clip(completed.stdout or "")
        stderr = _clip(completed.stderr or "")
        accepted = completed.returncode == 0
        reason = "lean accepted the file" if accepted else "lean rejected the file"
        return CheckResult(
            accepted=accepted,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            reason=reason,
        )
    finally:
        path.unlink(missing_ok=True)


def lean_check_job(workspace: str, source: str, timeout: int) -> dict:
    """Process-pool entry point. Arguments stay plain strings so they pickle."""
    return check_source(Path(workspace), source, int(timeout)).to_dict()
