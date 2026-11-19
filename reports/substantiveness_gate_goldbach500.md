# Substantiveness Gate

- Generated: 2026-11-19T09:46:18Z
- Lean files: **1**  declarations: **4**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/GoldbachBoundedVerification.lean:19` | `IsGoldbachDecomposable` | predicate `IsGoldbachDecomposable` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **3**  KILLED: **3**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/GoldbachBoundedVerification.lean` | `goldbach_bounded_up_to_100` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/GoldbachBoundedVerification.lean` | `goldbach_bounded_up_to_500` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/GoldbachBoundedVerification.lean` | `goldbach_even_gt_six_odd_primes` | `hn` | **KILLED** |

