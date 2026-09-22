"""A readable note and a Lean export of what this system has accepted."""

from __future__ import annotations

from pathlib import Path

_RANK = {"theorem": 0, "conjecture": 1, "known": 2, "rejected": 3}


def rank_records(rows: list[dict]) -> list[dict]:
    """Theorems first, then open conjectures. Shorter statements rank earlier within a status."""
    return sorted(rows, key=lambda row: (_RANK.get(str(row.get("status")), 9), len(str(row.get("text") or ""))))


def render_markdown(rows: list[dict]) -> str:
    ordered = rank_records(rows)
    lines = [
        "# Aimath results",
        "",
        "A theorem below was accepted by Lean with no sorry and no admit.",
        "New to this corpus is not a claim of a result new to mathematics.",
        "A theorem in a system other than mathlib is relative to that system's axioms.",
        "",
    ]
    if not ordered:
        lines.append("No statements are recorded yet.")
        lines.append("")
        return "\n".join(lines)
    current = None
    for row in ordered:
        status = str(row.get("status") or "unknown")
        if status != current:
            current = status
            lines.append(f"## {status}")
            lines.append("")
        system = str(row.get("system") or "mathlib")
        scope = f" (relative to {system})" if system != "mathlib" and status == "theorem" else ""
        lines.append(f"- {row.get('text')}{scope}")
        detail = str(row.get("detail") or "").strip()
        if detail:
            lines.append(f"  - {detail.splitlines()[0][:400]}")
        lines.append("")
    return "\n".join(lines)


def render_lean_export(rows: list[dict]) -> str:
    chunks = [
        "import Mathlib",
        "",
        "-- Exported from the aimath corpus. Only accepted Lean sources are included.",
        "",
    ]
    for row in rank_records(rows):
        if row.get("status") != "theorem":
            continue
        source = str(row.get("lean_src") or "").strip()
        if source:
            chunks.append(source)
            chunks.append("")
    if len(chunks) == 4:
        chunks.append("-- No accepted proof source is stored yet.")
        chunks.append("")
    return "\n".join(chunks)


def write_report(corpus, directory: Path) -> tuple[Path, Path]:
    rows = []
    for row in corpus.list_statements():
        rows.append(
            {
                "text": row["text"],
                "status": row["status"],
                "detail": row["detail"],
                "system": row["system"],
                "lean_src": corpus.accepted_lean(int(row["id"])),
            }
        )
    directory.mkdir(parents=True, exist_ok=True)
    note = directory / "report.md"
    lean = directory / "Report.lean"
    note.write_text(render_markdown(rows), encoding="utf-8")
    lean.write_text(render_lean_export(rows), encoding="utf-8")
    return note, lean
