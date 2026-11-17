import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Kyber (ML-KEM) polynomial coefficient bounds:
    Verify coefficient ranges for NTT-friendly parameters. -/
theorem kyber_poly_bound (coeff q k n : ℤ) (h_q : 1 < q) (h_k : 1 ≤ k)
    (h_n : 1 ≤ n) (h_coeff : -128 ≤ coeff) (h_coeff_max : coeff ≤ 127)
    (h_q_size : q ≤ 3329) :
    coeff * coeff < q * q := by
  have h₁ : coeff * coeff ≤ 127 * 127 := by
    nlinarith
  have h₂ : 127 * 127 < q * q := by
    have h₃ : q ≥ 2 := by linarith
    nlinarith
  nlinarith

#print axioms kyber_poly_bound

end Math30.SMTBridge