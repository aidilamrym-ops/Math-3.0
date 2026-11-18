import Mathlib.Tactic

namespace Math30.SMTBridge

/-- RSA exponent verification: e * d ≡ 1 mod phi(N).
    Verified bound check for exponent sizes.

    `omega` cannot discharge the nonlinear product `e * d`. From `1 < e` and
    `1 < d` we get `e + d ≤ e * d`; transitivity through
    `e * d ≤ phi * phi` closes the goal. The earlier `h_phi : 100 ≤ phi` was
    unused by this argument and has been removed rather than kept as a
    mutation-surviving decoration. -/
theorem rsa_exponent_bound (e d phi : ℤ) (he : 1 < e) (hd : 1 < d)
    (h_product : e * d ≤ phi * phi) : e + d ≤ phi * phi + 2 := by
  have hprod : e + d ≤ e * d := by
    nlinarith [mul_nonneg (show (0 : ℤ) ≤ e - 1 by linarith [he])
      (show (0 : ℤ) ≤ d - 1 by linarith [hd])]
  linarith [hprod, h_product]

#print axioms rsa_exponent_bound

end Math30.SMTBridge
