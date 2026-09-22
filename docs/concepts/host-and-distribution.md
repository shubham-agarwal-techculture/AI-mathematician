# Host awareness and distribution

## Non-invasive local use

On start, aimath:

- Lowers process priority (below normal on Windows, nice on Unix when possible).
- Leaves one CPU core free when possible.
- Reserves a fraction of RAM.
- Caps Lean workers by Mathlib memory footprint.
- Optionally shrinks work under disk pressure, high temperature, or slow Lean timings.

Sensors for GPU, temperature, and model latency are best-effort. Missing sensors do not crash the tool.

## Distribution

`serve` / `worker` share Lean **check** jobs over a JSON-lines socket protocol. Default bind is localhost. Non-loopback binds require a token. Disconnects requeue jobs with a retry budget.

This is a real multi-process distributed path for verification work. It is not a full cluster scheduler with autoscaling, but it is the designed extension point for remote nodes.
