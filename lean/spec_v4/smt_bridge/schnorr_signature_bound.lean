import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Schnorr signature verification bounds:
    s = k - c * x mod n. Verify parameter ranges. -/
theorem schnorr_signature_bound (s k c x n : ℤ) (h_n : 1 < n)
    (hs : 0 ≤ s) (hs_max : s < n) (hk : 0 ≤ k) (hk_max : k < n)
    (hc : 0 ≤ c) (hc_max : c < n) (hx : 0 ≤ x) (hx_max : x < n) :
    s + k + c + x < 4 * n := by
  omega

#print axioms schnorr_signature_bound

end Math30.SMTBridge