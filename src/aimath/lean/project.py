"""Create the Mathlib Lake workspace and detect whether it is ready."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import httpx

ELAN_HELP = """Lean was not found (`lake` is missing from PATH).
Install elan, then open a new terminal:
  https://github.com/leanprover/elan
On Windows, in PowerShell or Command Prompt:
  curl.exe -L -o elan-init.ps1 https://elan.lean-lang.org/elan-init.ps1
  powershell -ExecutionPolicy Bypass -File .\\elan-init.ps1
  Remove-Item .\\elan-init.ps1
Use curl.exe, not curl. In Windows PowerShell, curl is an alias and irm often
fails to download the GitHub copy of this script.
Then run `aimath init` again. Proofs are refused until Mathlib is present.
"""


def template_dir() -> Path:
    here = Path(__file__).resolve()
    packaged = here.parent.parent / "templates" / "lean_project"
    if (packaged / "lakefile.toml").is_file():
        return packaged
    for parent in here.parents:
        candidate = parent / "templates" / "lean_project"
        if (candidate / "lakefile.toml").is_file():
            return candidate
    raise FileNotFoundError("Lean project template not found")


def lake_executable() -> str | None:
    return shutil.which("lake")


def workspace_ready(workspace: Path) -> bool:
    return (workspace / "lakefile.toml").is_file() and (
        workspace / ".lake" / "packages" / "mathlib"
    ).is_dir()


def fetch_toolchain(url: str, timeout: float = 60) -> str:
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"could not download the Mathlib toolchain pin: {exc}") from exc
    if response.status_code >= 400:
        raise RuntimeError(
            f"could not download the Mathlib toolchain pin ({response.status_code}) from {url}"
        )
    line = response.text.strip().splitlines()
    if not line or not line[0].strip():
        raise RuntimeError(f"toolchain file at {url} was empty")
    return line[0].strip() + "\n"


def init_workspace(workspace: Path, toolchain_url: str, *, force: bool = False) -> None:
    """Copy the template, pin Mathlib's toolchain, then `lake update` and `lake exe cache get`."""
    lake = lake_executable()
    if lake is None:
        raise RuntimeError(ELAN_HELP)
    if workspace.exists() and any(workspace.iterdir()) and not force:
        raise RuntimeError(
            f"{workspace} already exists. Pass --force to replace it, or delete it first."
        )
    if workspace.exists() and force:
        shutil.rmtree(workspace)
    shutil.copytree(template_dir(), workspace)
    pin = fetch_toolchain(toolchain_url)
    (workspace / "lean-toolchain").write_text(pin, encoding="utf-8")
    _run([lake, "update"], workspace)
    _run([lake, "exe", "cache", "get"], workspace)
    if not workspace_ready(workspace):
        raise RuntimeError(
            "lake finished, but .lake/packages/mathlib is missing. "
            "Check the lake output above and run `aimath init --force` after it is fixed."
        )


def _run(cmd: list[str], cwd: Path) -> None:
    print(f"+ {' '.join(cmd)}", flush=True)
    completed = subprocess.run(cmd, cwd=cwd)
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(cmd)}")
