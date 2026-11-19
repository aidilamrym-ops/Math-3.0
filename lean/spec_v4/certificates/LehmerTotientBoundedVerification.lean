import Mathlib.Tactic
import Mathlib.Data.Nat.Totient
import Mathlib.Data.Nat.Prime.Basic

/-!
  LehmerTotientBoundedVerification.lean
  Math 3.0 Batch 17: Conjecture #7 — Lehmer's Totient Conjecture
  (bounded non-existence + universal squarefree obstruction).

  Scope: `no_lehmer_composite_up_to_100` is a FORMAL_FINITE_THEOREM
  checking that no composite `2 ≤ n ≤ 100` satisfies
  `Nat.totient n ∣ (n - 1)`.
  `lehmer_composite_must_be_squarefree` is a structural
  FORMAL_GENERAL_THEOREM: any `n > 1` with `Nat.totient n ∣ (n - 1)`
  cannot be divisible by the square of a prime.

  The full Lehmer Totient Conjecture — every `n > 1` with
  `Nat.totient n ∣ (n - 1)` is prime — remains OPEN. The squarefree
  obstruction is necessary but not sufficient.
-/

namespace Math30.Certificates

/-- A Lehmer composite witness: `n > 1` is not prime, yet its totient
    divides `n - 1`. -/
def IsLehmerCompositeWitness (n : ℕ) : Prop :=
  1 < n ∧ ¬ Nat.Prime n ∧ Nat.totient n ∣ (n - 1)

/-- Bounded deterministic verification: no Lehmer composite witness
    exists in the range `2 ≤ n ≤ 100`. -/
theorem no_lehmer_composite_up_to_100 (n : ℕ) (hn : 2 ≤ n ∧ n ≤ 100) :
    ¬ IsLehmerCompositeWitness n := by
  obtain ⟨h2, h100⟩ := hn
  interval_cases n <;> (unfold IsLehmerCompositeWitness; decide)

/-- Universal squarefree obstruction: if `Nat.totient n ∣ (n - 1)` with
    `n > 1`, then no prime square divides `n`. -/
theorem lehmer_composite_must_be_squarefree (n p : ℕ)
    (hdiv : Nat.totient n ∣ n - 1)
    (hn : 1 < n)
    (hp2 : Nat.Prime p ∧ p ^ 2 ∣ n) : False := by
  rcases hp2 with ⟨hp, hp2⟩
  obtain ⟨k, rfl⟩ := hp2
  have hp_dvd_n : p ∣ p ^ 2 * k := by
    rw [pow_two, mul_assoc]
    exact dvd_mul_right p (p * k)
  have hphi : Nat.totient (p ^ 2 * k) = p * Nat.totient (p * k) := by
    rw [pow_two, mul_assoc]
    exact Nat.totient_mul_of_prime_of_dvd hp (dvd_mul_right p k)
  have hp_dvd_phi : p ∣ Nat.totient (p ^ 2 * k) := by
    rw [hphi]
    exact dvd_mul_right p (Nat.totient (p * k))
  have hp_dvd_nm1 : p ∣ p ^ 2 * k - 1 := dvd_trans hp_dvd_phi hdiv
  have hsub : p ∣ 1 := by
    have h := Nat.dvd_sub hp_dvd_n hp_dvd_nm1
    have hEq : p ^ 2 * k - (p ^ 2 * k - 1) = 1 := by
      have hpos : 0 < p ^ 2 * k := lt_trans Nat.zero_lt_one hn
      omega
    rwa [hEq] at h
  exact hp.ne_one (Nat.dvd_one.mp hsub)

#eval "LehmerTotientBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
