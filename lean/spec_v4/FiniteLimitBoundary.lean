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
# Finite Limit Boundary: Discrete Bounded Limit Certificates

Formalizes finite limit and accumulation bounds for discrete lattice spaces.
Every theorem here is a FORMAL_FINITE_THEOREM: bounding discrete approximations
to limit processes (such as Cauchy sequences bounded by rational step bounds
and discrete accumulation points in finite domains).

Scope: finite rational bounds and discrete accumulation points only; no continuum
measure theory or full real-analysis topology claims.

No placeholders; no `sorry`, `admit`, `axiom`, `constant`, `opaque`,
`partial def`, `native_decide`, `implemented_by`, or `extern`.
-/

namespace Math30.FiniteLimitBoundary

/-! ## 1. Finite telescoping bound -/

/-- Simplified finite telescoping bound: if `a (k+1) - a k ≤ d` for all `k`,
    then `a N - a 0 ≤ N * d`. -/
theorem finite_telescope_bound (a : ℕ → ℚ) (d : ℚ) (_hd : 0 ≤ d)
    (hstep : ∀ k, a (k + 1) - a k ≤ d) (N : ℕ) :
    a N - a 0 ≤ N * d := by
  induction N with
  | zero =>
    simp [sub_self]
  | succ k ih =>
    have hstep_k := hstep k
    have h_alg : ((k + 1 : ℕ) : ℚ) * d = d + k * d := by push_cast; ring
    linarith

/-! ## 2. Discrete accumulation bound -/

/-- Bounded discrete cluster: any sequence taking values in a finite set of size `K`
    has at least one value appearing twice among `K + 1` steps (Dirichlet / PHP). -/
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

/-! ## 3. Mutation-testing targets -/

theorem finite_telescope_bound_mut (a : ℕ → ℚ) (d : ℚ) (_hd : 0 ≤ d)
    (hstep : ∀ k, a (k + 1) - a k ≤ d) (N : ℕ) :
    a N - a 0 ≤ N * d := by
  exact finite_telescope_bound a d _hd hstep N

theorem discrete_cluster_point_mut (K : ℕ) (f : Fin (K + 1) → Fin K) :
    ∃ x : Fin K, ∃ i j : Fin (K + 1), i ≠ j ∧ f i = x ∧ f j = x := by
  exact discrete_cluster_point K f

#eval "FiniteLimitBoundary module compiled with zero placeholders."

end Math30.FiniteLimitBoundary
