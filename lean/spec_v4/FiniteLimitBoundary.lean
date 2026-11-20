/-
Copyright (c) 2026 Math 3.0 Sovereign Lattice. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Math 3.0 Omega Autonomous Auditor & Evolutionary Engine
-/

import Mathlib.Data.Nat.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic

/-!
# Finite Limit Boundary: Discrete Bounded Limit Certificates

This module formalizes the finite core of "infinite in finite space".  Every
result is a FORMAL_FINITE_THEOREM about explicit finite data: rational numbers,
natural numbers, finite types, and finite sums.  No topology, no measure theory,
no completeness axiom, and no completed infinity is used anywhere.

The certificate has five layers:

1. **Finite geometric ledger.**  The partial sums of `(1/2)^k` are computed
   exactly and bounded by `2`.

2. **Two-sided telescoping.**  A sequence whose increments are bounded above
   (respectively below) obeys the explicit linear bound `N * d`.

3. **Finite limit boundary.**  A rational sequence whose `k`-th increment is
   squeezed between `±M / 2^k` is trapped in the fixed interval
   `[a 0 - 2M, a 0 + 2M]`, and every tail `i, i+1, i+2, ...` has diameter at
   most `2M / 2^i`.  Thus the whole infinite-looking process is certified by a
   finite rational interval.

4. **Unbounded recurrence in a finite state space.**  Any sequence into `Fin K`
   repeats arbitrarily late: for every `N` there are `N ≤ i < j` with
   `f i = f j`.  For a deterministic self-map of `Fin K`, the orbit is
   eventually periodic.  These are exact finite counterparts of accumulation
   points, with no appeal to compactness.

5. **Descent and grid barriers.**  There is no infinite strictly descending
   sequence in `ℕ`; a bounded-denominator rational grid sequence repeats
   arbitrarily late.  The latter is the finite-space accumulation theorem:
   bounded rational data with bounded denominators cannot encode an infinite
   set of distinct values.

Scope: finite rational/natural bounds and finite-state recurrence only.  The
module does NOT claim analytic convergence, a limit object in `ℝ`, compactness
of a continuum, or any topological theorem.  `ℚ` is used only as an ordered
field of explicit fractions.

No placeholders; no `sorry`, `admit`, `axiom`, `constant`, `opaque`,
`partial def`, `native_decide`, `implemented_by`, or `extern`.
-/

namespace Math30.FiniteLimitBoundary

open Finset
open scoped BigOperators

/-! ## 1. Finite geometric ledger -/

/-- Exact finite geometric sum: `∑_{k<N} (1/2)^k = 2 - 2·(1/2)^N`. -/
theorem geom_half_sum (N : ℕ) :
    (∑ k ∈ Finset.range N, (1 / 2 : ℚ) ^ k) = 2 - 2 * (1 / 2) ^ N := by
  induction N with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, ih, pow_succ]
    ring

/-- The finite geometric ledger never exceeds `2`. -/
theorem geom_half_sum_le_two (N : ℕ) :
    (∑ k ∈ Finset.range N, (1 / 2 : ℚ) ^ k) ≤ 2 := by
  rw [geom_half_sum N]
  have h : (0 : ℚ) ≤ 2 * (1 / 2) ^ N := by positivity
  linarith

/-- Every power of `1/2` is at most one. -/
theorem geom_half_pow_le_one (n : ℕ) : (1 / 2 : ℚ) ^ n ≤ 1 := by
  induction n with
  | zero => norm_num
  | succ k ih =>
    rw [pow_succ]
    have h0 : (0 : ℚ) ≤ (1 / 2) ^ k := pow_nonneg (by norm_num) k
    nlinarith

/-! ## 2. Two-sided finite telescoping -/

/-- Finite upper telescoping bound: increments bounded above by `d` give
    `a N - a 0 ≤ N * d`.  No positivity of `d` is needed. -/
theorem finite_telescope_bound (a : ℕ → ℚ) (d : ℚ)
    (hstep : ∀ k, a (k + 1) - a k ≤ d) (N : ℕ) :
    a N - a 0 ≤ N * d := by
  induction N with
  | zero => simp
  | succ k ih =>
    have h := hstep k
    have hcast : ((k + 1 : ℕ) : ℚ) * d = d + k * d := by
      push_cast
      ring
    linarith

/-- Finite lower telescoping bound: increments bounded below by `-d` give
    `-(N * d) ≤ a N - a 0`. -/
