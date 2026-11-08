import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.Field.Basic

namespace Math30.Core.Certificate

/-- Definition of the analytical rational expression for DIBD invariant. -/
def DiscreteInertiaBoundaryDeterminant (det_τ : ℝ) (norm_sq_τ : ℝ) : ℝ :=
  abs det_τ / (norm_sq_τ + abs det_τ + 1)

/-- Universal parametric DIBD invariant theorem. -/
theorem universal_dibd_invariant (det_τ : ℝ) (norm_sq_τ : ℝ) (h_norm : norm_sq_τ ≥ 0) :
    DiscreteInertiaBoundaryDeterminant det_τ norm_sq_τ < 1 := by
  dsimp [DiscreteInertiaBoundaryDeterminant]
  have h_denom : 0 < norm_sq_τ + abs det_τ + 1 := by
    apply add_pos_of_nonneg_of_pos
    · apply add_nonneg h_norm (abs_nonneg det_τ)
    · norm_num
  apply div_lt_one_of_lt
  · exact h_denom
  · linarith [h_norm, abs_nonneg det_τ]

end Math30.Core.Certificate
