import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic

/-!
  LegendreBoundedVerification.lean
  Math 3.0 Batch 12: Conjecture #2 — Legendre's Conjecture (bounded verification).

  Scope: `legendre_bounded_up_to_30` is a FORMAL_FINITE_THEOREM. It checks
  `HasPrimeBetweenSquares n` for every `1 ≤ n ≤ 30` by explicit prime witnesses
  in each open interval `(n², (n+1)²)`; the largest witness is `907 < 31² = 961`.
  `legendre_interval_gap_grows` is a FORMAL_GENERAL_THEOREM: the width of the
  interval `(n², (n+1)²)` is exactly `2n + 1`, hence at least `3` for `n ≥ 1`.

  The full Legendre's Conjecture — `∀ n ≥ 1, HasPrimeBetweenSquares n` — remains
  OPEN. This module makes no continuum or asymptotic claim.
-/

namespace Math30.Certificates

/-- `HasPrimeBetweenSquares n` states that some prime lies strictly between the
    consecutive squares `n ^ 2` and `(n + 1) ^ 2`. -/
def HasPrimeBetweenSquares (n : ℕ) : Prop :=
  ∃ p : ℕ, Nat.Prime p ∧ n ^ 2 < p ∧ p < (n + 1) ^ 2

/-- Bounded deterministic verification of Legendre's Conjecture for `1 ≤ n ≤ 30`.
    Each case is discharged by an explicit prime witness in `(n², (n+1)²)`. -/
theorem legendre_bounded_up_to_30 (n : ℕ) (hn : 1 ≤ n ∧ n ≤ 30) :
    HasPrimeBetweenSquares n := by
  rcases hn with ⟨h1, h30⟩
  interval_cases n <;> first
    | (use 2; solve | norm_num [Nat.Prime])
    | (use 5; solve | norm_num [Nat.Prime])
    | (use 11; solve | norm_num [Nat.Prime])
    | (use 17; solve | norm_num [Nat.Prime])
    | (use 29; solve | norm_num [Nat.Prime])
    | (use 37; solve | norm_num [Nat.Prime])
    | (use 53; solve | norm_num [Nat.Prime])
    | (use 67; solve | norm_num [Nat.Prime])
    | (use 83; solve | norm_num [Nat.Prime])
    | (use 101; solve | norm_num [Nat.Prime])
    | (use 127; solve | norm_num [Nat.Prime])
    | (use 149; solve | norm_num [Nat.Prime])
    | (use 173; solve | norm_num [Nat.Prime])
    | (use 197; solve | norm_num [Nat.Prime])
    | (use 227; solve | norm_num [Nat.Prime])
    | (use 257; solve | norm_num [Nat.Prime])
    | (use 293; solve | norm_num [Nat.Prime])
    | (use 331; solve | norm_num [Nat.Prime])
    | (use 367; solve | norm_num [Nat.Prime])
    | (use 401; solve | norm_num [Nat.Prime])
    | (use 443; solve | norm_num [Nat.Prime])
    | (use 487; solve | norm_num [Nat.Prime])
    | (use 541; solve | norm_num [Nat.Prime])
    | (use 577; solve | norm_num [Nat.Prime])
    | (use 631; solve | norm_num [Nat.Prime])
    | (use 677; solve | norm_num [Nat.Prime])
    | (use 733; solve | norm_num [Nat.Prime])
    | (use 787; solve | norm_num [Nat.Prime])
    | (use 853; solve | norm_num [Nat.Prime])
    | (use 907; solve | norm_num [Nat.Prime])

/-- Structural interval-width law: the gap between consecutive squares is
    `2n + 1` and never collapses; for every `n ≥ 1` it is at least `3`. -/
theorem legendre_interval_gap_grows (n : ℕ) (hn : 1 ≤ n) :
    (n + 1) ^ 2 - n ^ 2 = 2 * n + 1 ∧ 3 ≤ (n + 1) ^ 2 - n ^ 2 := by
  have hgap : (n + 1) ^ 2 - n ^ 2 = 2 * n + 1 := by
    have hsq : (n + 1) ^ 2 = n ^ 2 + (2 * n + 1) := by ring
    rw [hsq, Nat.add_sub_cancel_left]
  constructor
  · exact hgap
  · rw [hgap]
    omega

#eval "LegendreBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
