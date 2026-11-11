-- NoCloningFiniteDim.lean
-- Math 3.0 / Phase 47: Finite-dimensional no-cloning witness over ℤ
-- Bounded regression armor: linear cloning of a two-state system is impossible.
-- The model is a two-dimensional integer state space with an explicit additivity law;
-- it is a finite linear-algebra toy, not a full Hilbert-space quantum-mechanical proof.

import Mathlib.Data.Int.Basic
import Mathlib.Tactic

namespace Math30.Quantum.Finite

/-- A one-qubit state over the integers. -/
abbrev QState := Fin 2 → ℤ

/-- A two-register state over the integers. -/
abbrev QPair := Fin 2 × Fin 2 → ℤ

/-- Basis state |0>. -/
def e0 : QState := fun i => if i = 0 then 1 else 0

/-- Basis state |1>. -/
def e1 : QState := fun i => if i = 1 then 1 else 0

/-- Pointwise addition of states. -/
def addState (v w : QState) : QState := fun i => v i + w i

/-- Tensor product of two one-qubit states. -/
def tensor (v w : QState) : QPair := fun p => v p.1 * w p.2

/-- A cloning candidate with the additive linearity law. -/
structure CloneMap where
  toFun : QState → QPair
  map_add : ∀ v w : QState,
    toFun (addState v w) = fun p => toFun v p + toFun w p

/-- No-cloning: a map cannot simultaneously clone |0>, clone |1>, and clone their
superposition |0> + |1>. The obstruction is the two cross terms produced by the
superposition, which are absent from the sum of the two basis clones. -/
theorem no_cloning_finite (U : CloneMap)
    (h0 : U.toFun e0 = tensor e0 e0)
    (h1 : U.toFun e1 = tensor e1 e1)
    (hsup : U.toFun (addState e0 e1) = tensor (addState e0 e1) (addState e0 e1)) :
    False := by
  have hadd : U.toFun (addState e0 e1) =
      fun p => tensor e0 e0 p + tensor e1 e1 p := by
    rw [U.map_add, h0, h1]
  have hpoint := congrFun (hadd.symm.trans hsup) ((0 : Fin 2), (1 : Fin 2))
  norm_num [tensor, e0, e1, addState] at hpoint

end Math30.Quantum.Finite
