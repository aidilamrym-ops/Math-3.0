# Substantiveness Gate

- Generated: 2026-11-18T20:34:24Z
- Lean files: **1**  declarations: **6**  predicates: **2**
- Z3 premise check: **available**
- Findings: HIGH **5**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **FAIL**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| HIGH | `PREMISE_MUTATION_SURVIVED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | weakening `hp` to True still compiles |
| HIGH | `TRIVIAL_TRUE_CONSEQUENCE` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | conclusion contains a vacuous `True` conjunct or codomain |
| HIGH | `UNUSED_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | hypothesis `hp : Nat.Prime p` is not referenced in the proof |
| HIGH | `UNUSED_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | hypothesis `hp3 : 3 ≤ p` is not referenced in the proof |
| HIGH | `UNUSED_HYPOTHESIS` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:57` | `sophie_germain_auxiliary_constraint` | hypothesis `ha : a ^ p = 1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean:50` | `dh_safe_prime_order_property` | hypothesis `hp : IsSophieGermainPrime p` is not referenced in the proof |

## Mutation Results

- Mutants: **1**  KILLED: **0**  SURVIVED: **1**  survival rate: **1.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/SophieGermainFermatTheorem.lean` | `dh_safe_prime_order_property` | `hp` | **SURVIVED** |

