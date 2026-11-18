import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Schnorr signature verification bounds:
    s = k - c * x mod n. Verify parameter ranges. -/
theorem schnorr_signature_bound (s k c x n : ℤ) (_h_n : 1 < n)
    (_hs : 0 ≤ s) (hs_max : s < n) (_hk : 0 ≤ k) (hk_max : k < n)
    (_hc : 0 ≤ c) (hc_max : c < n) (_hx : 0 ≤ x) (hx_max : x < n) :
    s + k + c + x < 4 * n := by
  omega

#print axioms schnorr_signature_bound

end Math30.SMTBridge