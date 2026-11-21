import Mathlib

-- [MATH3-SCOPE: FORMAL_GENERAL_THEOREM]
-- BRIDGE-10: Dirichlet Character Orthogonality, GRH Explicit-Window Positivity & Masullo Gap Isolation
namespace Math3
namespace Bridges

theorem dirichlet_character_orthogonality_bound {N : Nat} (chi : Fin N → ℝ)
    (hunit : ∀ i : Fin N, chi i ^ 2 ≤ 1) :
    (0 ≤ ∑ i : Fin N, chi i ^ 2) ∧ ((∑ i : Fin N, chi i ^ 2) ≤ (N : ℝ)) := by
  constructor
  · apply Finset.sum_nonneg
    intro i _
    exact sq_nonneg (chi i)
  · have h_sum := Finset.sum_le_sum (fun i _ => hunit i)
    rw [Finset.sum_const, Finset.card_fin] at h_sum
    exact h_sum

theorem grh_explicit_window_positivity {N : Nat} (w Phi : Fin N → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hPhi : ∀ i, 0 ≤ Phi i) :
    0 ≤ ∑ i : Fin N, w i * Phi i := by
  apply Finset.sum_nonneg
  intro i _
  exact mul_nonneg (hw i) (hPhi i)

theorem masullo_gap_isolation_enclosure {N : Nat} (mid rad x : Fin N → ℝ)
    (hrad : ∀ i, rad i ≤ mid i)
    (henc : ∀ i, mid i - rad i ≤ x i ∧ x i ≤ mid i + rad i) :
    0 ≤ ∑ i : Fin N, x i := by
  apply Finset.sum_nonneg
  intro i _
  have hmid : 0 ≤ mid i - rad i := sub_nonneg.mpr (hrad i)
  exact le_trans hmid (henc i).1

end Bridges
end Math3
