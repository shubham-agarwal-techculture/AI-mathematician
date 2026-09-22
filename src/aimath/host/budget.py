"""Turn a host snapshot into a non-invasive worker cap."""

from __future__ import annotations

from dataclasses import dataclass

from aimath.host.probe import HostInfo

_GB = 1024**3


@dataclass(frozen=True)
class Budget:
    lean_workers: int
    llm_inflight: int
    ram_reserve_bytes: int
    memory_pressure: bool


def compute_budget(
    host: HostInfo,
    *,
    ram_reserve_ratio: float = 0.25,
    lean_worker_gb: float = 3.0,
    max_llm_inflight: int = 2,
) -> Budget:
    """Leave one core and a RAM reserve. Shrink to a single Lean worker under pressure.

    One Mathlib import is assumed to need `lean_worker_gb`. When free RAM cannot hold
    that footprint, the cap is one worker so the machine is not filled with checks.
    """
    cpu = max(1, host.cpu_count)
    cores_cap = 1 if cpu == 1 else cpu - 1
    reserve = int(host.ram_total_bytes * ram_reserve_ratio)
    pressure = host.ram_available_bytes < reserve
    usable = max(0, host.ram_available_bytes - reserve)
    per_worker = max(1, int(lean_worker_gb * _GB))
    if pressure or usable < per_worker:
        by_ram = 1
    else:
        by_ram = max(1, usable // per_worker)
    lean_workers = max(1, min(cores_cap, by_ram))
    llm_inflight = 1 if pressure else max(1, max_llm_inflight)
    return Budget(
        lean_workers=lean_workers,
        llm_inflight=llm_inflight,
        ram_reserve_bytes=reserve,
        memory_pressure=pressure,
    )


@dataclass(frozen=True)
class Timings:
    lean_ms: float
    llm_ms: float


def steer_budget(budget: Budget, *, disk_free_bytes: int, temperature_c: float | None, timings: Timings | None) -> tuple[Budget, str]:
    """Shrink work when the disk, the CPU temperature, or the slower side says so.

    A GPU name is reported by the caller. This function does not start GPU work.
    """
    lean = budget.lean_workers
    llm = budget.llm_inflight
    note = "workers follow the CPU and RAM reserve"
    if disk_free_bytes < 5 * _GB:
        lean = 1
        note = "free disk is under 5 GB; one Lean worker"
    if temperature_c is not None and temperature_c >= 90:
        lean = 1
        llm = 1
        note = "a sensor is at or above 90 C; one Lean worker and one model call"
    if timings is not None and timings.lean_ms > 3 * max(timings.llm_ms, 1):
        llm = 1
        note = "Lean is the slow side; model calls cut to one"
    elif timings is not None and timings.llm_ms > 3 * max(timings.lean_ms, 1):
        note = "the model is the slow side; Lean workers stay at the host cap"
    return (
        Budget(
            lean_workers=max(1, lean),
            llm_inflight=max(1, llm),
            ram_reserve_bytes=budget.ram_reserve_bytes,
            memory_pressure=budget.memory_pressure,
        ),
        note,
    )
