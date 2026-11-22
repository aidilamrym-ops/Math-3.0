# Batch C Pair 6 — quantum_tensor_engine.py flaw archive

**Date:** 2026-11-22
**File:** `Math30Solvers/quantum_tensor_engine.py`
**Original:** `quantum_tensor_engine.py.orig` (verbatim pre-repair)

## Defect (Stage 3: unguarded division)

`shor_modular_exponentiation(base, exp, modulus)` performed `base % modulus`
and `(result * cur_base) % modulus` with no guard on `modulus`. Calling with
`modulus <= 0` raised a raw `ZeroDivisionError` instead of a fail-closed
`QUANTUM_ENTANGLEMENT_ALARM`, violating the resolution-alarm discipline.

## Repair

Added trust-boundary input validation at top of function:

```python
if modulus <= 0:
    raise ValueError(f"QUANTUM_ENTANGLEMENT_ALARM: invalid modulus {modulus} (must be positive).")
```

`raise` chosen over `return None` so:
- invalid input is strictly fail-closed (no silent sentinel propagation);
- no new hardcoded `return None` literal added (2 legacy precision-alarm
  sentinels remain, unchanged).

## Verification

- `modulus=0` / `modulus=-5` → `ValueError` with alarm prefix (fail-closed).
- `shor_modular_exponentiation(7, 13, 15) == 7` (valid path intact).
- Bell-state norm identity `sum(|a_i|^2) == 2` intact.
- `audit_hardcoded_nodes.py`: 0 findings.
- `blindspot_audit.py`: 0 findings, 0 warnings.
