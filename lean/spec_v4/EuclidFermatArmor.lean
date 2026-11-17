-- EuclidFermatArmor.lean
-- Math 3.0 / Phase 48: Euclid infinitude + Fermat's little theorem (parameterized)
-- Scope:
--   * Euclid's theorem on the infinitude of primes (via Mathlib);
--   * Fermat's little theorem in parameterized form: for a prime `p` and any
--     `a` with `¬ p ∣ a`, `a ^ (p - 1) ≡ 1 [MOD p]`, derived from Mathlib's
--     finite-field identity `FiniteField.pow_card_sub_one_eq_one` applied to
--     the field `ZMod p`;
--   * the corollary `a ^ p ≡ a [MOD p]` for every `a`, and the concrete Fermat
--     residue instances at p = 5, 7, 11 derived from it.
-- Claim limits:
--   * this file does NOT prove Fermat's Last Theorem;
--   * every claim is residue arithmetic on ℕ modulo a prime; the bounded
--     instances are corollaries, not independent evidence.

import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Nat.Prime.Defs
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.Tactic

namespace Math30.NumberTheory.Foundation

/-- Euclid's theorem: for every bound there is a larger prime. -/
theorem euclid_infinite_primes (n : ℕ) : ∃ p, n < p ∧ Nat.Prime p := by
  obtain ⟨p, hp, hprime⟩ := Nat.exists_infinite_primes (n + 1)
  exact ⟨p, Nat.lt_of_succ_le hp, hprime⟩

/-- **Fermat's little theorem**, parameterized: for a prime `p` and any `a` with
`¬ p ∣ a`, `a ^ (p - 1) ≡ 1 [MOD p]`. -/
theorem fermat_little (p : ℕ) (hp : p.Prime) (a : ℕ) (ha : ¬ p ∣ a) :
    a ^ (p - 1) ≡ 1 [MOD p] := by
  have : Fact (Nat.Prime p) := ⟨hp⟩
  have hne : (a : ZMod p) ≠ 0 := by
    intro h0
    apply ha
    rwa [ZMod.natCast_eq_zero_iff] at h0
  have hcard : Fintype.card (ZMod p) = p := ZMod.card p
  have h1 : (a : ZMod p) ^ (Fintype.card (ZMod p) - 1) = 1 :=
    FiniteField.pow_card_sub_one_eq_one _ hne
  rw [hcard] at h1
  have h2 : ((a ^ (p - 1) : ℕ) : ZMod p) = ((1 : ℕ) : ZMod p) := by
    rw [Nat.cast_pow, Nat.cast_one, h1]
  rwa [ZMod.natCast_eq_natCast_iff] at h2

/-- **Fermat's little theorem**, `a ^ p ≡ a [MOD p]` form: for a prime `p` this
holds for every `a`, divisible by `p` or not. -/
theorem fermat_little_pow (p : ℕ) (hp : p.Prime) (a : ℕ) : a ^ p ≡ a [MOD p] := by
  by_cases h : p ∣ a
  · -- `a` is 0 modulo `p`, so both sides are 0 modulo `p`
    have h0 : a ^ p ≡ 0 [MOD p] := by
      have hpz := (h.modEq_zero_nat).pow p
      rwa [zero_pow (by have := hp.one_lt; omega)] at hpz
    exact Nat.ModEq.trans h0 (h.zero_modEq_nat)
  · -- `a` is invertible modulo `p`: multiply the `p - 1` form by `a`
    have h1 := fermat_little p hp a h
    have h4 := h1.mul_right a
    have e : p - 1 + 1 = p := by
      have := hp.pos
      omega
    calc a ^ p = a ^ ((p - 1) + 1) := by rw [e]
      _ = a ^ (p - 1) * a := pow_succ a (p - 1)
      _ ≡ (1 : ℕ) * a [MOD p] := h4
      _ ≡ a [MOD p] := by rw [one_mul]

/-- Fermat residue instance at p = 5, a = 2, derived from `fermat_little_pow`. -/
theorem fermat_five_two : 2 ^ 5 % 5 = 2 % 5 := by
  simpa only [Nat.ModEq] using fermat_little_pow 5 Nat.prime_five 2

/-- Fermat residue instance at p = 7, a = 3, derived from `fermat_little_pow`. -/
theorem fermat_seven_three : 3 ^ 7 % 7 = 3 % 7 := by
  simpa only [Nat.ModEq] using fermat_little_pow 7 Nat.prime_seven 3

/-- Fermat residue instance at p = 11, a = 5, derived from `fermat_little_pow`. -/
theorem fermat_eleven_five : 5 ^ 11 % 11 = 5 % 11 := by
  simpa only [Nat.ModEq] using fermat_little_pow 11 Nat.prime_eleven 5

#print axioms euclid_infinite_primes
#print axioms fermat_little
#print axioms fermat_little_pow

end Math30.NumberTheory.Foundation
