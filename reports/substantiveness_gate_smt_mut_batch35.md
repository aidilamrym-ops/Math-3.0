# Substantiveness Gate

- Generated: 2026-11-18T01:28:00Z
- Lean files: **3**  declarations: **3**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **9**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:12` | `kyber_poly_bound_3329` | hypothesis `h_coeff : -128 ≤ coeff` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:12` | `kyber_poly_bound_3329` | hypothesis `h_coeff_max : coeff ≤ 127` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:12` | `lattice_svp_bound` | hypothesis `h_det : 0 < det` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:12` | `lattice_svp_bound` | hypothesis `h_n : 1 ≤ n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:12` | `lattice_svp_bound` | hypothesis `h_svp : lambda * lambda ≤ det + n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:13` | `rsa_exponent_bound` | hypothesis `he : 1 < e` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:13` | `rsa_exponent_bound` | hypothesis `hd : 1 < d` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:13` | `rsa_exponent_bound` | hypothesis `h_product : e * d ≤ phi * phi` is not referenced in the proof |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |

## Mutation Results

- Mutants: **3**  KILLED: **3**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/smt_bridge/kyber_poly_bound.lean` | `kyber_poly_bound_3329` | `h_coeff` | **KILLED** |
| `lean/spec_v4/smt_bridge/lattice_svp_bound.lean` | `lattice_svp_bound` | `h_det` | **KILLED** |
| `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean` | `rsa_exponent_bound` | `he` | **KILLED** |

