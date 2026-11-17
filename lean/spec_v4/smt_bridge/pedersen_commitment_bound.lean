import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Pedersen commitment bounds check:
    C = g^m * h^r mod p. Verify parameter ranges. -/
theorem pedersen_commitment_bound (m r g h p : ℤ) (h_p : 1 < p)
    (hm : 0 ≤ m) (hm_max : m < p) (hr : 0 ≤ r) (hr_max : r < p)
    (hg : 1 < g) (hg_max : g < p) (hh : 1 < h) (hh_max : h < p) :
    m + r + g + h < 4 * p := by
  omega

#print axioms pedersen_commitment_bound

end Math30.SMTBridge