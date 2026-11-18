import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Kyber (ML-KEM) polynomial coefficient bound at the actual Kyber prime
    modulus `q = 3329`.

    This replaces the earlier `kyber_poly_bound`, which quantified `q` under
    only `1 < q` and was therefore false at `q = 2`. The archived false
    declaration and its counterexample are preserved in
    `reports/flawed_artifacts/kyber_poly_bound_flawed.lean`. -/
theorem kyber_poly_bound_3329 (coeff : ℤ) (h_coeff : -128 ≤ coeff)
    (h_coeff_max : coeff ≤ 127) : coeff * coeff < 3329 * 3329 := by
  have hlo : (0 : ℤ) ≤ coeff + 128 := by linarith [h_coeff]
  have hhi : (0 : ℤ) ≤ 128 - coeff := by linarith [h_coeff_max]
  have hsquare : coeff * coeff ≤ 128 * 128 := by
    nlinarith [mul_nonneg hlo hhi]
  nlinarith

#print axioms kyber_poly_bound_3329

end Math30.SMTBridge
