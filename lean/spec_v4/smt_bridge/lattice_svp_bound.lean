import Mathlib.Tactic

-- Scope: finite integer SVP arithmetic bound only. This file makes no claim
-- about continuous lattices, computational SVP hardness, or cryptographic
-- security parameters.

namespace Math30.SMTBridge

/-- Lattice Shortest Vector Problem (SVP) bound verification:
    Minkowski bound approximation check.

    `omega` cannot discharge the nonlinear premise `lambda * lambda ≤ det + n`.
    The proof splits on the sign of `lambda`: non-positive values are bounded
    by `det + n + 1` directly, and positive values satisfy
    `lambda ≤ lambda * lambda`. -/
theorem lattice_svp_bound (det : ℤ) (lambda : ℤ) (n : ℤ) (h_det : 0 < det) (h_n : 1 ≤ n)
    (h_svp : lambda * lambda ≤ det + n) : lambda ≤ det + n + 1 := by
  have hS : (0 : ℤ) ≤ det + n := by linarith [h_det, h_n]
  by_cases h : lambda ≤ 0
  · linarith [hS, h_svp]
  · have hsq : lambda ≤ lambda * lambda := by
      nlinarith [mul_nonneg (show (0 : ℤ) ≤ lambda by linarith)
        (show (0 : ℤ) ≤ lambda - 1 by linarith)]
    linarith [hS, hsq, h_svp]

#print axioms lattice_svp_bound

end Math30.SMTBridge