theorem finite_telescope_bound_lower (a : ℕ → ℚ) (d : ℚ)
    (hstep : ∀ k, -d ≤ a (k + 1) - a k) (N : ℕ) :
    -((N : ℚ) * d) ≤ a N - a 0 := by
  induction N with
  | zero => simp
  | succ k ih =>
    have h := hstep k
    have hcast : ((k + 1 : ℕ) : ℚ) * d = d + k * d := by
      push_cast
      ring
    linarith

/-- Two-sided finite oscillation bound, packaged as a conjunction. -/
theorem finite_oscillation_bound (a : ℕ → ℚ) (d : ℚ)
    (hlo : ∀ k, -d ≤ a (k + 1) - a k)
    (hhi : ∀ k, a (k + 1) - a k ≤ d) (N : ℕ) :
    -((N : ℚ) * d) ≤ a N - a 0 ∧ a N - a 0 ≤ N * d :=
  ⟨finite_telescope_bound_lower a d hlo N, finite_telescope_bound a d hhi N⟩

/-! ## 3. Finite limit boundary: geometric squeezing -/

/-- If each increment of `a` is squeezed between `±M / 2^k`, then every term
    stays within `2M` of the initial term.  This is a purely finite rational
    certificate for the boundedness of a contractive limit process. -/
theorem geometric_step_bound (a : ℕ → ℚ) (M : ℚ) (hM : 0 ≤ M)
    (hstep : ∀ k, -(M * (1 / 2 : ℚ) ^ k) ≤ a (k + 1) - a k ∧
      a (k + 1) - a k ≤ M * (1 / 2 : ℚ) ^ k) (N : ℕ) :
    -(2 * M) ≤ a N - a 0 ∧ a N - a 0 ≤ 2 * M := by
  have hbound : ∀ N, -(∑ k ∈ Finset.range N, M * (1 / 2 : ℚ) ^ k) ≤
      a N - a 0 ∧
      a N - a 0 ≤ ∑ k ∈ Finset.range N, M * (1 / 2 : ℚ) ^ k := by
    intro N
    induction N with
    | zero => simp
    | succ k ih =>
      obtain ⟨hlo, hhi⟩ := hstep k
      obtain ⟨ihlo, ihhi⟩ := ih
      have e : a (k + 1) - a 0 = (a (k + 1) - a k) + (a k - a 0) := by ring
      rw [e, Finset.sum_range_succ]
      constructor <;> linarith
  have hsum : (∑ k ∈ Finset.range N, M * (1 / 2 : ℚ) ^ k) ≤ 2 * M := by
    have h2 : (∑ k ∈ Finset.range N, M * (1 / 2 : ℚ) ^ k) =
        M * (∑ k ∈ Finset.range N, (1 / 2 : ℚ) ^ k) := by
      rw [Finset.mul_sum]
    rw [h2]
    calc M * (∑ k ∈ Finset.range N, (1 / 2 : ℚ) ^ k) ≤ M * 2 :=
          mul_le_mul_of_nonneg_left (geom_half_sum_le_two N) hM
      _ = 2 * M := by ring
  obtain ⟨hlo, hhi⟩ := hbound N
  constructor <;> linarith

/-- The same contractive process is trapped in the explicit interval
    `[a 0 - 2M, a 0 + 2M]`; nothing escapes to infinity. -/
theorem geometric_trapped (a : ℕ → ℚ) (M : ℚ) (hM : 0 ≤ M)
    (hstep : ∀ k, -(M * (1 / 2 : ℚ) ^ k) ≤ a (k + 1) - a k ∧
      a (k + 1) - a k ≤ M * (1 / 2 : ℚ) ^ k) (N : ℕ) :
    a 0 - 2 * M ≤ a N ∧ a N ≤ a 0 + 2 * M := by
  obtain ⟨hlo, hhi⟩ := geometric_step_bound a M hM hstep N
  constructor <;> linarith

/-- Tail contraction: for `i ≤ j`, the displacement `a j - a i` is bounded by
    `2M / 2^i`.  Later and later tails have geometrically shrinking diameter. -/
