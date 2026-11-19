# Substantiveness Gate

- Generated: 2026-11-19T11:12:55Z
- Lean files: **1**  declarations: **8**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **0**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Mutation Results

- Mutants: **6**  KILLED: **6**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `no_lehmer_composite_up_to_200` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `lehmer_composite_must_be_squarefree` | `hdiv` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `lehmer_composite_must_be_odd` | `hdiv` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `lehmer_composite_odd_and_squarefree` | `hdiv` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `totient_prod_primes` | `hprime` | **KILLED** |
| `lean/spec_v4/certificates/LehmerTotientBoundedVerification.lean` | `no_lehmer_composite_up_to_1000` | `hn` | **KILLED** |

No substantiveness findings detected.
