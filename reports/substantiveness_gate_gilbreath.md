# Substantiveness Gate

- Generated: 2026-11-19T06:48:09Z
- Lean files: **1**  declarations: **5**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/GilbreathBoundedVerification.lean:36` | `SatisfiesGilbreathHead` | predicate `SatisfiesGilbreathHead` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/GilbreathBoundedVerification.lean` | `gilbreath_first_20_primes` | `hps` | **KILLED** |
| `lean/spec_v4/certificates/GilbreathBoundedVerification.lean` | `gilbreath_parity_preservation_general` | `hhead` | **KILLED** |

