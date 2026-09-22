# Configuration reference

File: `aimath.yaml` (from `config.example.yaml`). Paths are relative to the yaml file’s directory.

## `llm`

| Key | Type | Meaning |
| --- | --- | --- |
| `provider` | string | `openai_compatible` or `anthropic` |
| `base_url` | string | API root |
| `model` | string | Model id |
| `api_key_env` | string | Env var name for secret; empty for keyless local servers |

## `host`

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `ram_reserve_ratio` | float | 0.25 | Fraction of RAM kept free |
| `lean_worker_gb` | float | 3 | Assumed Mathlib worker footprint |
| `max_llm_inflight` | int | 2 | Cap on concurrent model calls |

## `lean`

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `workspace` | path | `lean_ws` | Lake project root |
| `timeout_seconds` | int | 180 | Per-check timeout |
| `toolchain_url` | url | Mathlib master pin | Toolchain file fetched on init |

## `knowledge`

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `arxiv` | bool | false | Fetch arXiv abstracts |
| `web` | bool | false in loader / true in example | Wikipedia + OEIS |
| `db` | path | `aimath.sqlite` | Corpus database |
| `notes` | path | `notes` | Local notes directory |
| `foreign` | path | `foreign` | Other-prover excerpts |

## `distributed`

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `host` | string | `127.0.0.1` | Bind / connect host |
| `port` | int | 8765 | Port |
| `token` | string | `""` | Required off-loopback |

## Environment

| Variable | Meaning |
| --- | --- |
| `AIMATH_CONFIG` | Override path to yaml |
| value of `llm.api_key_env` | API secret |
