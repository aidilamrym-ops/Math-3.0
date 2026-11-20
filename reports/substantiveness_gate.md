# Substantiveness Gate

- Generated: 2026-11-20T04:37:47Z
- Lean files: **1**  declarations: **4**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/FiniteLimitBoundary.lean:34` | `finite_telescope_bound` | hypothesis `_hd : 0 ≤ d` is not referenced in the proof |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/FiniteLimitBoundary.lean` | `finite_telescope_bound` | `_hd` | **KILLED** |
| `lean/spec_v4/FiniteLimitBoundary.lean` | `finite_telescope_bound_mut` | `_hd` | **KILLED** |

