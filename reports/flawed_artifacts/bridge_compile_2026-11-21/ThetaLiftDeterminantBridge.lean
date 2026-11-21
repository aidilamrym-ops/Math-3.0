import Mathlib

-- [MATH3-SCOPE: FORMAL_GENERAL_THEOREM]
-- BRIDGE-07: Theta-Lift Determinant Bridge
namespace Math3
namespace Bridges

theorem finite_theta_chain_truncation_bound (m : Nat) (B : ℝ) (capacity_unit : ℝ)
    (step_cost : Fin m → ℝ) (hcost : ∀ i : Fin m, step_cost i ≤ B) :
    (∑ i : Fin m, step_cost i) ≤ (m : ℝ) * B := by
  apply Finset.sum_le_sum
  intro i _
  exact hcost i

theorem interlacing_determinant_positivity {N : Nat} (w Phi : Fin N → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hPhi : ∀ i, 0 ≤ Phi i) :
    0 ≤ ∑ i : Fin N, w i * Phi i := by
  apply Finset.sum_nonneg
  intro i _
  exact mul_nonneg (hw i) (hPhi i)

theorem theta_lift_interval_containment {N : Nat} (mid rad x : Fin N → ℝ)
    (hrad : ∀ i, rad i ≤ mid i) (henc : ∀ i, mid i - rad i ≤ x i) :
    0 ≤ ∑ i : Fin N, x i := by
  apply Finset.sum_nonneg
  intro i _
  have hmid : 0 ≤ mid i - rad i := sub_nonneg.mpr (hrad i)
  exact le_trans hmid (henc i)

end Bridges
end Math3
