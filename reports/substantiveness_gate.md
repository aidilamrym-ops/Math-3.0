# Substantiveness Gate

- Generated: 2026-11-18T20:23:41Z
- Lean files: **1**  declarations: **6**  predicates: **2**
- Z3 premise check: **available**
- Findings: HIGH **2**, MEDIUM **4**, LOW **3**
- Waived constant definitions: **0**
- Verdict: **FAIL**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| HIGH | `PREMISE_MUTATION_SURVIVED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | weakening `_hq` to True still compiles |
| HIGH | `TRUE_CONCLUSION` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:56` | `sophie_germain_auxiliary_constraint` | theorem states `True` |
| MEDIUM | `DECORATIVE_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:56` | `sophie_germain_auxiliary_constraint` | hypothesis `_hp_prime : Nat.Prime p` is not referenced in the proof |
| MEDIUM | `DECORATIVE_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:56` | `sophie_germain_auxiliary_constraint` | hypothesis `_hq_prime : Nat.Prime q` is not referenced in the proof |
| MEDIUM | `DECORATIVE_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:56` | `sophie_germain_auxiliary_constraint` | hypothesis `_heq : q = 2 * p + 1` is not referenced in the proof |
| MEDIUM | `DECORATIVE_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:56` | `sophie_germain_auxiliary_constraint` | hypothesis `_ha : a ≠ 0` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | hypothesis `_hq : IsSafePrime q` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | hypothesis `_hp : IsSophieGermainPrime p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | hypothesis `heq : q = 2 * p + 1` is not referenced in the proof |

## Mutation Results

- Mutants: **1**  KILLED: **0**  SURVIVED: **1**  survival rate: **1.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean` | `dh_safe_prime_order_property` | `_hq` | **SURVIVED** |

