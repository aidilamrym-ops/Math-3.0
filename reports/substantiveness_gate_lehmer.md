# Substantiveness Gate

- Generated: 2026-11-19T07:47:04Z
- Lean files: **1**  declarations: **3**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean:26` | `IsLehmerCompositeWitness` | predicate `IsLehmerCompositeWitness` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `no_lehmer_composite_up_to_100` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `lehmer_composite_must_be_squarefree` | `hdiv` | **KILLED** |

