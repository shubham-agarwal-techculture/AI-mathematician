# Chapter 20 — Host awareness, budgets, and sensors

“Non-invasive” is a promise with a formula. Here is the formula.

## Probe

`probe()` uses psutil:

- logical CPU count (at least 1);
- total RAM;
- available RAM;
- load: `getloadavg()[0]` if it exists, else `cpu_percent * cores` as a crude stand-in (Windows has no Unix load average).

It also calls `lower_priority()` once per process. Windows: `BELOW_NORMAL_PRIORITY_CLASS`. Unix: `os.nice(5)`. Failures return `"unchanged"` and do not crash.

## Raw budget

See Chapter 11 for the worked 8-core 32 GB example. Tests in `tests/test_budget.py` lock those numbers. If you change the formula, change the tests and this chapter together.

Remember: `max(1, ...)` means we never compute zero workers. A machine that should not run Lean will still try one worker and then swap. The operator’s job is to not start prove on a starving machine.

## Steering

`sense_host` adds:

- GPU name from `nvidia-smi --query-gpu=name --format=csv,noheader` if the binary exists and returns 0;
- disk free on the work root;
- hottest temperature from `psutil.sensors_temperatures` if present (often missing on Windows);
- TCP connect latency to the model host (1.5 s timeout).

`steer_budget` then may shrink. It never raises workers above the raw budget. It does not start GPU Lean. The GPU line is information for humans who run local models on the same card: if the card is already full of Ollama, lower `max_llm_inflight` yourself.

## Timings

Each Lean check and each LLM call records milliseconds in sqlite. `recent_timing` averages the last five. Steering uses that pair if both exist. A first run has no pair; steering skips the timing clause.

If Lean is more than three times slower than the model, incoming proposals are limited (llm=1) so you do not pile scripts on a saturated checker. If the model is the slow side, Lean worker count stays at the host cap; we do not add checkers you did not already pay for in RAM.

## Scheduler

`Scheduler` holds:

- a list `backlog` of `WorkItem`;
- a `ProcessPoolExecutor` with `spawn` (Windows-safe) of size `lean_workers`, unless tests pass `use_processes=False`;
- a `ThreadPoolExecutor` of size `llm_inflight`.

`lean_check_job` is picklable: workspace path string, source string, timeout int, result dict.

Do not put a live sqlite connection in the process pool. The parent records timings after `.result()`.

## What we still do not sense

Fan speed, battery, whether the user is presenting, whether a video call is on. The original “optimal use” request asked for more. This is the implemented subset. If you add a sensor, fail soft: missing data must not crash prove.

## After this chapter

Chapter 21 walks the source tree as an extender. Chapter 22 is people. Then limits.
