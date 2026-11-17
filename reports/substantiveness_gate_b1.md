# Substantiveness Gate

- Generated: 2026-11-17T02:31:20Z
- Lean files: **3**  declarations: **24**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **2**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/CollatzBoundedDefeat.lean:72` | `collatz_horizon_defeat` | hypothesis `hn : n ≥ 1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/CollatzBoundedDefeat.lean:72` | `collatz_horizon_defeat` | hypothesis `hn_max : n ≤ 100` is not referenced in the proof |

