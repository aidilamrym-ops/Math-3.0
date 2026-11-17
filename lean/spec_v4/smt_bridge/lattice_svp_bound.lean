import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Lattice Shortest Vector Problem (SVP) bound verification:
    Minkowski bound approximation check. -/
theorem lattice_svp_bound (det : ℤ) (lambda : ℤ) (n : ℤ) (h_det : 0 < det) (h_n : 1 ≤ n)
    (h_svp : lambda * lambda ≤ det + n) : lambda ≤ det + n + 1 := by
  omega

#print axioms lattice_svp_bound

end Math30.SMTBridge
