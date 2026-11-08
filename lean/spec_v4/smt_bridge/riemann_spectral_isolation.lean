import Init.Data.Rat.Basic
import Mathlib.Tactic

/-
  Math 3.0 SMT -> Lean certificate bridge (v1.0.0)
  Source: smt/phase4/riemann_spectral_isolation.smt2
  Source-SHA256: 32adfebbf50d154939b10bd11d4cfe6b3ac892a8915612c10e9d79f7734bd6b0
  Logic: QF_NRA
  SMT verdict: unsat
  The theorem below re-proves the same constraint system natively in Lean 4.
  It is not a translation of an internal Z3 proof object.
  No sorry, admit, or axiom is used.
-/

namespace Math30.SMTBridge

theorem riemann_spectral_isolation_unsat (t : Rat) :
  ¬ (((t ≥ (0 : Rat))) ∧ ((¬ ((t * t) ≥ (0 : Rat))))) := by
  intro h
  rcases h with ⟨h1, h2⟩
  have h5 : False := by
    norm_num at h1 h2 ⊢
    <;>
    (try contradiction) <;>
    (try nlinarith) <;>
    (try norm_num at * <;> nlinarith)
  exact h5

#print axioms riemann_spectral_isolation_unsat

end Math30.SMTBridge
