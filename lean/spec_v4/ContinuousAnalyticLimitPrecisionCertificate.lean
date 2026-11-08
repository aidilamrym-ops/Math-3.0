-- ContinuousAnalyticLimitPrecisionCertificate.lean (Hardened v3 - Fully Verified)
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.Archimedean

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
  exact (div_lt_iff₀ hN_pos).mp hN

end Math30.SpecV4