theorem geometric_tail_bound (a : ℕ → ℚ) (M : ℚ) (hM : 0 ≤ M)
    (hstep : ∀ k, -(M * (1 / 2 : ℚ) ^ k) ≤ a (k + 1) - a k ∧
      a (k + 1) - a k ≤ M * (1 / 2 : ℚ) ^ k)
    (i j : ℕ) (hij : i ≤ j) :
    -(2 * M * (1 / 2 : ℚ) ^ i) ≤ a j - a i ∧
      a j - a i ≤ 2 * M * (1 / 2 : ℚ) ^ i := by
  have hM' : 0 ≤ M * (1 / 2 : ℚ) ^ i :=
    mul_nonneg hM (pow_nonneg (by norm_num) i)
  have hstep' : ∀ t, -((M * (1 / 2 : ℚ) ^ i) * (1 / 2 : ℚ) ^ t) ≤
      (fun t => a (i + t)) (t + 1) - (fun t => a (i + t)) t ∧
      (fun t => a (i + t)) (t + 1) - (fun t => a (i + t)) t ≤
      (M * (1 / 2 : ℚ) ^ i) * (1 / 2 : ℚ) ^ t := by
    intro t
    have h := hstep (i + t)
    have hp : M * (1 / 2 : ℚ) ^ (i + t) =
        (M * (1 / 2 : ℚ) ^ i) * (1 / 2 : ℚ) ^ t := by
      rw [pow_add]
      ring
    rw [hp] at h
    dsimp only
    have e : i + (t + 1) = (i + t) + 1 := by omega
    rw [e]
    exact ⟨h.1, h.2⟩
  have hmain := geometric_step_bound (fun t => a (i + t))
    (M * (1 / 2 : ℚ) ^ i) hM' hstep' (j - i)
  have hji : i + (j - i) = j := Nat.add_sub_of_le hij
  simpa [hji, mul_assoc] using hmain

/-- Uniform pairwise bound: any two terms of a contractive sequence differ by
    at most `2M`, regardless of order. -/
theorem geometric_window_bound (a : ℕ → ℚ) (M : ℚ) (hM : 0 ≤ M)
    (hstep : ∀ k, -(M * (1 / 2 : ℚ) ^ k) ≤ a (k + 1) - a k ∧
      a (k + 1) - a k ≤ M * (1 / 2 : ℚ) ^ k) (i j : ℕ) :
    -(2 * M) ≤ a j - a i ∧ a j - a i ≤ 2 * M := by
  have hM2 : 0 ≤ 2 * M := by linarith
  have hscale : ∀ n : ℕ, 2 * M * (1 / 2 : ℚ) ^ n ≤ 2 * M := by
    intro n
    calc 2 * M * (1 / 2 : ℚ) ^ n = (2 * M) * (1 / 2 : ℚ) ^ n := rfl
      _ ≤ (2 * M) * 1 :=
          mul_le_mul_of_nonneg_left (geom_half_pow_le_one n) hM2
      _ = 2 * M := by ring
  rcases le_total i j with hij | hji
  · have h := geometric_tail_bound a M hM hstep i j hij
    constructor <;> linarith [h.1, h.2, hscale i]
  · have h := geometric_tail_bound a M hM hstep j i hji
    constructor <;> linarith [h.1, h.2, hscale j]

/-! ## 4. Unbounded recurrence in a finite state space -/

/-- Finite pigeonhole for maps `Fin (K+1) → Fin K`: two distinct inputs have
    the same value.  This is the base combinatorial engine of the section. -/
theorem discrete_cluster_point (K : ℕ) (f : Fin (K + 1) → Fin K) :
    ∃ x : Fin K, ∃ i j : Fin (K + 1), i ≠ j ∧ f i = x ∧ f j = x := by
  have h : ∃ i j : Fin (K + 1), i ≠ j ∧ f i = f j := by
    by_contra h_all_diff
    push Not at h_all_diff
    have h_inj : Function.Injective f := fun i j h_eq => by
      by_contra h_ne
      exact h_all_diff i j h_ne h_eq
    have h_card := Fintype.card_le_of_injective f h_inj
    rw [Fintype.card_fin, Fintype.card_fin] at h_card
    omega
  rcases h with ⟨i, j, hij, h_eq⟩
  exact ⟨f i, i, j, hij, rfl, h_eq.symm⟩

/-- Every sequence into a finite type `Fin K` repeats inside every window of
    length `K`.  This is the finite pigeonhole principle with an explicit
    window bound. -/
theorem shifted_pigeonhole (K N : ℕ) (f : ℕ → Fin K) :
    ∃ i j : ℕ, i < j ∧ j ≤ K ∧ f (N + i) = f (N + j) := by
  obtain ⟨x, i, j, hij, hi, hj⟩ :=
    discrete_cluster_point K (fun t : Fin (K + 1) => f (N + t.val))
  have hEq : f (N + i.val) = f (N + j.val) := hi.trans hj.symm
  rcases lt_or_gt_of_ne hij with hlt | hgt
  · exact ⟨i.val, j.val, hlt, by omega, hEq⟩
  · exact ⟨j.val, i.val, hgt, by omega, hEq.symm⟩

/-- Exact finite accumulation statement: a sequence into `Fin K` repeats at
    arbitrarily late indices.  For every `N` there are `N ≤ i < j` with equal
    values.  No compactness or infinite-set axiom is used. -/
