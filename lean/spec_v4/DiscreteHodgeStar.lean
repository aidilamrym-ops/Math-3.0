-- DiscreteHodgeStar.lean
-- Math 3.0 / Fase 59 (rebuilt in Batch 10): Discrete Hodge Star on a Finite Cycle
--
-- Scope:
--   * the cyclic lattice with sites `Fin n` and the forward difference
--       (d a)_i = a_{i+1} - a_i;
--   * the formal adjoint `delta = d^T` with respect to the standard inner
--     product on cochains;
--   * the Hodge star as the metric identification between 0- and 1-cochains.
--     On the unit-spacing cycle every metric weight is 1, so in the chosen
--     bases the star is the identity matrix;
--   * `star * star = 1`, symmetry and isometry of the star;
--   * the Green identity `<d u, v> = <u, delta v>`, i.e. `delta` is the
--     formal adjoint of `d`;
--   * the Hodge Laplacians `Delta_0 = delta d` and `Delta_1 = d delta`;
--   * explicit 3x3 matrices, vanishing determinant, and `Delta_0 = Delta_1`
--     on the 3-cycle.
--
-- Claim limits:
--   * this is not the Hodge star of a continuum Riemannian manifold;
--   * the star is the identity because the lattice metric is flat and
--     unit-spaced; no metric-dependent star is claimed;
--   * `delta` is the l2 adjoint `d^T`; this file does not claim the continuum
--     formula `delta = +/- star d star` for a nontrivial metric;
--   * no elliptic theory and no spectral theorem; the Hodge decomposition is
--     stated separately in `DiscreteHodgeDecomposition.lean`.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteHodgeStar

variable {n : ℕ} [NeZero n]

/-- Forward difference on the cyclic lattice, as an `n x n` integer matrix. -/
def discreteGrad (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- Formal adjoint of the forward difference: the transpose matrix. -/
def discreteDiv (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n)ᵀ

/-- Hodge star on 0-cochains: the metric identification with 1-cochains.
    The unit-spacing cycle has trivial metric weights, so this is the identity. -/
def hodgeStar0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  1

/-- Hodge star on 1-cochains: the inverse metric identification with
    0-cochains, again the identity for the unit-spacing cycle. -/
def hodgeStar1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  1

/-- Laplacian on 0-cochains: `Delta_0 = delta d`. -/
def laplacian0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteDiv n) * (discreteGrad n)

/-- Laplacian on 1-cochains: `Delta_1 = d delta`. -/
def laplacian1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n) * (discreteDiv n)

/-- The Hodge star on 0-cochains is an involution. -/
theorem hodgeStar0_involution (n : ℕ) [NeZero n] :
    (hodgeStar0 n) * (hodgeStar0 n) = (1 : Matrix (Fin n) (Fin n) ℤ) := by
  simp [hodgeStar0]

/-- The Hodge star on 1-cochains is an involution. -/
theorem hodgeStar1_involution (n : ℕ) [NeZero n] :
    (hodgeStar1 n) * (hodgeStar1 n) = (1 : Matrix (Fin n) (Fin n) ℤ) := by
  simp [hodgeStar1]

/-- The Hodge star on 0-cochains is symmetric. -/
theorem hodgeStar0_symmetric (n : ℕ) [NeZero n] :
    (hodgeStar0 n)ᵀ = hodgeStar0 n := by
  simp [hodgeStar0]

/-- The Hodge star on 1-cochains is symmetric. -/
theorem hodgeStar1_symmetric (n : ℕ) [NeZero n] :
    (hodgeStar1 n)ᵀ = hodgeStar1 n := by
  simp [hodgeStar1]

/-- The Hodge star on 0-cochains preserves the cochain inner product. -/
theorem hodgeStar0_isometry (n : ℕ) [NeZero n] (u v : Fin n → ℤ) :
    dotProduct (hodgeStar0 n *ᵥ u) (hodgeStar0 n *ᵥ v) = dotProduct u v := by
  simp [hodgeStar0]

/-- The Hodge star on 1-cochains preserves the cochain inner product. -/
theorem hodgeStar1_isometry (n : ℕ) [NeZero n] (u v : Fin n → ℤ) :
    dotProduct (hodgeStar1 n *ᵥ u) (hodgeStar1 n *ᵥ v) = dotProduct u v := by
  simp [hodgeStar1]

/-- Green identity: `delta = d^T` is the formal adjoint of `d`. -/
theorem green_identity (n : ℕ) [NeZero n] (u v : Fin n → ℤ) :
    dotProduct (discreteGrad n *ᵥ u) v =
      dotProduct u (discreteDiv n *ᵥ v) := by
  rw [dotProduct_comm (discreteGrad n *ᵥ u) v]
  rw [← Matrix.dotProduct_transpose_mulVec]
  rfl

/-- `Delta_0` is symmetric. -/
theorem laplacian0_symmetric (n : ℕ) [NeZero n] :
    (laplacian0 n)ᵀ = laplacian0 n := by
  dsimp [laplacian0, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- `Delta_1` is symmetric. -/
theorem laplacian1_symmetric (n : ℕ) [NeZero n] :
    (laplacian1 n)ᵀ = laplacian1 n := by
  dsimp [laplacian1, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- The 3x3 matrix of `Delta_0` on the 3-cycle. -/
theorem laplacian0_3_eq :
    laplacian0 3 = !![2, -1, -1; -1, 2, -1; -1, -1, 2] := by
  ext i j
  fin_cases i <;> fin_cases j <;> decide

/-- The 3x3 matrix of `Delta_1` on the 3-cycle. -/
theorem laplacian1_3_eq :
    laplacian1 3 = !![2, -1, -1; -1, 2, -1; -1, -1, 2] := by
  ext i j
  fin_cases i <;> fin_cases j <;> decide

/-- The 3x3 `Delta_0` is singular, as expected for a Laplacian. -/
theorem laplacian0_3_det : (laplacian0 3).det = 0 := by
  rw [laplacian0_3_eq]
  decide

/-- The 3x3 `Delta_1` is singular, as expected for a Laplacian. -/
theorem laplacian1_3_det : (laplacian1 3).det = 0 := by
  rw [laplacian1_3_eq]
  decide

/-- On the 3-cycle the 0-form and 1-form Laplacians coincide. -/
theorem laplacian0_3_eq_laplacian1_3 :
    laplacian0 3 = laplacian1 3 := by
  rw [laplacian0_3_eq, laplacian1_3_eq]

/-- Hodge duality on the 3-cycle: conjugation by the star identifies
    `Delta_0` with `Delta_1`. The star is the identity and the two Laplacians
    are equal on the cycle, so the identity reduces to that equality. -/
theorem hodge_star_duality_3 :
    hodgeStar1 3 * laplacian0 3 * hodgeStar0 3 = laplacian1 3 := by
  simp [hodgeStar0, hodgeStar1, laplacian0_3_eq_laplacian1_3]

end Math30.Topology.DiscreteHodgeStar
