# Formal systems beyond Mathlib

A **formal system** in aimath is a named set of Lean axioms that still imports Mathlib.

## Loading

YAML → Lean namespace `User.<Name>` → Lean check → status `accepted` or `proposed`.

## Using

```powershell
aimath prove --system Parity --statement "..."
```

Only accepted systems may be selected.

## Interpreting results

A theorem under `Parity` means:

> From Mathlib + the axioms of Parity, Lean derived this statement.

It does **not** mean the axioms are true in ordinary mathematics. Treat them as hypothetical.

## Research definitions vs axioms

Research keeps **definitions** that prove a consequence. Formal systems add **axioms** (assumptions). Prefer definitions when you can; use axioms when you are deliberately studying a theory relative to extra assumptions.