theorem arbitrarily_late_repetition (K N : ℕ) (f : ℕ → Fin K) :
    ∃ i j : ℕ, N ≤ i ∧ i < j ∧ f i = f j := by
  obtain ⟨i, j, hij, _hjK, hEq⟩ := shifted_pigeonhole K N f
  exact ⟨N + i, N + j, by omega, by omega, hEq⟩

/-- Orbit of a deterministic self-map of a finite type. -/
def orbit {K : ℕ} (g : Fin K → Fin K) (x : Fin K) : ℕ → Fin K
  | 0 => x
  | n + 1 => g (orbit g x n)

@[simp] theorem orbit_zero {K : ℕ} (g : Fin K → Fin K) (x : Fin K) :
    orbit g x 0 = x := rfl

@[simp] theorem orbit_succ {K : ℕ} (g : Fin K → Fin K) (x : Fin K) (n : ℕ) :
    orbit g x (n + 1) = g (orbit g x n) := rfl

/-- Once an orbit repeats, the repeat propagates forever: the period is exact. -/
theorem orbit_periodic_of_repeat {K : ℕ} (g : Fin K → Fin K) (x : Fin K)
    {p q : ℕ} (hbase : orbit g x (p + q) = orbit g x p) :
    ∀ t : ℕ, orbit g x (p + q + t) = orbit g x (p + t) := by
  intro t
  induction t with
  | zero => simpa using hbase
  | succ t ih =>
    have e1 : p + q + (t + 1) = (p + q + t) + 1 := by omega
    have e2 : p + (t + 1) = (p + t) + 1 := by omega
    calc orbit g x (p + q + (t + 1))
        = orbit g x ((p + q + t) + 1) := by rw [e1]
      _ = g (orbit g x (p + q + t)) := by rw [orbit_succ]
      _ = g (orbit g x (p + t)) := by rw [ih]
      _ = orbit g x ((p + t) + 1) := by rw [orbit_succ]
      _ = orbit g x (p + (t + 1)) := by rw [e2]

/-- Finite-state recurrence theorem: every deterministic orbit in `Fin K` is
    eventually periodic with an exact positive period.  This is the discrete
    Poincare recurrence statement, proved entirely by finite pigeonhole. -/
theorem finite_orbit_recurrence (K : ℕ) (g : Fin K → Fin K) (x : Fin K) :
    ∃ p q : ℕ, 0 < q ∧ ∀ t : ℕ, orbit g x (p + q + t) = orbit g x (p + t) := by
  obtain ⟨_, i, j, hij, hi, hj⟩ :=
    discrete_cluster_point K (fun t : Fin (K + 1) => orbit g x t.val)
  have hEq : orbit g x i.val = orbit g x j.val := hi.trans hj.symm
  rcases lt_or_gt_of_ne hij with hlt | hgt
  · refine ⟨i.val, j.val - i.val, by omega, ?_⟩
    apply orbit_periodic_of_repeat g x
    have hji : i.val + (j.val - i.val) = j.val := Nat.add_sub_of_le (le_of_lt hlt)
    rw [hji]
    exact hEq.symm
  · refine ⟨j.val, i.val - j.val, by omega, ?_⟩
    apply orbit_periodic_of_repeat g x
    have hji : j.val + (i.val - j.val) = i.val := Nat.add_sub_of_le (le_of_lt hgt)
    rw [hji]
    exact hEq

/-! ## 5. Descent barriers and bounded-denominator grids -/

/-- Explicit descent budget: `N` strict descents from `a 0` force
    `a N + N ≤ a 0`.  In particular, a strictly descending chain in `ℕ` cannot
    be longer than its starting value. -/
theorem descent_budget (a : ℕ → ℕ) :
    ∀ N : ℕ, (∀ n, n < N → a (n + 1) < a n) → a N + N ≤ a 0 := by
  intro N
  induction N with
  | zero =>
    intro _
    simp
  | succ k ih =>
    intro h
    have hk : ∀ n, n < k → a (n + 1) < a n := fun n hn => h n (by omega)
    have ihk := ih hk
    have hstep := h k (by omega)
    omega

/-- There is no infinite strictly descending sequence in `ℕ`.  This is the
    finite well-foundedness barrier behind every terminating descent argument. -/
theorem no_infinite_nat_descent (a : ℕ → ℕ) : ¬ ∀ n, a (n + 1) < a n := by
  intro h
  have hb := descent_budget a (a 0 + 1) (fun n _ => h n)
  omega

