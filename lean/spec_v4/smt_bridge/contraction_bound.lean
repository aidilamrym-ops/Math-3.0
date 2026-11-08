import Init.Data.Rat.Basic
import Mathlib.Tactic

namespace Math30.SMTBridge

theorem contraction_bound_unsat (c0 : Rat) (c1 : Rat) (c2 : Rat) :
  ¬ (((0 ≤ c0 ∧ c0 ≤ 0.14223641401884418) ∧ 
      (0 ≤ c1 ∧ c1 ≤ 0.1836129694132613) ∧ 
      (0 ≤ c2 ∧ c2 ≤ 0.17667853244575302) ∧ 
      (2 * c0 ≥ 1 ∨ 2 * c1 ≥ 1 ∨ 2 * c2 ≥ 1))) := by
  intro h
  rcases h with ⟨⟨h1a, h1b⟩, ⟨h2a, h2b⟩, ⟨h3a, h3b⟩, h4⟩
  rcases h4 with h4 | h4 | h4
  · linarith
  · linarith
  · linarith

#print axioms contraction_bound_unsat

end Math30.SMTBridge
