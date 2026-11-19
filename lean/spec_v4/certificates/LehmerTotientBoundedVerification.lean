import Mathlib.Tactic
import Mathlib.Data.Nat.Totient
import Mathlib.Data.Nat.Prime.Basic

/-!
  LehmerTotientBoundedVerification.lean
  Math 3.0 Batch 18: Lehmer's Totient Conjecture strengthening
  (bounded non-existence up to 200 + odd and squarefree obstructions).

  Scope: `no_lehmer_composite_up_to_200` is a FORMAL_FINITE_THEOREM
  checking that no composite `2 ≤ n ≤ 200` satisfies
  `Nat.totient n ∣ (n - 1)`.
  `lehmer_composite_must_be_odd` and
  `lehmer_composite_must_be_squarefree` are structural
  FORMAL_GENERAL_THEOREMs: any `n > 1` with
  `Nat.totient n ∣ (n - 1)` must be odd and squarefree.
  `lehmer_composite_odd_and_squarefree` combines both obstructions.

  The full Lehmer Totient Conjecture — every `n > 1` with
  `Nat.totient n ∣ (n - 1)` is prime — remains OPEN. Oddness and
  squarefreeness are necessary but not sufficient.
-/

namespace Math30.Certificates

set_option maxRecDepth 100000

/-- A Lehmer composite witness: `n > 1` is not prime, yet its totient
    divides `n - 1`. -/
def IsLehmerCompositeWitness (n : ℕ) : Prop :=
  1 < n ∧ ¬ Nat.Prime n ∧ Nat.totient n ∣ (n - 1)

/-- Ground witness: `4` is not a Lehmer composite witness. -/
theorem no_lehmer_witness_at_four : ¬ IsLehmerCompositeWitness 4 := by
  unfold IsLehmerCompositeWitness
  decide

/-- Bounded deterministic verification: no Lehmer composite witness
    exists in the range `2 ≤ n ≤ 200`. -/
theorem no_lehmer_composite_up_to_200 (n : ℕ) (hn : 2 ≤ n ∧ n ≤ 200) :
    ¬ IsLehmerCompositeWitness n := by
  obtain ⟨h2, h200⟩ := hn
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

/-- Universal oddness obstruction: if `Nat.totient n ∣ (n - 1)` with
    `n > 2`, then `n` is odd. -/
theorem lehmer_composite_must_be_odd (n : ℕ)
    (hdiv : Nat.totient n ∣ n - 1)
    (hn : 2 < n) : Odd n := by
  have h2phi : 2 ∣ Nat.totient n := even_iff_two_dvd.mp (Nat.totient_even hn)
  have h2nm1 : 2 ∣ n - 1 := dvd_trans h2phi hdiv
  rcases Nat.even_or_odd n with he | ho
  · exfalso
    have h2n : 2 ∣ n := even_iff_two_dvd.mp he
    have h := Nat.dvd_sub h2n h2nm1
    have hEq : n - (n - 1) = 1 := by omega
    rw [hEq] at h
    norm_num at h
  · exact ho

/-- Combined structural obstruction: a Lehmer counterexample `n > 2`
    must be odd and squarefree. -/
theorem lehmer_composite_odd_and_squarefree (n : ℕ)
    (hdiv : Nat.totient n ∣ n - 1)
    (hn : 2 < n) :
    Odd n ∧ ∀ p : ℕ, Nat.Prime p → ¬ p ^ 2 ∣ n := by
  constructor
  · exact lehmer_composite_must_be_odd n hdiv hn
  · intro p hp hp2
    exact lehmer_composite_must_be_squarefree n p hdiv (by omega) ⟨hp, hp2⟩

#eval "LehmerTotientBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
