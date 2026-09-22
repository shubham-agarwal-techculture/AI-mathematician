"""SQLite record of this system's systems, statements, and proof attempts.

Mathlib itself is not copied here. A row is a theorem only after Lean accepts it.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from aimath.textutil import content_hash, normalize


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Corpus:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS systems (
                  id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE NOT NULL,
                  lean_src TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS statements (
                  id INTEGER PRIMARY KEY,
                  system_id INTEGER,
                  content_hash TEXT NOT NULL,
                  text TEXT NOT NULL,
                  status TEXT NOT NULL,
                  personality TEXT,
                  detail TEXT,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(system_id) REFERENCES systems(id)
                );
                CREATE TABLE IF NOT EXISTS attempts (
                  id INTEGER PRIMARY KEY,
                  statement_id INTEGER,
                  kind TEXT NOT NULL,
                  lean_src TEXT NOT NULL,
                  accepted INTEGER NOT NULL,
                  output TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(statement_id) REFERENCES statements(id)
                );
                CREATE INDEX IF NOT EXISTS idx_statements_hash ON statements(content_hash);
                CREATE TABLE IF NOT EXISTS timings (
                  id INTEGER PRIMARY KEY,
                  kind TEXT NOT NULL,
                  ms REAL NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def upsert_system(self, name: str, lean_src: str, status: str) -> int:
        with self._lock:
            row = self._conn.execute("SELECT id FROM systems WHERE name = ?", (name,)).fetchone()
            if row:
                self._conn.execute(
                    "UPDATE systems SET lean_src = ?, status = ? WHERE id = ?",
                    (lean_src, status, row["id"]),
                )
                self._conn.commit()
                return int(row["id"])
            cur = self._conn.execute(
                "INSERT INTO systems (name, lean_src, status, created_at) VALUES (?, ?, ?, ?)",
                (name, lean_src, status, _now()),
            )
            self._conn.commit()
            return int(cur.lastrowid)

    def ensure_library(self) -> int:
        return self.upsert_system("mathlib", "import Mathlib\n", "library")

    def system_id(self, name: str) -> int | None:
        with self._lock:
            row = self._conn.execute("SELECT id FROM systems WHERE name = ?", (name,)).fetchone()
        return None if row is None else int(row["id"])

    def system_status(self, name: str) -> str | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT status FROM systems WHERE name = ?", (name,)
            ).fetchone()
        return None if row is None else str(row["status"])

    def find_statement(self, system: str, text: str) -> sqlite3.Row | None:
        digest = content_hash(system, text)
        with self._lock:
            return self._conn.execute(
                """
                SELECT statements.* FROM statements
                JOIN systems ON systems.id = statements.system_id
                WHERE systems.name = ? AND statements.content_hash = ?
                ORDER BY statements.id DESC LIMIT 1
                """,
                (system, digest),
            ).fetchone()

    def add_statement(
        self,
        system: str,
        text: str,
        status: str,
        personality: str | None,
        detail: str,
    ) -> int:
        system_row = self.system_id(system)
        if system_row is None:
            system_row = self.ensure_library() if system == "mathlib" else self.upsert_system(
                system, "", "proposed"
            )
        digest = content_hash(system, text)
        with self._lock:
            existing = self._conn.execute(
                "SELECT id FROM statements WHERE system_id = ? AND content_hash = ?",
                (system_row, digest),
            ).fetchone()
            if existing:
                self._conn.execute(
                    "UPDATE statements SET status = ?, personality = ?, detail = ? WHERE id = ?",
                    (status, personality, detail, existing["id"]),
                )
                self._conn.commit()
                return int(existing["id"])
            cur = self._conn.execute(
                """
                INSERT INTO statements
                  (system_id, content_hash, text, status, personality, detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (system_row, digest, text, status, personality, detail, _now()),
            )
            self._conn.commit()
            return int(cur.lastrowid)

    def set_status(self, statement_id: int, status: str, detail: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE statements SET status = ?, detail = ? WHERE id = ?",
                (status, detail, statement_id),
            )
            self._conn.commit()

    def add_attempt(
        self,
        statement_id: int,
        kind: str,
        lean_src: str,
        accepted: bool,
        output: str,
    ) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO attempts
                  (statement_id, kind, lean_src, accepted, output, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (statement_id, kind, lean_src, 1 if accepted else 0, output, _now()),
            )
            self._conn.commit()

    def search(self, query: str, limit: int = 5) -> list[sqlite3.Row]:
        tokens = [tok for tok in normalize(query).split() if len(tok) >= 3][:4]
        if not tokens:
            return []
        clause = " AND ".join("text LIKE ?" for _ in tokens)
        params: list = [f"%{tok}%" for tok in tokens]
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(
                f"SELECT text, status FROM statements WHERE {clause} LIMIT ?",
                params,
            ).fetchall()
        return list(rows)

    def counts(self) -> dict[str, int]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT status, COUNT(*) AS n FROM statements GROUP BY status"
            ).fetchall()
        return {str(row["status"]): int(row["n"]) for row in rows}

    def list_systems(self) -> list[sqlite3.Row]:
        with self._lock:
            return list(self._conn.execute("SELECT name, status FROM systems ORDER BY name").fetchall())

    def list_statements(self) -> list[sqlite3.Row]:
        with self._lock:
            return list(
                self._conn.execute(
                    """
                    SELECT statements.id, statements.text, statements.status,
                           statements.detail, statements.personality, systems.name AS system
                    FROM statements
                    JOIN systems ON systems.id = statements.system_id
                    ORDER BY statements.id
                    """
                ).fetchall()
            )

    def accepted_lean(self, statement_id: int) -> str | None:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT lean_src FROM attempts
                WHERE statement_id = ? AND accepted = 1
                ORDER BY id DESC LIMIT 1
                """,
                (statement_id,),
            ).fetchone()
        return None if row is None else str(row["lean_src"])

    def failed_tactics(self, system: str, text: str) -> list[str]:
        row = self.find_statement(system, text)
        if row is None:
            return []
        with self._lock:
            attempts = self._conn.execute(
                "SELECT output FROM attempts WHERE statement_id = ? AND accepted = 0",
                (row["id"],),
            ).fetchall()
        found: list[str] = []
        for attempt in attempts:
            for line in str(attempt["output"]).splitlines():
                if line.startswith("tactic:"):
                    tactic = line.split(":", 1)[1].strip()
                    if tactic and tactic not in found:
                        found.append(tactic)
        return found

    def record_timing(self, kind: str, ms: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO timings (kind, ms, created_at) VALUES (?, ?, ?)",
                (kind, float(ms), _now()),
            )
            self._conn.commit()

    def recent_timing(self, kind: str) -> float | None:
        with self._lock:
            rows = self._conn.execute(
                "SELECT ms FROM timings WHERE kind = ? ORDER BY id DESC LIMIT 5",
                (kind,),
            ).fetchall()
        if not rows:
            return None
        return sum(float(row["ms"]) for row in rows) / len(rows)
