# Substantiveness Gate

- Generated: 2026-11-18T20:36:48Z
- Lean files: **1**  declarations: **6**  predicates: **2**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **2**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | hypothesis `hp : Nat.Prime p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | hypothesis `hp3 : 3 ≤ p` is not referenced in the proof |

## Mutation Results

- Mutants: **1**  KILLED: **1**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean` | `dh_safe_prime_order_property` | `hp` | **KILLED** |

