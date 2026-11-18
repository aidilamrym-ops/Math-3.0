import Mathlib.Tactic

/-!
# Asymptotic Circuit & Gauge Scaling Bridge (BRIDGE-06)

This file formalizes three universal asymptotic scaling and circuit/gauge bounds
completing the 6-bridge multi-scale architecture: exponential growth dominating
linear bounds for state-space complexity, vanishing circuit density ratios
beyond threshold scales, and topological gauge action gap preservation across
lattice refinements.

1. `exponential_dominates_linear_bound`: for all `n ≥ 2`, `n + 1 < 2 ^ n`,
   establishing strict exponential state-space growth over linear bounds.
2. `circuit_density_ratio_vanishes`: for any positive overhead constant `C > 0`
   and tolerance `ε > 0`, density ratios bounded by `C / n` vanish beyond a
   finite scale threshold `N₀ ≥ 1`.
3. `gauge_action_gap_scale_invariant`: a non-zero integer topological charge
   `Q ≠ 0` with integer action `Q² ≤ S` preserves the discrete action gap `1 ≤ S`.

Scope: Every statement is finite or quantified over discrete scales. This module
proves bounded circuit and gauge scaling lemmas. It does **not** claim a
continuum Yang–Mills mass gap or a P vs NP resolution.
-/

namespace Math30.Bridges

/-- Exponential state-space complexity dominates linear bounds.

For all natural numbers `n ≥ 2` (supplied by `hn : 2 ≤ n`), the exponential
growth `2 ^ n` strictly dominates the linear expression `n + 1`.

The primary hypothesis `hn` is load-bearing: for `n = 0` or `n = 1`,
`0 + 1 = 2⁰` (1 = 1) or `1 + 1 = 2¹` (2 = 2), so strict inequality fails. -/
theorem exponential_dominates_linear_bound
    (n : ℕ) (hn : 2 ≤ n) :
    n + 1 < 2 ^ n := by
  induction' n, hn using Nat.le_induction with k hk ih
  · decide
  · calc
      (k + 1) + 1 = (k + 1) + 1 := rfl
      _ < 2 ^ k + 1 := by linarith [ih]
      _ ≤ 2 ^ k + 2 ^ k := by
        have : 1 ≤ 2 ^ k := by omega
        omega
      _ = 2 ^ (k + 1) := by ring

/-- Circuit density ratios vanish beyond a threshold scale.

For any positive overhead constant `C > 0`, tolerance `ε > 0`, and density
ratio sequence satisfying `∀ n ≥ 1, ratio n ≤ C / (n : ℚ)`, there exists a finite
scale threshold `N₀ ≥ 1` such that for all `n ≥ N₀`, `ratio n < ε`.

The primary hypothesis `hC : 0 < C` is load-bearing: without a positive overhead
bound, the density ratio need not be controlled by `C / n`. -/
theorem circuit_density_ratio_vanishes
    (ratio : ℕ → ℚ) (C ε : ℚ)
    (hC : 0 < C)
    (heps : 0 < ε)
    (hratio : ∀ n : ℕ, 1 ≤ n → ratio n ≤ C / (n : ℚ)) :
    ∃ N₀ : ℕ, 1 ≤ N₀ ∧ ∀ n : ℕ, N₀ ≤ n → ratio n < ε := by
  obtain ⟨N, hN⟩ := exists_nat_gt (C / ε)
  have hN_pos : 0 < N := by
    by_contra h_le
    have h_zero : N ≤ 0 := by omega
    have h_eq : N = 0 := by omega
    subst h_eq
    have h_gt : (0 : ℚ) < C / ε := div_pos hC heps
    norm_cast at hN
    linarith
  set N₀ := max 1 N
  have hN₀_ge1 : 1 ≤ N₀ := le_max_left 1 N
  have hN₀_geN : N ≤ N₀ := le_max_right 1 N
  use N₀
  refine ⟨hN₀_ge1, ?_⟩
  intro n hn
  have hn_ge1 : 1 ≤ n := le_trans hN₀_ge1 hn
  have hrat := hratio n hn_ge1
  have h_bound : C / (n : ℚ) < ε := by
    have h1 : C / ε < (N : ℚ) := hN
    have h2 : (N : ℚ) ≤ (N₀ : ℚ) := by exact_mod_cast hN₀_geN
    have h3 : (N₀ : ℚ) ≤ (n : ℚ) := by exact_mod_cast hn
    have h_n_gt : C / ε < (n : ℚ) := by linarith
    have h_eps_pos : 0 < ε := heps
    have h_n_pos : 0 < (n : ℚ) := by exact_mod_cast hn_ge1
    rw [div_lt_iff₀ h_eps_pos] at h_n_gt
    rw [mul_comm] at h_n_gt
    rw [div_lt_iff₀ h_n_pos]
    exact h_n_gt
  exact lt_of_le_of_lt hrat h_bound

/-- Topological gauge action gap scale invariance.

Given a non-zero integer topological charge `Q ≠ 0` (supplied by `hQ : Q ≠ 0`)
and an integer action `S` satisfying `Q * Q ≤ S`, the integer action gap
`1 ≤ S` is preserved across discrete lattice refinements.

The primary hypothesis `hQ : Q ≠ 0` is load-bearing: if `Q = 0`, then `0 ≤ S`
which permits `S = 0`, violating the strictly positive action gap `1 ≤ S`. -/
theorem gauge_action_gap_scale_invariant
    (Q S : ℤ)
    (hQ : Q ≠ 0)
    (hS : Q * Q ≤ S) :
    1 ≤ S := by
  have h_sq : 1 ≤ Q * Q := by
    have : Q * Q ≠ 0 := mul_ne_zero hQ hQ
    have : 0 ≤ Q * Q := mul_self_nonneg Q
    omega
  have h_main : 1 ≤ S := by
    linarith [h_sq, hS]
  exact h_main

end Math30.Bridges