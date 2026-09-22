"""Local pools. Lean checks run in processes; model calls run on threads."""

from __future__ import annotations

from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import get_context
from typing import Callable

from aimath.host.budget import Budget
from aimath.runtime.protocol import WorkItem


def echo_job(text: str) -> str:
    """Picklable stand-in used to test the process pool."""
    return text


class Scheduler:
    """Drain a backlog with a Lean process pool and an LLM thread pool.

    Slots are semaphores, so a thread that is waiting on Lean does not hold an
    LLM slot. A later remote worker would consume the same `WorkItem` JSON.
    """

    def __init__(self, budget: Budget, *, use_processes: bool = True) -> None:
        self.budget = budget
        self.backlog: list[WorkItem] = []
        workers = max(1, budget.lean_workers)
        llm_workers = max(1, budget.llm_inflight)
        if use_processes:
            self._lean_pool: ProcessPoolExecutor | ThreadPoolExecutor = ProcessPoolExecutor(
                max_workers=workers,
                mp_context=get_context("spawn"),
            )
        else:
            self._lean_pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="lean")
        self._llm_pool = ThreadPoolExecutor(max_workers=llm_workers, thread_name_prefix="llm")

    def enqueue(self, item: WorkItem) -> None:
        self.backlog.append(item)

    def submit_lean(self, fn: Callable, *args) -> Future:
        return self._lean_pool.submit(fn, *args)

    def submit_llm(self, fn: Callable, *args) -> Future:
        return self._llm_pool.submit(fn, *args)

    def run_lean(self, fn: Callable, *args):
        return self.submit_lean(fn, *args).result()

    def run_llm(self, fn: Callable, *args):
        return self.submit_llm(fn, *args).result()

    def close(self) -> None:
        self._lean_pool.shutdown(wait=True, cancel_futures=False)
        self._llm_pool.shutdown(wait=True, cancel_futures=False)

    def __enter__(self) -> Scheduler:
        return self

    def __exit__(self, *exc) -> None:
        self.close()
