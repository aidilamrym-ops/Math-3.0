# Substantiveness Gate

- Generated: 2026-11-19T09:47:18Z
- Lean files: **1**  declarations: **4**  predicates: **1**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **2**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/certificates/LegendreBoundedVerification.lean:173` | `legendre_interval_gap_grows` | hypothesis `hn : 1 ≤ n` is not referenced in the proof |
| LOW | `WITNESS_MISSING` | `lean/spec_v4/certificates/LegendreBoundedVerification.lean:23` | `HasPrimeBetweenSquares` | predicate `HasPrimeBetweenSquares` is never applied to ground arguments or existentially witnessed |

## Mutation Results

- Mutants: **3**  KILLED: **3**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/certificates/LegendreBoundedVerification.lean` | `legendre_bounded_up_to_30` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/LegendreBoundedVerification.lean` | `legendre_bounded_up_to_100` | `hn` | **KILLED** |
| `lean/spec_v4/certificates/LegendreBoundedVerification.lean` | `legendre_interval_gap_grows` | `hn` | **KILLED** |

