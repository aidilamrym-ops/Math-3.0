# Full-Surface Lean Compile Audit

- Generated: 2026-11-18 09:04:28
- Scope: **full** (canonical receipt: true)
- Verdict: **FAIL** (complete: false)
- Surfaces: `lean/spec_v4`, `Math30Kernel`, `Math30Interfaces`
- Total files: **504**
- Compiled: **504**
- Counts: `{'PASS': 501, 'FAIL': 3}`
- PASS files with compiler warnings: **8**
- Aggregate compile time: 3060.7s

## Failures

| Status | File | Detail |
|---|---|---|
| FAIL | `lean/spec_v4/smt_bridge/kyber_poly_bound.lean` | spec_v4/smt_bridge/kyber_poly_bound.lean:12:4: error: linarith failed to find a contradiction |
| FAIL | `lean/spec_v4/smt_bridge/lattice_svp_bound.lean` | spec_v4/smt_bridge/lattice_svp_bound.lean:9:2: error: omega could not prove the goal: |
| FAIL | `lean/spec_v4/smt_bridge/rsa_exponent_bound.lean` | spec_v4/smt_bridge/rsa_exponent_bound.lean:9:2: error: omega could not prove the goal: |

## Warnings (PASS with diagnostics)

| File | Warnings |
|---|---|
| `lean/spec_v4/EuclidFermatArmor.lean` | 6 |
| `lean/spec_v4/smt_bridge/bls_aggregation_bound.lean` | 6 |
| `lean/spec_v4/smt_bridge/dh_parameter_safety.lean` | 8 |
| `lean/spec_v4/smt_bridge/ecdsa_signature_bound.lean` | 10 |
| `lean/spec_v4/smt_bridge/pedersen_commitment_bound.lean` | 6 |
| `lean/spec_v4/smt_bridge/schnorr_signature_bound.lean` | 10 |
| `lean/spec_v4/smt_bridge/vrf_output_bound.lean` | 12 |
| `lean/spec_v4/smt_bridge/zkp_commitment_bound.lean` | 4 |
