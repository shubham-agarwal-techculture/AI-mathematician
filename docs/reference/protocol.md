# Worker protocol

Transport: TCP socket, UTF-8, **one JSON object per line**.

## Handshake

Client → server:

```json
{"op":"hello","token":""}
```

Server → client:

```json
{"op":"ok"}
```

or `{"op":"denied"}`.

## Pull work

Client:

```json
{"op":"pull"}
```

Server:

```json
{"op":"empty"}
```

or

```json
{"op":"work","item":"<stringified WorkItem JSON>"}
```

Note: `item` is a JSON **string** containing the serialized `WorkItem`.

## Return result

```json
{"op":"result","result":"<stringified WorkResult JSON>"}
```

## Bye

```json
{"op":"bye"}
```

## WorkItem fields

| Field | Meaning |
| --- | --- |
| `id` | Job id |
| `kind` | `prove`, `conjecture`, `check`, `critique`, `formalize`, `solve`, `search`, `research` |
| `payload` | Kind-specific object |
| `budget_ms` | Soft time budget |

## WorkResult fields

| Field | Meaning |
| --- | --- |
| `id` | Same job id |
| `ok` | Worker-level success |
| `lean_accepted` | Lean acceptance if applicable |
| `artifact` | Free-form details / CheckResult dict |

## Failure handling

If a client disconnects while a job is inflight, the coordinator requeues until `max_tries` (default 3), then stores a failed result.
