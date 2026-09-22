from pathlib import Path

from aimath.formal.system import load_system, render_system
from aimath.lean.project import template_dir
from aimath.lean.sandbox import check_source, render_proof, render_typecheck
from aimath.textutil import find_banned


def test_user_system_imports_mathlib(tmp_path: Path):
    path = tmp_path / "parity.yaml"
    path.write_text(
        "name: Parity\nnotes: toy\naxioms:\n  - name: zero_even\n"
        '    statement: "∃ k : Nat, 0 = 2 * k"\n',
        encoding="utf-8",
    )
    source = render_system(load_system(path))
    assert source.startswith("import Mathlib")
    assert "namespace User.Parity" in source
    assert "axiom zero_even : ∃ k : Nat, 0 = 2 * k" in source
    assert "end User.Parity" in source


def test_template_requires_mathlib():
    text = (template_dir() / "lakefile.toml").read_text(encoding="utf-8")
    assert 'name = "mathlib"' in text
    assert 'scope = "leanprover-community"' in text


def test_proof_and_typecheck_import_mathlib_without_sorry():
    proof = render_proof("∀ n : Nat, n = n", "rfl", ["Mathlib.Data.Nat.Basic"])
    assert "import Mathlib.Data.Nat.Basic" in proof
    assert "theorem aimath_result" in proof
    assert find_banned(proof) is None
    check = render_typecheck("∀ n : Nat, n = n", None)
    assert check.startswith("import Mathlib")
    assert "Or.inr trivial" in check
    assert find_banned(check) is None


def test_sorry_is_rejected_before_lean_runs(tmp_path: Path):
    source = "import Mathlib\ntheorem t : True := by sorry\n"
    result = check_source(tmp_path, source, timeout=5)
    assert result.accepted is False
    assert "sorry" in result.reason
    assert result.returncode == 1