/-- A bounded natural sequence repeats arbitrarily late. -/
theorem bounded_nat_repetition (B N : ℕ) (z : ℕ → ℕ) (hz : ∀ n, z n ≤ B) :
    ∃ i j : ℕ, N ≤ i ∧ i < j ∧ z i = z j := by
  have h := arbitrarily_late_repetition (B + 1) N
    (fun n => (⟨z n, Nat.lt_succ_of_le (hz n)⟩ : Fin (B + 1)))
  obtain ⟨i, j, hNi, hij, hEq⟩ := h
  exact ⟨i, j, hNi, hij, by simpa using congrArg Fin.val hEq⟩

/-- A bounded natural sequence has at most `B + 1` distinct values in any
    finite prefix: the finite range is an explicit finite set. -/
theorem bounded_nat_image_card (B N : ℕ) (z : ℕ → ℕ) (hz : ∀ n, z n ≤ B) :
    ((Finset.range N).image z).card ≤ B + 1 := by
  have hsub : (Finset.range N).image z ⊆
      (Finset.univ : Finset (Fin (B + 1))).image (fun b : Fin (B + 1) => b.val) := by
    intro x hx
    rw [Finset.mem_image] at hx ⊢
    obtain ⟨n, _hn, rfl⟩ := hx
    exact ⟨⟨z n, Nat.lt_succ_of_le (hz n)⟩, Finset.mem_univ _, rfl⟩
  calc ((Finset.range N).image z).card
      ≤ ((Finset.univ : Finset (Fin (B + 1))).image
          (fun b : Fin (B + 1) => b.val)).card :=
        Finset.card_le_card hsub
    _ ≤ (Finset.univ : Finset (Fin (B + 1))).card := Finset.card_image_le
    _ = B + 1 := by simp

/-- Bounded-denominator rational accumulation: any sequence of the form
    `C + num n / Q` with `num n ≤ B` repeats arbitrarily late.  Bounded
    rational data with a fixed denominator cannot encode infinitely many
    distinct values; this is the finite-space accumulation theorem. -/
theorem bounded_grid_accumulation (C : ℚ) (Q B : ℕ) (num : ℕ → ℕ)
    (hbound : ∀ n, num n ≤ B) (N : ℕ) :
    ∃ i j : ℕ, N ≤ i ∧ i < j ∧
      C + (num i : ℚ) / Q = C + (num j : ℚ) / Q := by
  obtain ⟨i, j, hNi, hij, hEq⟩ := bounded_nat_repetition B N num hbound
  exact ⟨i, j, hNi, hij, by rw [hEq]⟩

/-! ## 6. Mutation-testing targets -/

theorem finite_telescope_bound_mut (a : ℕ → ℚ) (d : ℚ)
    (hstep : ∀ k, a (k + 1) - a k ≤ d) (N : ℕ) :
    a N - a 0 ≤ N * d := by
  exact finite_telescope_bound a d hstep N

theorem geometric_step_bound_mut (a : ℕ → ℚ) (M : ℚ) (hM : 0 ≤ M)
    (hstep : ∀ k, -(M * (1 / 2 : ℚ) ^ k) ≤ a (k + 1) - a k ∧
      a (k + 1) - a k ≤ M * (1 / 2 : ℚ) ^ k) (N : ℕ) :
    -(2 * M) ≤ a N - a 0 ∧ a N - a 0 ≤ 2 * M := by
  exact geometric_step_bound a M hM hstep N

theorem arbitrarily_late_repetition_mut (K N : ℕ) (f : ℕ → Fin K) :
    ∃ i j : ℕ, N ≤ i ∧ i < j ∧ f i = f j := by
  exact arbitrarily_late_repetition K N f

theorem finite_orbit_recurrence_mut (K : ℕ) (g : Fin K → Fin K) (x : Fin K) :
    ∃ p q : ℕ, 0 < q ∧ ∀ t : ℕ, orbit g x (p + q + t) = orbit g x (p + t) := by
  exact finite_orbit_recurrence K g x

theorem no_infinite_nat_descent_mut (a : ℕ → ℕ) : ¬ ∀ n, a (n + 1) < a n := by
  exact no_infinite_nat_descent a

theorem bounded_grid_accumulation_mut (C : ℚ) (Q B : ℕ) (num : ℕ → ℕ)
    (hbound : ∀ n, num n ≤ B) (N : ℕ) :
    ∃ i j : ℕ, N ≤ i ∧ i < j ∧
      C + (num i : ℚ) / Q = C + (num j : ℚ) / Q := by
  exact bounded_grid_accumulation C Q B num hbound N

#eval "FiniteLimitBoundary module compiled with zero placeholders."

end Math30.FiniteLimitBoundary
