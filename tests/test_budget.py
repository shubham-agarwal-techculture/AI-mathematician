from aimath.host.budget import compute_budget
from aimath.host.probe import HostInfo

GB = 1024**3


def _host(cores: int, total_gb: int, available_gb: float) -> HostInfo:
    return HostInfo(
        cpu_count=cores,
        ram_total_bytes=int(total_gb * GB),
        ram_available_bytes=int(available_gb * GB),
        load=0.1,
    )


def test_caps_by_ram_and_cores():
    budget = compute_budget(_host(8, 32, 24), ram_reserve_ratio=0.25, lean_worker_gb=3, max_llm_inflight=2)
    # usable = 24 - 8 = 16 GB, 16 // 3 = 5, cores - 1 = 7
    assert budget.lean_workers == 5
    assert budget.llm_inflight == 2
    assert budget.memory_pressure is False


def test_memory_pressure_shrinks_to_one():
    budget = compute_budget(_host(16, 32, 4), ram_reserve_ratio=0.25, lean_worker_gb=3, max_llm_inflight=4)
    assert budget.lean_workers == 1
    assert budget.llm_inflight == 1
    assert budget.memory_pressure is True


def test_one_core_machine_still_runs_one_worker():
    budget = compute_budget(_host(1, 64, 64), lean_worker_gb=3)
    assert budget.lean_workers == 1


def test_usable_ram_below_one_mathlib_footprint_is_one_worker():
    # reserve is 2 GB, available 5 GB, usable 3 GB, footprint 3 GB is not strictly below,
    # so a tighter case: usable 2 GB < 3 GB footprint.
    budget = compute_budget(_host(8, 16, 6), ram_reserve_ratio=0.25, lean_worker_gb=3)
    assert budget.memory_pressure is False
    assert budget.lean_workers == 1
