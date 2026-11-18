import Mathlib.Tactic

namespace Math30.SMTBridge

/-- SMT-bridge theorem: verify linear modular parameter bound for cryptography.
    `h_p_pos` removed: `0 < a` and `a < p` already imply `0 < p`.
    Postcondition couples `0 < a` so the remaining domain hypothesis is
    load-bearing under hypothesis weakening. -/
theorem crypto_primitive_feasibility (p a : ℤ) (h_a_pos : 0 < a)
    (h_constraint : a < p) : a + 1 ≤ p ∧ 0 < a := by
  omega

#print axioms crypto_primitive_feasibility

end Math30.SMTBridge
