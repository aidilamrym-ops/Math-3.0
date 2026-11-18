# Substantiveness Gate

- Generated: 2026-11-17T23:56:58Z
- Lean files: **19**  declarations: **20**  predicates: **0**
- Z3 premise check: **available**
- Findings: HIGH **0**, MEDIUM **0**, LOW **89**
- Waived constant definitions: **0**
- Verdict: **PASS**

## Findings

| Severity | Code | File:Line | Declaration | Detail |
|---|---|---|---|---|
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h1 : r1 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h2 : r2 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h3 : r3 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h4 : r4 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h5 : r5 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h6 : r6 ≤ 2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h7 : 0 ≤ r1` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h8 : 0 ≤ r2` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h9 : 0 ≤ r3` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h10 : 0 ≤ r4` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h11 : 0 ≤ r5` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `h12 : 0 ≤ r6` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/auto_generated_bridge.lean:6` | `auto_generated_unsat` | hypothesis `htot : 13 ≤ r1 + r2 + r3 + r4 + r5 + r6` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_n : 1 < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_sig : 0 ≤ sig_agg` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_sig_max : sig_agg < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_pk : 0 ≤ pk_agg` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_pk_max : pk_agg < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_msg : 0 ≤ msg_hash` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean:9` | `bls_aggregation_bound` | hypothesis `h_msg_max : msg_hash < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/crypto_primitive_feasibility.lean:9` | `crypto_primitive_feasibility` | hypothesis `h_a_pos : 0 < a` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/crypto_primitive_feasibility.lean:9` | `crypto_primitive_feasibility` | hypothesis `h_constraint : a < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `hp : 11 ≤ p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `hg_low : 1 < g` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `hg_high : g < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `ha_low : 0 < a` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `hb_low : 0 < b` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `ha_bound : a < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/dh_parameter_safety.lean:9` | `dh_parameter_safety` | hypothesis `hb_bound : b < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hr : 0 ≤ r` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hr_max : r < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hs : 0 ≤ s` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hs_max : s < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hk : 0 < k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hk_max : k < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hh : 0 ≤ h` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hm : 0 ≤ m` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `hd : 0 ≤ d` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean:11` | `ecdsa_signature_bound` | hypothesis `h_sum : h + m + d < n * n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/elliptic_curve_point_bound.lean:9` | `elliptic_curve_hassee_bound_11` | hypothesis `h_lower : 7 ≤ n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/elliptic_curve_point_bound.lean:9` | `elliptic_curve_hassee_bound_11` | hypothesis `h_upper : n ≤ 17` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_q : 1 < q` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_k : 1 ≤ k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_n : 1 ≤ n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_coeff : -128 ≤ coeff` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_coeff_max : coeff ≤ 127` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean:7` | `kyber_poly_bound` | hypothesis `h_q_size : q ≤ 3329` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:7` | `lattice_svp_bound` | hypothesis `h_det : 0 < det` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:7` | `lattice_svp_bound` | hypothesis `h_n : 1 ≤ n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:7` | `lattice_svp_bound` | hypothesis `h_svp : lambda * lambda ≤ det + n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hm : 0 ≤ m` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hm_max : m < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hr : 0 ≤ r` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hr_max : r < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hg : 1 < g` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hg_max : g < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hh : 1 < h` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean:10` | `pedersen_commitment_bound` | hypothesis `hh_max : h < p` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/ramsey_clique_bound.lean:15` | `ramsey_clique_bound_unsat` | hypothesis `htotal : 13 ≤ ∑ i, r i` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:7` | `rsa_exponent_bound` | hypothesis `he : 1 < e` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:7` | `rsa_exponent_bound` | hypothesis `hd : 1 < d` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:7` | `rsa_exponent_bound` | hypothesis `h_phi : 100 ≤ phi` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean:7` | `rsa_exponent_bound` | hypothesis `h_product : e * d ≤ phi * phi` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `h_n : 1 < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hs : 0 ≤ s` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hs_max : s < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hk : 0 ≤ k` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hk_max : k < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hc : 0 ≤ c` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hc_max : c < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hx : 0 ≤ x` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean:7` | `schnorr_signature_bound` | hypothesis `hx_max : x < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `h_n : 1 < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `ho : 0 ≤ output` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `ho_max : output < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hp : 0 ≤ proof` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hp_max : proof < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hpk : 0 ≤ pk` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hpk_max : pk < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hsk : 0 ≤ sk` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `hsk_max : sk < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `halpha : 0 ≤ alpha` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/vrf_output_bound.lean:7` | `vrf_output_bound` | hypothesis `halpha_max : alpha < n` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean:6` | `zkp_commitment_bound` | hypothesis `h_v : 0 ≤ v` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean:6` | `zkp_commitment_bound` | hypothesis `h_v_max : v < 1024` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean:6` | `zkp_commitment_bound` | hypothesis `h_r : 0 ≤ r` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean:6` | `zkp_commitment_bound` | hypothesis `h_r_max : r < q` is not referenced in the proof |
| LOW | `HYPOTHESIS_NOT_REFERENCED` | `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean:6` | `zkp_commitment_bound` | hypothesis `h_q : 1024 ≤ q` is not referenced in the proof |
| LOW | `SCOPE_UNDECLARED` | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean:1` | `-` | bounded-model file has no explicit Scope/Cakupan/Batas klaim header |

## Mutation Results

- Mutants: **12**  KILLED: **12**  SURVIVED: **0**  survival rate: **0.0**

| File | Declaration | Hypothesis | Verdict |
|---|---|---|---|
| `lean/spec_v4/smt_bridge/auto_generated_bridge.lean` | `auto_generated_unsat` | `h1` | **KILLED** |
| `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean` | `bls_aggregation_bound` | `h_n` | **KILLED** |
| `lean/spec_v4/smt_bridge/crypto_primitive_feasibility.lean` | `crypto_primitive_feasibility` | `h_a_pos` | **KILLED** |
| `lean/spec_v4/smt_bridge/dh_parameter_safety.lean` | `dh_parameter_safety` | `hp` | **KILLED** |
| `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean` | `ecdsa_signature_bound` | `hr` | **KILLED** |
| `lean/spec_v4/smt_bridge/elliptic_curve_point_bound.lean` | `elliptic_curve_hassee_bound_11` | `h_lower` | **KILLED** |
| `lean/spec_v4/smt_bridge/kyber_poly_bound.lean` | `kyber_poly_bound` | `h_q` | **KILLED** |
| `lean/spec_v4/smt_bridge/lattice_svp_bound.lean` | `lattice_svp_bound` | `h_det` | **KILLED** |
| `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean` | `pedersen_commitment_bound` | `hm` | **KILLED** |
| `lean/spec_v4/smt_bridge/ramsey_clique_bound.lean` | `ramsey_clique_bound_unsat` | `hcap` | **KILLED** |
| `lean/spec_v4/smt_bridge/ramsey_clique_bound.lean` | `ramsey_clique_bound_edge_cap` | `hcap` | **KILLED** |
| `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean` | `rsa_exponent_bound` | `he` | **KILLED** |

