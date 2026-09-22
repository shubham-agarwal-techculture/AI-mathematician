"""Read CPU and memory, and keep this process from competing with the user."""

from __future__ import annotations

import os
from dataclasses import dataclass

_LOWERED = False


@dataclass(frozen=True)
class HostInfo:
    cpu_count: int
    ram_total_bytes: int
    ram_available_bytes: int
    load: float


def lower_priority() -> str:
    """Drop to below-normal priority once. Further calls leave the priority where it is."""
    global _LOWERED
    if _LOWERED:
        return "below normal" if os.name == "nt" else "niced"
    try:
        import psutil

        if os.name == "nt":
            psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            _LOWERED = True
            return "below normal"
        os.nice(5)
        _LOWERED = True
        return "niced"
    except Exception:
        return "unchanged"


def probe() -> HostInfo:
    import psutil

    lower_priority()
    cpu = psutil.cpu_count(logical=True) or 1
    memory = psutil.virtual_memory()
    try:
        load = float(psutil.getloadavg()[0])
    except (AttributeError, OSError):
        load = float(psutil.cpu_percent(interval=0.0)) / 100.0 * cpu
    return HostInfo(
        cpu_count=cpu,
        ram_total_bytes=int(memory.total),
        ram_available_bytes=int(memory.available),
        load=load,
    )
