# Chapter 16 — `serve`, `worker`, and the JSON-line protocol

Distribution in 0.1.x is real and small. It shares **Lean check jobs**, not a magical remote mathematician.

## Why this exists

The original request asked for concurrent, parallel, and distributed systems. The first plan deferred a cluster. The later work added a coordinator and a worker that speak the same `WorkItem` / `WorkResult` objects the local scheduler already used.

You can run the coordinator on one machine and a worker on another if you accept the security model (a shared token, no TLS in 0.1.x). The default is localhost.

## `aimath serve`

```text
aimath serve [--host HOST] [--port PORT] [--token TOKEN]
```

Unspecified flags come from yaml `distributed`.

If host is not loopback and token is empty, the process exits with a message. It does not bind first and warn later.

The coordinator:

1. Binds a TCP socket, `SO_REUSEADDR`.
2. Listens.
3. Accepts in a daemon thread.
4. Each client is another thread.

It then sleeps until Ctrl+C. There is no job-injection CLI in 0.1.x: the in-memory `JobQueue` starts empty unless you write a program that calls `Coordinator` and `queue.put`. The tests do that. The production CLI as shipped is the **socket shape** and a process you can keep up while you develop a producer.

That limitation must be stated: `aimath serve` alone does not drain your sqlite prove queue. It is the protocol endpoint. A later version should attach the scheduler backlog to this queue. Until then, treat serve/worker as the supported way to **implement** remote checks, and use the tests as the usage sample.

If you need a mental model: the book still documents the protocol completely so an extender can hook `queue.put(WorkItem(kind="check", ...))` from their own script today.

## Protocol, byte by byte

UTF-8, one JSON object per line, newline at the end of each object.

**Hello.** Client sends `{"op":"hello","token":"..."}`. Server replies `{"op":"ok"}` or `{"op":"denied"}`.

**Pull.** Client sends `{"op":"pull"}`. Server sends `{"op":"empty"}` or `{"op":"work","item": "<string>"}` where `<string>` is `WorkItem.to_json()` **embedded as a JSON string**, not as a nested object. The worker does `WorkItem.from_json(msg["item"])`.

**Result.** Client sends `{"op":"result","result": "<WorkResult json string>"}`.

**Bye.** `{"op":"bye"}`.

If the client dies while a job is inflight, `abandon` requeues until `max_tries` (3), then stores a failed `WorkResult` explaining the retry budget.

## `WorkItem`

Fields: `id` (string), `kind` (one of `prove`, `conjecture`, `check`, `critique`, `formalize`, `solve`, `search`, `research`), `payload` (object), `budget_ms` (int).

Unknown kinds raise on construction. That is a compatibility fence.

## `WorkResult`

Fields: `id`, `ok`, `lean_accepted` (bool or null), `artifact` (object). For checks, artifact is often the `CheckResult` dict: accepted, returncode, stdout, stderr, reason.

## `aimath worker`

```text
aimath worker [--host HOST] [--port PORT] [--token TOKEN]
```

Defaults: 127.0.0.1, 8765, empty token.

The CLI worker loops: `worker_once` with `_remote_check`. `_remote_check` only handles `kind == "check"`. Other kinds return a failed result explaining the mismatch.

The payload it expects: `source` (Lean text), `workspace` (path string), `timeout` (seconds, default 180). It calls `lean_check_job` on that machine. **The worker machine must have the workspace and Mathlib.** A worker without `lean_ws` cannot help.

On `empty`, it sleeps one second and pulls again. Ctrl+C exits.

## Security, said as a grown-up

- Loopback without a token is for a single-user machine.
- A token on a LAN is a shared password sent in JSON without TLS. Anyone who can read the network can read the token and the Lean sources.
- Binding `0.0.0.0` on a public IP is a bad idea.
- The worker runs Lean on whatever source the coordinator sends. That is arbitrary-code-adjacent in the sense that Lean elaborators and tactics are powerful. Only send jobs you trust. Only accept coordinators you trust.

## After this chapter

You know what “distributed” means here: a socket, a queue, a check. Chapter 17 memorizes statuses. Chapter 18 is novelty language.
