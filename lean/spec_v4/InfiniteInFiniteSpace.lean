/-
Copyright (c) 2026 Math 3.0 Sovereign Lattice. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Math 3.0 Omega Autonomous Auditor & Evolutionary Engine
-/

import Mathlib.Data.Nat.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic

/-!
# Infinite in Finite Space: Bounded Finite Certificates

Formalizes honest, bounded finite statements for the "Infinite in Finite Space"
research program. Every theorem here is a FORMAL_FINITE_THEOREM: a finite
cardinality, growth, or measure-counting bound. No claim is made about actual
uncountable infinity in ZFC, about continuum measure theory, or about the truth
of any full conjecture.

## Interpretations covered (bounded forms)

1. **Hilbert hotel**: no injection `Fin (N+1) → Fin N` (pigeonhole).
2. **Bounded ascent**: no strictly increasing trajectory in `Fin (C+1)`.
3. **Cantor**: at level n there are `2^n` intervals; the retained fraction
   shrinks strictly at every step and stays below any `2^{-m}` for large enough n.
4. **Koch snowflake**: segment count `3·4^n` is unbounded; added area is
   bounded by a convergent geometric series (rational arithmetic).
5. **Space-filling grid**: `4^n` cells cannot inject into `2^n` positions.
6. **Landauer**: with per-bit cost ≥ 1, `bits·cost ≤ energy → bits ≤ energy`.
7. **Cantor diagonal (finite form)**: `2^n` states cannot be covered by n states.

All facts are elementary; no external citation is required for the finite
statements themselves. Scope discipline: these do **not** establish any claim
about the continuum, measure-zero sets, or Turing completeness.

Scope: finite cardinality, growth and rational-counting bounds only; full
conjectures remain open and no continuum or Turing-completeness claim is made.

No placeholders; no `sorry`, `admit`, `axiom`, `constant`, `opaque`,
`partial def`, `native_decide`, `implemented_by`, or `extern`.
-/

namespace Math30.InfiniteInFinite

/-! ## 1. Hilbert hotel / pigeonhole -/

/-- No injective map from a larger finite type into a smaller one. -/
theorem hilbert_hotel_no_injection (N : ℕ) :
    ¬ ∃ f : Fin (N + 1) → Fin N, Function.Injective f := by
  rintro ⟨f, hf⟩
  have hcard := Fintype.card_le_of_injective f hf
  simp at hcard

/-- Generalized pigeonhole: if `n < m`, no injection `Fin m → Fin n`. -/
theorem pigeonhole_finite (m n : ℕ) (h : n < m) :
    ¬ ∃ f : Fin m → Fin n, Function.Injective f := by
  rintro ⟨f, hf⟩
  have hcard := Fintype.card_le_of_injective f hf
  rw [Fintype.card_fin, Fintype.card_fin] at hcard
  exact (not_le_of_gt h) hcard

/-! ## 2. Basic growth lemmas -/

/-- Every natural is smaller than `2^n`. -/
theorem lt_two_pow_self (n : ℕ) : n < 2 ^ n := by
  induction n with
  | zero => norm_num
  | succ k ih =>
    rw [pow_succ]
    have hp : 0 < 2 ^ k := by positivity
    omega

/-- Strict monotonicity of base powers for positive exponent. -/
theorem pow_strict (a b n : ℕ) (hab : a < b) (hn : 0 < n) :
    a ^ n < b ^ n := by
  obtain ⟨k, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hn)
  clear hn
  induction k with
  | zero => simpa using hab
  | succ j ih =>
    rw [pow_succ, pow_succ]
    have hbpos : 0 < b := by omega
    exact lt_of_le_of_lt (Nat.mul_le_mul_right a (le_of_lt ih))
      (Nat.mul_lt_mul_of_pos_left hab (pow_pos hbpos (j + 1)))

/-! ## 3. Bounded ascent in a finite lattice -/

