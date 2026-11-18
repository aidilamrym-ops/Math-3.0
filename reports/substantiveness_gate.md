# Substantiveness Gate

- Generated: 2026-11-18T08:53:09Z
- Lean files: **1**  declarations: **2**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **1**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/bridges/ContinuumCompactnessBridge.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |

## Mutation Results

- Mutants: **2**  KILLED: **2**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/bridges/ContinuumCompactnessBridge.lean` | `grid_sequential_compactness` | `hu` | **KILLED** |
| `lean/spec_v4/bridges/ContinuumCompactnessBridge.lean` | `dyadic_diagonal_extraction` | `hu` | **KILLED** |

