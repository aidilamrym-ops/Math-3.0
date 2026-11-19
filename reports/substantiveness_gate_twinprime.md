# Substantiveness Gate

- Generated: 2026-11-19T04:38:40Z
- Lean files: **1**  declarations: **3**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **2**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/TwinPrimeBoundedVerification.lean:35` | `twin_prime_mod6_and_diff_sq_24` | hypothesis `hgt3 : 3 < p` is not referenced in the proof |
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/TwinPrimeBoundedVerification.lean:21` | `IsTwinPrime` | predicate `IsTwinPrime` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/TwinPrimeBoundedVerification.lean` | `twin_prime_witnesses_below_200` | `hp` | **KILLED** |
| `lean/spec_v4/certificates/TwinPrimeBoundedVerification.lean` | `twin_prime_mod6_and_diff_sq_24` | `htwin` | **KILLED** |

