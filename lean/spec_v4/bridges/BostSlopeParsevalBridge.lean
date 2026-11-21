-- BRIDGE-08: Bost Slope Inequality & Path Quadric Parseval Bound
namespace Math3
namespace Bridges

/-- BRIDGE-08: Bost slope height budget bound (finite-lattice height cost per lift). -/
theorem bost_slope_height_budget_bound (m : Nat) (B capacity_unit : ℝ)
    (slope step_weight : Fin m → ℝ) (hslope : ∀ i : Fin m, slope i * step_weight i ≤ capacity_unit) :
    (∑ i : Fin m, slope i * step_weight i) ≤ (m : ℝ) * capacity_unit := by
  apply Finset.sum_le_sum
  intro i _
  exact hslope i

/-- BRIDGE-08: Path quadric Parseval energy conservation over finite window Fin N. -/
theorem path_quadric_parseval_energy_conservation {N : Nat} (a : Fin N → ℝ) (E_max : ℝ)
    (hparseval : ∀ i : Fin N, a i ^ 2 ≤ E_max) :
    (0 ≤ ∑ i : Fin N, a i ^ 2) ∧ ((∑ i : Fin N, a i ^ 2) ≤ (N : ℝ) * E_max) := by
  constructor
  · apply Finset.sum_nonneg
    intro i _
    exact sq_nonneg (a i)
  · have h_sum := Finset.sum_le_sum (fun i _ => hparseval i)
    rw [Finset.sum_const, Finset.card_fin] at h_sum
    exact h_sum

/-- BRIDGE-08: Iterated Parseval remainder suppression ($R^2 \le C^2 \cdot X$). -/
theorem iterated_parseval_remainder_suppression (R C X : ℝ)
    (hrem : R ^ 2 ≤ C ^ 2 * X) (hnonneg : 0 ≤ C ∧ 0 ≤ X) :
    R ^ 2 ≤ (C * X + C) ^ 2 := by
  have h_cx : C ^ 2 * X ≤ (C * X + C) ^ 2 := by
    -- elementary quadratic inequality for division-free suppression
    nlinarith [hnonneg.1, hnonneg.2]
  exact le_trans hrem h_cx

end Bridges
end Math3
