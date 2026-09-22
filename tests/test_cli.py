from pathlib import Path

import pytest

from aimath.config import load_config
from aimath.lean.project import workspace_ready
from aimath.lean.sandbox import check_source
from aimath.runtime.scheduler import Scheduler, echo_job
from aimath.host.budget import Budget
from aimath.cli import main


def test_example_config_loads(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    text = (root / "config.example.yaml").read_text(encoding="utf-8")
    path = tmp_path / "aimath.yaml"
    path.write_text(text, encoding="utf-8")
    cfg = load_config(path)
    assert cfg.llm.provider == "openai_compatible"
    assert cfg.lean.workspace == (tmp_path / "lean_ws").resolve()
    assert cfg.knowledge.arxiv is False


def test_prove_without_init_tells_you_to_init(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    code = main(["prove", "--statement", "True"])
    assert code == 1
    assert "init" in capsys.readouterr().err


def test_resources_prints_a_budget(capsys):
    code = main(["resources"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Lean workers:" in out
    assert "LLM in flight:" in out


def test_scheduler_thread_pool_runs_a_job():
    budget = Budget(lean_workers=1, llm_inflight=1, ram_reserve_bytes=0, memory_pressure=False)
    with Scheduler(budget, use_processes=False) as sched:
        assert sched.run_lean(echo_job, "ok") == "ok"
        assert sched.run_llm(echo_job, "llm") == "llm"


def test_scheduler_process_pool_runs_a_job():
    budget = Budget(lean_workers=1, llm_inflight=1, ram_reserve_bytes=0, memory_pressure=False)
    with Scheduler(budget, use_processes=True) as sched:
        assert sched.run_lean(echo_job, "process") == "process"


@pytest.mark.skipif(
    not workspace_ready(Path("lean_ws")),
    reason="Mathlib workspace not initialized",
)
def test_live_mathlib_accepts_a_trivial_proof():
    source = "import Mathlib\ntheorem aimath_live : True := trivial\n"
    result = check_source(Path("lean_ws"), source, timeout=180)
    assert result.accepted, result.stderr