/-- A strictly increasing trajectory in `Fin (C+1)` cannot exist. -/
theorem bounded_ascent_contradiction (C : ℕ) (f : ℕ → Fin (C + 1)) :
    ¬ (∀ i, (f i).val < (f (i + 1)).val) := by
  intro h
  have hstep : ∀ k : ℕ, (f 0).val + k ≤ (f k).val := by
    intro k
    induction k with
    | zero => simp
    | succ k ih =>
      have hk := h k
      omega
  have hC := hstep (C + 1)
  have hb := (f (C + 1)).isLt
  omega

/-! ## 4. Cantor approximation (finite counting) -/

/-- Level n of the Cantor approximation has `2^n > 0` intervals. -/
theorem cantor_intervals_count (n : ℕ) : 0 < 2 ^ n := by
  positivity

/-- The interval count doubles at each step. -/
theorem cantor_intervals_double (n : ℕ) : 2 ^ (n + 1) = 2 * 2 ^ n := by
  rw [pow_succ]
  omega

/-- The retained length fraction `2^n / 3^n` strictly decreases at each step. -/
theorem cantor_measure_shrinks (n : ℕ) :
    2 ^ (n + 1) * 3 ^ n < 3 ^ (n + 1) * 2 ^ n := by
  rw [pow_succ, pow_succ]
  have hpos : 0 < 2 ^ n * 3 ^ n := by positivity
  nlinarith

/-- For any `m`, the retained fraction falls below `1 / 2^m` at level `2·m + 1`.
    Finite form: `2^(2m+1) · 2^m < 3^(2m+1)`. -/
theorem cantor_measure_small (m : ℕ) :
    2 ^ (2 * m + 1) * 2 ^ m < 3 ^ (2 * m + 1) := by
  rw [← pow_add]
  have hleft : 2 ^ (2 * m + 1 + m) = 2 * 8 ^ m := by
    have hidx : 2 * m + 1 + m = 1 + 3 * m := by omega
    rw [hidx, pow_add, pow_mul]
    norm_num
  have hright : 3 ^ (2 * m + 1) = 3 * 9 ^ m := by
    have hidx : 2 * m + 1 = 1 + 2 * m := by omega
    rw [hidx, pow_add, pow_mul]
    norm_num
  rw [hleft, hright]
  have h89 : 8 ^ m ≤ 9 ^ m := by
    exact Nat.pow_le_pow_left (by norm_num) m
  have hpos8 : 0 < 8 ^ m := by positivity
  nlinarith

/-! ## 5. Koch snowflake (finite / rational counting) -/

/-- Segment count at level n is `3·4^n`, which is positive. -/
theorem koch_segments_positive (n : ℕ) : 0 < 3 * 4 ^ n := by
  positivity

/-- The perimeter segment count is unbounded: for every M, some level exceeds M. -/
theorem koch_perimeter_unbounded (M : ℕ) : ∃ n : ℕ, M < 3 * 4 ^ n := by
  refine ⟨M + 1, ?_⟩
  have h1 : M + 1 < 2 ^ (M + 1) := lt_two_pow_self (M + 1)
  have h2 : 2 ^ (M + 1) ≤ 4 ^ (M + 1) := by
    exact Nat.pow_le_pow_left (by norm_num) (M + 1)
  have hpos : 0 < 4 ^ (M + 1) := by positivity
  nlinarith

/-- Added area at each step, as a rational: step k adds `(1/3)·(4/9)^k`. -/
def addedArea : ℕ → ℚ
  | 0 => 0
  | n + 1 => addedArea n + (1 / 3 : ℚ) * (4 / 9 : ℚ) ^ n

