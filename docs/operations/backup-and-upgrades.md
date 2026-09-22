# Backup and upgrades

## Backup

Copy at least:

```text
aimath.yaml
aimath.sqlite
notes/
foreign/
reports/
lean_ws/Aimath/
```

Optional costly mirror: entire `lean_ws/.lake` (reproducible via init).

## Upgrade Python package

```powershell
python -m pip install -e ".[dev]"
pytest
```

## Upgrade Mathlib

Deliberate act:

```powershell
# backup first
aimath init --force
```

Expect a long download. Re-validate with a trivial prove and `status`.
