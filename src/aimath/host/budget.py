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