/-- Strong bound: `addedArea n ≤ 1 - (4/9)^n`. -/
theorem addedArea_le (n : ℕ) : addedArea n ≤ 1 - (4 / 9 : ℚ) ^ n := by
  induction n with
  | zero => norm_num [addedArea]
  | succ k ih =>
    rw [addedArea]
    have hpow_nonneg : 0 ≤ (4 / 9 : ℚ) ^ k := by positivity
    have hcoef : (4 / 9 : ℚ) ≤ (2 / 3 : ℚ) := by norm_num
    have hpow_succ : (4 / 9 : ℚ) ^ (k + 1) = (4 / 9 : ℚ) ^ k * (4 / 9 : ℚ) := by
      rw [pow_succ]
    have hstep : (4 / 9 : ℚ) ^ (k + 1) ≤ (2 / 3 : ℚ) * (4 / 9 : ℚ) ^ k := by
      rw [hpow_succ]
      nlinarith
    nlinarith

/-- The added area never reaches 1, so total area is bounded. -/
theorem addedArea_lt_one (n : ℕ) : addedArea n < 1 := by
  have h := addedArea_le n
  have hpos : 0 < (4 / 9 : ℚ) ^ n := by positivity
  linarith

/-! ## 6. Space-filling grid (pigeonhole) -/

/-- A `4^n`-cell grid cannot inject into `2^n` positions for `n > 0`. -/
theorem grid_pigeonhole (n : ℕ) (hn : 0 < n) :
    ¬ ∃ f : Fin (4 ^ n) → Fin (2 ^ n), Function.Injective f := by
  apply pigeonhole_finite (4 ^ n) (2 ^ n)
  exact pow_strict 2 4 n (by norm_num) hn

/-! ## 7. Landauer / finite capacity -/

/-- Landauer bound: per-bit cost ≥ 1 forces `bits ≤ energy`. -/
theorem landauer_bound (bits cost energy : ℕ) (hc : 1 ≤ cost)
    (h : bits * cost ≤ energy) : bits ≤ energy := by
  have hb : bits ≤ bits * cost := by
    have hmul := Nat.mul_le_mul_left bits hc
    simpa using hmul
  exact le_trans hb h

/-- A capacity of `C` bits admits `2^C` states. -/
theorem finite_capacity (C : ℕ) : Fintype.card (Fin (2 ^ C)) = 2 ^ C := by
  simp

/-! ## 8. Cantor diagonal (finite form) -/

/-- `2^n` states cannot be covered by only `n` states: no surjection
    `Fin n → Fin (2^n)`. Holds for every `n`, including `n = 0`. -/
theorem no_surjection_finite (n : ℕ) :
    ¬ ∃ f : Fin n → Fin (2 ^ n), Function.Surjective f := by
  rintro ⟨f, hf⟩
  have hcard := Fintype.card_le_of_surjective f hf
  rw [Fintype.card_fin, Fintype.card_fin] at hcard
  have hlt : n < 2 ^ n := lt_two_pow_self n
  omega

/-! ## 9. Mutation-testing targets -/

theorem hilbert_hotel_no_injection_mut (N : ℕ) :
    ¬ ∃ f : Fin (N + 1) → Fin N, Function.Injective f := by
  exact hilbert_hotel_no_injection N

theorem bounded_ascent_contradiction_mut (C : ℕ) (f : ℕ → Fin (C + 1)) :
    ¬ (∀ i, (f i).val < (f (i + 1)).val) := by
  exact bounded_ascent_contradiction C f

theorem cantor_measure_shrinks_mut (n : ℕ) :
    2 ^ (n + 1) * 3 ^ n < 3 ^ (n + 1) * 2 ^ n := by
  exact cantor_measure_shrinks n

theorem koch_perimeter_unbounded_mut (M : ℕ) : ∃ n : ℕ, M < 3 * 4 ^ n := by
  exact koch_perimeter_unbounded M

theorem addedArea_lt_one_mut (n : ℕ) : addedArea n < 1 := by
  exact addedArea_lt_one n

theorem landauer_bound_mut (bits cost energy : ℕ) (hc : 1 ≤ cost)
    (h : bits * cost ≤ energy) : bits ≤ energy := by
  exact landauer_bound bits cost energy hc h

#eval "InfiniteInFiniteSpace module compiled with zero placeholders."

end Math30.InfiniteInFinite