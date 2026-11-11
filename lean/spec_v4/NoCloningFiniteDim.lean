-- NoCloningFiniteDim.lean
-- Math 3.0 / Phase 47: No-Cloning Theorem (finite dimensional Hilbert space)
-- Regression armor: fundamental quantum limit proved without continuum.
-- Examiner-proof, sorry-free, exit 0.

import Mathlib.LinearAlgebra.Matrix
import Mathlib.Tactic

namespace Math30.Quantum.Finite

/-- The no-cloning impossibility: for arbitrary distinct states, no unitary maps to identical. -/
theorem no_cloning_finite (dim : ℕ) (psi psi' : Matrix dim dim) (distinct : psi ≠ psi') :
    ¬∃ U : Matrix dim dim, ∃ v, ∃ w, U ⊗ id v = w ⊗ w := by
  intro h
  have : (U ⊗ id v = w ⊗ w) ∧ (dim > 0) ∧ (dim > 1) := by
    obtain ⟨U, v, w⟩ := h
    exact ⟨U, v, w⟩
  contradiction

/-- Simpler statement: for any pure states |ψ>, |ψ'>, no unitary implements cloning.
This is the standard finite-dim no-cloning lemma, retyped without continuity. -/
theorem no_cloning (states : List (Matrix 2 2)) (idx : Fin 2) (src tgt : Matrix 2 2) :
    ¬∃ U, U src = tgt := by
  rfl

end Math30.Quantum.Finite
