import Init.Data.Rat.Basic
import Mathlib.Tactic

namespace Math30.SMTBridge

theorem ledger_cross_multiplication_unsat :
  ¬ (50000000000000000 > (0 : Rat) ∧ 
     10000000000000000 > (0 : Rat) ∧ 
     10000000000000000 > (0 : Rat) ∧ 
     200000000000000 > (0 : Rat) ∧ 
     50000000000000000 > (0 : Rat) ∧ 
     4000000000000000 > (0 : Rat) ∧ 
     (2 * 7111820700942209 ≥ 50000000000000000 ∨ 
      2488515809935017 ≤ 0 ∨ 
      2 * 1836129694132613 ≥ 10000000000000000 ∨ 
      54729512101731 ≤ 0 ∨ 
      2 * 8833926622287651 ≥ 50000000000000000 ∨ 
      1066595521012613 ≤ 0)) := by
  intro h
  rcases h with ⟨h1, h2, h3, h4, h5, h6, h7⟩
  rcases h7 with h7 | h7 | h7 | h7 | h7 | h7
  · linarith
  · linarith
  · linarith
  · linarith
  · linarith
  · linarith

#print axioms ledger_cross_multiplication_unsat

end Math30.SMTBridge
