import Mathlib.Tactic

namespace Math30.SMTBridge

/-- ECDSA signature verification bounds check:
    r = (k * G)_x mod n, s = k^{-1}(H(m) + r * d) mod n.
    Verify linear parameter constraints. -/
theorem ecdsa_signature_bound (r s k h m d n : ℤ) (h_n : 1 < n)
    (hr : 0 ≤ r) (hr_max : r < n) (hs : 0 ≤ s) (hs_max : s < n)
    (hk : 0 < k) (hk_max : k < n) (hh : 0 ≤ h) (hm : 0 ≤ m) (hd : 0 ≤ d)
    (h_sum : h + m + d < n * n) : r + s + k < 3 * n := by
  omega

#print axioms ecdsa_signature_bound

end Math30.SMTBridge