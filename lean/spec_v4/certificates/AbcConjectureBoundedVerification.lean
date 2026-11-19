import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Factorization.Basic

/-!
  AbcConjectureBoundedVerification.lean
  Math 3.0 Batch 14: Conjecture #4 — the abc Conjecture (bounded witness + structural radical law).

  Scope: `reyssat_abc_triple_witness` is a FORMAL_FINITE_THEOREM. It seals the
  Reyssat triple `2 + 3^10 * 109 = 23^5`, computes `radical (a * b * c) = 15042`,
  and proves the exact division-free quality inequality
  `c ^ 10 > (radical (a * b * c)) ^ 16` (quality `q > 1.6` at this triple,
  with no floating-point logarithms).
  `abc_coprime_radical_product` is a structural FORMAL_GENERAL_THEOREM: for
  positive coprime `a`, `b`, the product `a * b` is coprime to `a + b` and the
  radical is multiplicative over `a * b * (a + b)`.

  The full abc Conjecture — `∀ ε > 0, only finitely many triples satisfy
  c > radical (a * b * c) ^ (1 + ε)` — remains OPEN. This module makes no
  finiteness, asymptotic, or logarithmic claim.
-/

namespace Math30.Certificates

/-- `IsAbcTriple a b c` states that `a` and `b` are positive coprime naturals
    whose sum is `c`. -/
def IsAbcTriple (a b c : ℕ) : Prop :=
  0 < a ∧ 0 < b ∧ Nat.Coprime a b ∧ a + b = c

/-- `radical n` is the product of the distinct prime divisors of `n`. -/
def radical (n : ℕ) : ℕ :=
  ∏ p ∈ n.primeFactors, p

/-- Bounded witness: the Reyssat triple `2 + 3^10 * 109 = 23^5`, with
    `radical (a * b * c) = 2 * 3 * 109 * 23 = 15042` and the exact
    division-free quality inequality `c^10 > rad(abc)^16`. -/
theorem reyssat_abc_triple_witness (a b c : ℕ)
    (htrip : a = 2 ∧ b = 3 ^ 10 * 109 ∧ c = 23 ^ 5) :
    IsAbcTriple a b c ∧ radical (a * b * c) = 15042 ∧
      c ^ 10 > (radical (a * b * c)) ^ 16 := by
  rcases htrip with ⟨rfl, rfl, rfl⟩
  have hpf : (2 * (3 ^ 10 * 109) * 23 ^ 5).primeFactors = {2, 3, 109, 23} := by
    rw [Nat.primeFactors_mul (by norm_num) (by norm_num)]
    rw [Nat.primeFactors_pow 23 (by norm_num)]
    rw [Nat.primeFactors_mul (by norm_num) (by norm_num)]
    rw [Nat.primeFactors_mul (by norm_num) (by norm_num)]
    rw [Nat.primeFactors_pow 3 (by norm_num)]
    rw [Nat.Prime.primeFactors (by norm_num : Nat.Prime 2),
        Nat.Prime.primeFactors (by norm_num : Nat.Prime 3),
        Nat.Prime.primeFactors (by norm_num : Nat.Prime 109),
        Nat.Prime.primeFactors (by norm_num : Nat.Prime 23)]
    decide
  refine ⟨?_, ?_, ?_⟩
  · norm_num [IsAbcTriple, Nat.Coprime]
  · unfold radical
    rw [hpf]
    decide
  · unfold radical
    rw [hpf]
    norm_num

/-- Structural radical law for coprime additive triples: `a * b` is coprime
    to `a + b`, and `radical` is multiplicative over `a * b * (a + b)`. -/
theorem abc_coprime_radical_product (a b : ℕ)
    (hab : Nat.Coprime a b) (ha : 0 < a) (hb : 0 < b) :
    Nat.Coprime (a * b) (a + b) ∧
      radical (a * b * (a + b)) = radical a * radical b * radical (a + b) := by
  have ha0 : a ≠ 0 := Nat.pos_iff_ne_zero.mp ha
  have hb0 : b ≠ 0 := Nat.pos_iff_ne_zero.mp hb
  have hab0 : a + b ≠ 0 := by omega
  have hmul0 : a * b ≠ 0 := Nat.mul_ne_zero ha0 hb0
  have hcop : Nat.Coprime (a * b) (a + b) := by
    rw [Nat.coprime_mul_iff_left]
    refine ⟨?_, ?_⟩
    · rwa [Nat.coprime_self_add_right]
    · rw [Nat.coprime_add_self_right]
      exact hab.symm
  refine ⟨hcop, ?_⟩
  unfold radical
  rw [Nat.primeFactors_mul hmul0 hab0]
  rw [Finset.prod_union hcop.disjoint_primeFactors]
  rw [Nat.primeFactors_mul ha0 hb0]
  rw [Finset.prod_union hab.disjoint_primeFactors]

#eval "AbcConjectureBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
