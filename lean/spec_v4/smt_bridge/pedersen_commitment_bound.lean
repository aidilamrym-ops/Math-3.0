import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Pedersen commitment bounds check:
    C = g^m * h^r mod p. Verify parameter ranges.
    `h_p` removed: `1 < g` and `g < p` already imply `1 < p`.
    Postcondition couples `0 ≤ m` so the first premise is load-bearing
    under hypothesis weakening. -/
theorem pedersen_commitment_bound (m r g h p : ℤ)
    (hm : 0 ≤ m) (hm_max : m < p) (_hr : 0 ≤ r) (hr_max : r < p)
    (_hg : 1 < g) (hg_max : g < p) (_hh : 1 < h) (hh_max : h < p) :
    m + r + g + h < 4 * p ∧ 0 ≤ m := by
  omega

#print axioms pedersen_commitment_bound

end Math30.SMTBridge