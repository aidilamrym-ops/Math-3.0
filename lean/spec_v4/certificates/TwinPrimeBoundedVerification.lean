import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic

/-!
  TwinPrimeBoundedVerification.lean
  Math 3.0 Batch 13: Conjecture #3 — Twin Prime Conjecture (bounded witnesses + modular invariant).

  Scope: `twin_prime_witnesses_below_200` is a FORMAL_FINITE_THEOREM. It seals the
  15 twin prime pairs with smaller member below 200 by explicit membership and
  primality checks. `twin_prime_mod6_and_diff_sq_24` is a structural
  FORMAL_GENERAL_THEOREM: every twin prime pair with `p > 3` has `p % 6 = 5`
  and square difference divisible by 24.

  The full Twin Prime Conjecture — `∀ N : ℕ, ∃ p ≥ N, IsTwinPrime p` — remains
  OPEN. This module makes no infinitude claim.
-/

namespace Math30.Certificates

/-- `IsTwinPrime p` states that both `p` and `p + 2` are prime. -/
def IsTwinPrime (p : ℕ) : Prop :=
  Nat.Prime p ∧ Nat.Prime (p + 2)

/-- Bounded deterministic verification: all 15 twin prime pairs with smaller
    member below 200 are sealed by explicit witnesses. -/
theorem twin_prime_witnesses_below_200 (p : ℕ)
    (hp : p ∈ [3, 5, 11, 17, 29, 41, 59, 71, 101, 107, 137, 149, 179, 191, 197]) :
    IsTwinPrime p := by
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals norm_num [IsTwinPrime, Nat.Prime]

/-- Structural invariant for twin primes above 3: `p % 6 = 5` and the square
    difference `(p + 2)^2 - p^2 = 4(p + 1)` is divisible by 24. -/
theorem twin_prime_mod6_and_diff_sq_24 (p : ℕ) (htwin : IsTwinPrime p) (hgt3 : 3 < p) :
    p % 6 = 5 ∧ 24 ∣ ((p + 2) ^ 2 - p ^ 2) := by
  have hp : Nat.Prime p := htwin.1
  have hp2 : Nat.Prime (p + 2) := htwin.2
  have hp_odd : p % 2 = 1 := by
    rcases hp.eq_two_or_odd with h | h
    · omega
    · exact h
  have h3p : ¬ 3 ∣ p := by
    intro h
    have h3 : p = 3 := (hp.dvd_iff_eq (by norm_num : (3 : ℕ) ≠ 1)).mp h
    omega
  have h3p2 : ¬ 3 ∣ (p + 2) := by
    intro h
    have h3 : p + 2 = 3 := (hp2.dvd_iff_eq (by norm_num : (3 : ℕ) ≠ 1)).mp h
    omega
  have hp_mod3_ne : p % 3 ≠ 0 := by
    intro h
    exact h3p (Nat.dvd_of_mod_eq_zero h)
  have hp2_mod3_ne : (p + 2) % 3 ≠ 0 := by
    intro h
    exact h3p2 (Nat.dvd_of_mod_eq_zero h)
  have hp_mod3 : p % 3 = 2 := by
    have hlt : p % 3 < 3 := Nat.mod_lt _ (by norm_num)
    have hcases : p % 3 = 1 ∨ p % 3 = 2 := by omega
    rcases hcases with h | h
    · exfalso
      have hzero : (p + 2) % 3 = 0 := by omega
      exact hp2_mod3_ne hzero
    · exact h
  have hmod6 : p % 6 = 5 := by omega
  constructor
  · exact hmod6
  · have h4 : (p + 2) ^ 2 - p ^ 2 = 4 * (p + 1) := by
      have hsq : (p + 2) ^ 2 = p ^ 2 + (4 * p + 4) := by ring
      rw [hsq, Nat.add_sub_cancel_left]
      ring
    rw [h4]
    have h6mod : (p + 1) % 6 = 0 := by omega
    obtain ⟨k, hk⟩ := Nat.dvd_of_mod_eq_zero h6mod
    refine ⟨k, ?_⟩
    rw [hk]
    ring

#eval "TwinPrimeBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
