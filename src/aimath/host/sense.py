"""Disk, GPU, temperature, and model-server latency. Failures stay empty, not fatal."""

from __future__ import annotations

import shutil
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class HostSense:
    gpu_name: str | None
    disk_free_bytes: int
    temperature_c: float | None
    llm_latency_ms: float | None


def _gpu_name() -> str | None:
    nvidia = shutil.which("nvidia-smi")
    if nvidia is None:
        return None
    try:
        completed = subprocess.run(
            [nvidia, "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=3,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if completed.returncode != 0:
        return None
    line = (completed.stdout or "").strip().splitlines()
    return line[0].strip() if line else None


def _temperature() -> float | None:
    try:
        import psutil
    except Exception:
        return None
    sensors = getattr(psutil, "sensors_temperatures", None)
    if sensors is None:
        return None
    try:
        reading = sensors()
    except Exception:
        return None
    hottest = None
    for entries in (reading or {}).values():
        for entry in entries:
            current = getattr(entry, "current", None)
            if current is None:
                continue
            hottest = current if hottest is None else max(hottest, current)
    return None if hottest is None else float(hottest)


def _latency_ms(base_url: str | None) -> float | None:
    if not base_url:
        return None
    parsed = urlparse(base_url)
    host = parsed.hostname
    if not host:
        return None
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=1.5):
            pass
    except OSError:
        return None
    return (time.perf_counter() - started) * 1000


def sense_host(root: Path | None = None, base_url: str | None = None) -> HostSense:
    import psutil

    anchor = root or Path.cwd()
    try:
        free = int(psutil.disk_usage(str(anchor)).free)
    except OSError:
        free = 0
    return HostSense(
        gpu_name=_gpu_name(),
        disk_free_bytes=free,
        temperature_c=_temperature(),
        llm_latency_ms=_latency_ms(base_url),
    )
