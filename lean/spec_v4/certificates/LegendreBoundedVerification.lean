import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic

/-!
  LegendreBoundedVerification.lean
  Math 3.0 Batch 12: Conjecture #2 — Legendre's Conjecture (bounded verification).

  Scope: `legendre_bounded_up_to_30` and `legendre_bounded_up_to_100` are
  FORMAL_FINITE_THEOREMs. Each checks `HasPrimeBetweenSquares n` by explicit
  prime witnesses in every open interval `(n², (n+1)²)`; the largest witness
  for the 100-bound is `10007 < 101² = 10201`.
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

/-- Bounded deterministic verification of Legendre's Conjecture for `1 ≤ n ≤ 100`.
    Each case is discharged by an explicit prime witness in `(n², (n+1)²)`;
    the largest witness is `10007 < 101² = 10201`. -/
theorem legendre_bounded_up_to_100 (n : ℕ) (hn : 1 ≤ n ∧ n ≤ 100) :
    HasPrimeBetweenSquares n := by
  obtain ⟨h1, h100⟩ := hn
  interval_cases n
  · exact ⟨2, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨11, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨17, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨29, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨37, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨53, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨67, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨83, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨101, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨127, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨149, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨173, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨197, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨227, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨257, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨293, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨331, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨367, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨401, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨443, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨487, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨541, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨577, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨631, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨677, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨733, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨787, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨853, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨907, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨967, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1031, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1091, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1163, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1229, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1297, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1373, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1447, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1523, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1601, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1693, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1777, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1861, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨1949, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2027, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2129, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2213, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2309, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2411, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2503, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2609, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2707, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2819, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨2917, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3037, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3137, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3251, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3371, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3491, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3607, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3727, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3847, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨3989, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4099, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4229, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4357, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4493, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4637, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4783, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨4903, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5051, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5189, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5333, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5477, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5639, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5779, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨5939, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6089, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6247, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6421, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6563, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6733, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨6899, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7057, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7229, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7411, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7573, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7753, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨7927, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨8101, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨8287, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨8467, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨8663, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨8837, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨9029, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨9221, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨9413, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨9613, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨9803, by norm_num [Nat.Prime], by norm_num, by norm_num⟩
  · exact ⟨10007, by norm_num [Nat.Prime], by norm_num, by norm_num⟩

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
