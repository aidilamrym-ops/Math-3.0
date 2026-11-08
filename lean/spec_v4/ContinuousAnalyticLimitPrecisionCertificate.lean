-- ContinuousAnalyticLimitPrecisionCertificate.lean (Hardened v7 - Fully Verified)
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Tactic

namespace Math30.SpecV4

theorem continuous_analytic_limit_zero_error 
  (a b : ℝ) (h_lt : a < b) :
  ∀ (epsilon : ℝ), 0 < epsilon → ∃ (N : ℕ), 0 < N ∧ (b - a) / (N : ℝ) < epsilon := by
  intros epsilon h_eps
  have h_diff_pos : 0 < b - a := sub_pos.mpr h_lt
  rcases exists_nat_gt ((b - a) / epsilon) with ⟨N, hN⟩
  have hN_pos : 0 < (N : ℝ) := by
    calc 0 < (b - a) / epsilon := div_pos h_diff_pos h_eps
         _ < N := hN
  have hN_nat_pos : 0 < N := Nat.cast_pos.mp hN_pos
  refine ⟨N, hN_nat_pos, ?_⟩
  rw [div_lt_iff₀ hN_pos]
  have h_mul := (div_lt_iff₀ h_eps).mp hN
  linarith

end Math30.SpecV4
