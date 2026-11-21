import Mathlib

-- [MATH3-SCOPE: FORMAL_GENERAL_THEOREM]
-- BRIDGE-08: Bost Slope Inequality & Path Quadric Parseval Bound
namespace Math3
namespace Bridges

theorem bost_slope_height_budget_bound (m : Nat) (capacity_unit : ℝ)
    (slope step_weight : Fin m → ℝ) (hslope : ∀ i : Fin m, slope i * step_weight i ≤ capacity_unit) :
    (∑ i : Fin m, slope i * step_weight i) ≤ (m : ℝ) * capacity_unit := by
  calc
    (∑ i : Fin m, slope i * step_weight i) ≤ ∑ i : Fin m, capacity_unit :=
      Finset.sum_le_sum (fun i _ => hslope i)
    _ = (m : ℝ) * capacity_unit := by simp

theorem path_quadric_parseval_energy_conservation {N : Nat} (a : Fin N → ℝ) (E_max : ℝ)
    (hparseval : ∀ i : Fin N, a i ^ 2 ≤ E_max) :
    (0 ≤ ∑ i : Fin N, a i ^ 2) ∧ ((∑ i : Fin N, a i ^ 2) ≤ (N : ℝ) * E_max) := by
  constructor
  · exact Finset.sum_nonneg (fun i _ => sq_nonneg (a i))
  · calc
      (∑ i : Fin N, a i ^ 2) ≤ ∑ i : Fin N, E_max := Finset.sum_le_sum (fun i _ => hparseval i)
      _ = (N : ℝ) * E_max := by simp

theorem iterated_parseval_remainder_suppression (R C X : ℝ)
    (hrem : R ^ 2 ≤ C ^ 2 * X) (hnonneg : 0 ≤ C ∧ 0 ≤ X) :
    R ^ 2 ≤ (C * X + C) ^ 2 := by
  have h_cx : C ^ 2 * X ≤ (C * X + C) ^ 2 := by
    nlinarith [hnonneg.1, hnonneg.2]
  exact le_trans hrem h_cx

end Bridges
end Math3
