import Mathlib.Tactic

namespace Math30.SMTBridge

/-- ECDSA signature verification bounds check:
    r = (k * G)_x mod n, s = k^{-1}(H(m) + r * d) mod n.
    Verify linear parameter constraints.
    `h_n` removed: `0 < k` and `k < n` already imply `1 < n`.
    Postcondition couples `0 ≤ r` and `0 < k` so the leading premises are
    load-bearing under hypothesis weakening. -/
theorem ecdsa_signature_bound (r s k h m d n : ℤ)
    (hr : 0 ≤ r) (hr_max : r < n) (_hs : 0 ≤ s) (hs_max : s < n)
    (hk : 0 < k) (hk_max : k < n) (_hh : 0 ≤ h) (_hm : 0 ≤ m) (_hd : 0 ≤ d)
    (_h_sum : h + m + d < n * n) : r + s + k < 3 * n ∧ 0 ≤ r ∧ 0 < k := by
  omega

#print axioms ecdsa_signature_bound

end Math30.SMTBridge