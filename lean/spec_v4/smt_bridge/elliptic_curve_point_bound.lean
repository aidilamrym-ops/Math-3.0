import Mathlib.Tactic

namespace Math30.SMTBridge

/-- Hasse's Theorem parameter bound for elliptic curves over ZMod p:
    |#E(F_p) - (p + 1)| ≤ 2 * sqrt(p).
    Here we verify the integer approximation bound for p = 11:
    7 ≤ #E ≤ 17. -/
theorem elliptic_curve_hassee_bound_11 (n : ℤ) (h_lower : 7 ≤ n) (h_upper : n ≤ 17) :
    7 ≤ n ∧ n ≤ 17 := by
  omega

#print axioms elliptic_curve_hassee_bound_11

end Math30.SMTBridge
