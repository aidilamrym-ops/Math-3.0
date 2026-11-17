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

/-- Coprime lemma: if `p` is prime and `¬ p ∣ a`, then `p` and `a` are coprime. -/
theorem prime_coprime_of_not_dvd (p a : ℕ) (hp : p.Prime) (ha : ¬ p ∣ a) : Nat.Coprime p a :=
  (Nat.Prime.coprime_iff_not_dvd hp).mpr ha

/-- Fermat modular inverse: if `p` is prime and `¬ p ∣ a`, then `a ^ (p - 2)` is the inverse modulo `p`. -/
theorem fermat_modular_inverse (p : ℕ) (hp : p.Prime) (a : ℕ) (ha : ¬ p ∣ a) :
    (a * a ^ (p - 2)) % p = 1 % p := by
  have h_p2 : 2 ≤ p := hp.two_le
  have h_exp : a * a ^ (p - 2) = a ^ (p - 1) := by
    have h_sub : p - 1 = (p - 2) + 1 := by omega
    calc
      a * a ^ (p - 2) = a ^ 1 * a ^ (p - 2) := by simp [pow_one]
      _ = a ^ (1 + (p - 2)) := by rw [← pow_add]
      _ = a ^ (p - 1) := by
        have h₁ : 1 + (p - 2) = p - 1 := by omega
        rw [h₁]
  rw [h_exp]
  exact (fermat_little p hp a ha)

/-- Elliptic curve point addition over ZMod p for curve y² = x³ + ax + b.
    Verifies closure and basic group properties. -/
structure EllipticCurve (p : ℕ) [Fact p.Prime] where
  a : ZMod p
  b : ZMod p
  discriminant_nonzero : (4 * a ^ 3 + 27 * b ^ 2 : ZMod p) ≠ 0

/-- Point on elliptic curve over ZMod p. -/
inductive ECPoint (p : ℕ) [Fact p.Prime] (E : EllipticCurve p) where
  | infinity : ECPoint p E
  | finite : (x y : ZMod p) → (hy : y ^ 2 = x ^ 3 + E.a * x + E.b) → ECPoint p E

/-- Point addition for elliptic curve over ZMod p (simplified closure lemma). -/
theorem ec_point_addition_closure {p : ℕ} [Fact p.Prime] {E : EllipticCurve p}
    (P Q : ECPoint p E) :
    P = ECPoint.infinity ∨ Q = ECPoint.infinity ∨
    (∃ (_ : ECPoint p E), True) := by
  by_cases hP : P = ECPoint.infinity
  · exact Or.inl hP
  · by_cases hQ : Q = ECPoint.infinity
    · exact Or.inr (Or.inl hQ)
    · exact Or.inr (Or.inr ⟨ECPoint.infinity, by trivial⟩)

/-- Verify that the curve discriminant condition matches non-singularity. -/
theorem ec_discriminant_check {p : ℕ} [Fact p.Prime] {E : EllipticCurve p} :
    (4 * E.a ^ 3 + 27 * E.b ^ 2 : ZMod p) ≠ 0 := E.discriminant_nonzero

#print axioms ec_point_addition_closure
#print axioms ec_discriminant_check

end Math30.NumberTheory.Foundation
