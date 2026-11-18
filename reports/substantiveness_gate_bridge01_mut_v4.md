# Substantiveness Gate

- Generated: 2026-11-18T02:45:16Z
- Lean files: **1**  declarations: **4**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **0**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Mutation Results

- Mutants: **4**  KILLED: **4**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/bridges/ScaleInvariantEnergyBridge.lean` | `energy_nonincreasing` | `hD` | **KILLED** |
| `lean/spec_v4/bridges/ScaleInvariantEnergyBridge.lean` | `flat_step_zero_dissipation` | `hν` | **KILLED** |
| `lean/spec_v4/bridges/ScaleInvariantEnergyBridge.lean` | `no_finite_time_blowup` | `hB` | **KILLED** |
| `lean/spec_v4/bridges/ScaleInvariantEnergyBridge.lean` | `lattice_family_energy_bound` | `hN` | **KILLED** |

No substantiveness findings detected.
