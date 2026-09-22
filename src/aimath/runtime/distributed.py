"""A localhost work queue. Remote workers pull JSON lines and return JSON lines.

Binding anywhere other than loopback requires a token. A worker that disconnects
mid-job puts the job back, up to three tries.
"""

from __future__ import annotations

import json
import socket
import threading
from dataclasses import dataclass, field

from aimath.runtime.protocol import WorkItem, WorkResult

_LOOPBACK = {"127.0.0.1", "localhost", "::1"}


def require_token(host: str, token: str) -> None:
    if host not in _LOOPBACK and not token:
        raise ValueError("a token is required when the coordinator is not bound to localhost")


@dataclass
class JobQueue:
    max_tries: int = 3
    pending: list[WorkItem] = field(default_factory=list)
    inflight: dict[str, WorkItem] = field(default_factory=dict)
    tries: dict[str, int] = field(default_factory=dict)
    results: dict[str, WorkResult] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def put(self, item: WorkItem) -> None:
        with self._lock:
            self.pending.append(item)

    def take(self) -> WorkItem | None:
        with self._lock:
            if not self.pending:
                return None
            item = self.pending.pop(0)
            self.inflight[item.id] = item
            self.tries[item.id] = self.tries.get(item.id, 0) + 1
            return item

    def complete(self, result: WorkResult) -> None:
        with self._lock:
            self.inflight.pop(result.id, None)
            self.results[result.id] = result

    def abandon(self, item_id: str) -> str:
        """Return `requeued` or `dropped`."""
        with self._lock:
            item = self.inflight.pop(item_id, None)
            if item is None:
                return "dropped"
            if self.tries.get(item_id, 1) >= self.max_tries:
                self.results[item_id] = WorkResult(
                    id=item_id,
                    ok=False,
                    lean_accepted=None,
                    artifact={"reason": "worker disconnected and the retry budget is spent"},
                )
                return "dropped"
            self.pending.append(item)
            return "requeued"


class Coordinator:
    def __init__(self, host: str, port: int, token: str, queue: JobQueue | None = None) -> None:
        require_token(host, token)
        self.host = host
        self.token = token
        self.queue = queue or JobQueue()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self.port = int(self._sock.getsockname()[1])
        self._sock.listen(8)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._accept_loop, name="aimath-coordinator", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        try:
            self._sock.close()
        except OSError:
            pass

    def _accept_loop(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _addr = self._sock.accept()
            except OSError:
                return
            threading.Thread(target=self._client, args=(conn,), daemon=True).start()

    def _client(self, conn: socket.socket) -> None:
        reader = conn.makefile("r", encoding="utf-8", newline="\n")
        writer = conn.makefile("w", encoding="utf-8", newline="\n")
        current: WorkItem | None = None
        try:
            hello_raw = reader.readline()
            if not hello_raw:
                return
            hello = json.loads(hello_raw)
            if str(hello.get("token") or "") != self.token:
                writer.write(json.dumps({"op": "denied"}) + "\n")
                writer.flush()
                return
            writer.write(json.dumps({"op": "ok"}) + "\n")
            writer.flush()
            while not self._stop.is_set():
                raw = reader.readline()
                if not raw:
                    break
                msg = json.loads(raw)
                op = msg.get("op")
                if op == "pull":
                    current = self.queue.take()
                    if current is None:
                        writer.write(json.dumps({"op": "empty"}) + "\n")
                    else:
                        writer.write(json.dumps({"op": "work", "item": current.to_json()}) + "\n")
                    writer.flush()
                elif op == "result":
                    result = WorkResult.from_json(msg["result"])
                    self.queue.complete(result)
                    current = None
                elif op == "bye":
                    break
        except (json.JSONDecodeError, KeyError, OSError, ValueError):
            pass
        finally:
            if current is not None:
                self.queue.abandon(current.id)
            try:
                conn.close()
            except OSError:
                pass


def worker_once(host: str, port: int, token: str, handle) -> WorkResult | None:
    """Pull one job, handle it, and return the result. `handle` maps a work item to a result."""
    with socket.create_connection((host, port), timeout=5) as sock:
        reader = sock.makefile("r", encoding="utf-8", newline="\n")
        writer = sock.makefile("w", encoding="utf-8", newline="\n")
        writer.write(json.dumps({"op": "hello", "token": token}) + "\n")
        writer.flush()
        hello = json.loads(reader.readline())
        if hello.get("op") != "ok":
            raise PermissionError("coordinator rejected the token")
        writer.write(json.dumps({"op": "pull"}) + "\n")
        writer.flush()
        msg = json.loads(reader.readline())
        if msg.get("op") != "work":
            writer.write(json.dumps({"op": "bye"}) + "\n")
            writer.flush()
            return None
        item = WorkItem.from_json(msg["item"])
        result = handle(item)
        writer.write(json.dumps({"op": "result", "result": result.to_json()}) + "\n")
        writer.write(json.dumps({"op": "bye"}) + "\n")
        writer.flush()
        return result
