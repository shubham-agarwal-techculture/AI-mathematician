# Data and files layout

## Project repository (source)

```text
AI_mathematician/
  README.md
  pyproject.toml
  config.example.yaml
  docs/                 this documentation
  examples/             sample YAML systems
  scripts/              PDF builder, helpers
  src/aimath/           Python package
  templates/lean_project/
  tests/
```

## Runtime workspace (after init)

```text
./aimath.yaml
./aimath.sqlite
./lean_ws/
   lean-toolchain
   lakefile.toml
   Aimath.lean
   Aimath/User/*.lean
   Aimath/Research/*.lean
   .lake/packages/mathlib/...
   .aimath_scratch/     temporary checks
./notes/
./foreign/
./reports/
```

## SQLite tables

- `systems` — name, lean_src, status
- `statements` — text, status, personality, detail, content hash
- `attempts` — lean_src, accepted flag, output
- `timings` — recent lean/llm milliseconds for steering
