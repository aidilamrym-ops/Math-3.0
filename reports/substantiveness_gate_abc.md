# Substantiveness Gate

- Generated: 2026-11-19T05:57:29Z
- Lean files: **1**  declarations: **4**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/AbcConjectureBoundedVerification.lean:27` | `IsAbcTriple` | predicate `IsAbcTriple` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/AbcConjectureBoundedVerification.lean` | `reyssat_abc_triple_witness` | `htrip` | **KILLED** |
| `lean/spec_v4/certificates/AbcConjectureBoundedVerification.lean` | `abc_coprime_radical_product` | `hab` | **KILLED** |

