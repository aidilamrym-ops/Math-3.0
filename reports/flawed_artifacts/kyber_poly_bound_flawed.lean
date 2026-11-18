-- ARCHIVED_INVALID
-- Original `kyber_poly_bound` declaration, preserved verbatim because its
-- statement is FALSE as written. Do not import or rehabilitate this file.
--
-- Counterexample: coeff = -128, q = 2, k = 1, n = 1.
--   * 1 < q                    (1 < 2)
--   * 1 <= k, 1 <= n           (1 <= 1)
--   * -128 <= coeff <= 127     (-128 <= -128 <= 127)
--   * q <= 3329                (2 <= 3329)
--   * conclusion: coeff * coeff < q * q  becomes  16384 < 4, which is FALSE.
--
-- The active surface now carries `kyber_poly_bound_3329`, with the modulus
-- fixed at the actual Kyber prime q = 3329.

import Mathlib.Tactic

namespace Math30.SMTBridge

/-- ARCHIVED_INVALID: false as stated; see the header for the counterexample. -/
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

end Math30.SMTBridge
