import Init.Data.Rat.Basic
import Mathlib.Tactic

namespace Math30.SMTBridge

theorem sign_flip_absence_unsat (e0 : Rat) (e1 : Rat) (e2 : Rat) :
  ¬ (((13.325072930817287 ≤ e0 ∧ e0 ≤ 16.04720839245173) ∧ 
      (10.409477555590692 ≤ e1 ∧ e1 ≤ 13.218241121140293) ∧ 
      (11.068653927850544 ≤ e2 ∧ e2 ≤ 13.931346072149456) ∧ 
      (e0 ≤ 0 ∨ e1 ≤ 0 ∨ e2 ≤ 0))) := by
  intro h
  rcases h with ⟨⟨h1a, h1b⟩, ⟨h2a, h2b⟩, ⟨h3a, h3b⟩, h4⟩
  rcases h4 with h4 | h4 | h4
  · linarith
  · linarith
  · linarith

#print axioms sign_flip_absence_unsat

end Math30.SMTBridge
