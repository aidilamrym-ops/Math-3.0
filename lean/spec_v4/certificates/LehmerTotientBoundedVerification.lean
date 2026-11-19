import Mathlib.Tactic
import Mathlib.Data.Nat.Totient
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.GCD.BigOperators

/-!
  LehmerTotientBoundedVerification.lean
  Math 3.0 Batch 18-21: Lehmer's Totient Conjecture strengthening
  (bounded non-existence up to 1000 + odd and squarefree obstructions).

  Scope: `no_lehmer_composite_up_to_200` and
  `no_lehmer_composite_up_to_1000` are FORMAL_FINITE_THEOREMs
  checking that no composite `n` in the stated range satisfies
  `Nat.totient n ∣ (n - 1)`. The 1000-bound classifies each case using
  the structural obstructions plus `totient_prod_primes`, Euler's product
  formula for distinct-prime lists, so no kernel evaluation of
  `Nat.totient` at each numeral is required.
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

/-- Euler's product formula for a list of pairwise distinct primes:
    `Nat.totient l.prod = (l.map (fun p => p - 1)).prod`. -/
theorem totient_prod_primes (l : List ℕ)
    (hprime : ∀ p ∈ l, Nat.Prime p)
    (hpair : l.Pairwise (· ≠ ·)) :
    Nat.totient l.prod = (l.map (fun p => p - 1)).prod := by
  induction l with
  | nil => simp
  | cons p rest ih =>
    have hp : Nat.Prime p := hprime p (by simp)
    have hrest_prime : ∀ q ∈ rest, Nat.Prime q := fun q hq => hprime q (by simp [hq])
    have hrest_pair : rest.Pairwise (· ≠ ·) := (List.pairwise_cons.mp hpair).2
    have hp_ne : ∀ q ∈ rest, p ≠ q := (List.pairwise_cons.mp hpair).1
    have hcop : Nat.Coprime p rest.prod := by
      rw [Nat.coprime_list_prod_right_iff]
      intro q hq
      exact (Nat.coprime_primes hp (hrest_prime q hq)).mpr (hp_ne q hq)
    rw [List.prod_cons, Nat.totient_mul hcop, ih hrest_prime hrest_pair,
      List.map_cons, List.prod_cons, Nat.totient_prime hp]

set_option maxHeartbeats 1000000 in
/-- Bounded deterministic verification: no Lehmer composite witness
    exists in the range `2 ≤ n ≤ 1000`. The proof classifies each case:
    primes are excluded by hypothesis, even values by the oddness
    obstruction, odd multiples of a prime square by the squarefree
    obstruction, and the remaining odd squarefree composites by Euler's
    product formula, which avoids kernel evaluation of `Nat.totient`. -/
theorem no_lehmer_composite_up_to_1000 (n : ℕ)
    (hn : 2 ≤ n ∧ n ≤ 1000) :
    ¬ IsLehmerCompositeWitness n := by
  obtain ⟨h2, hN⟩ := hn
  by_cases hp : Nat.Prime n
  · intro hw
    exact hw.2.1 hp
  · interval_cases n
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 4 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 6 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 8 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 9 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 10 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 12 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 14 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 15 = 8 := by
        rw [show (15 : ℕ) = [3, 5].prod by norm_num]
        rw [totient_prod_primes [3, 5] (by decide) (by decide)]
        norm_num
      have hdiv : 8 ∣ 15 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (8 ∣ 15 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 16 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 18 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 20 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 21 = 12 := by
        rw [show (21 : ℕ) = [3, 7].prod by norm_num]
        rw [totient_prod_primes [3, 7] (by decide) (by decide)]
        norm_num
      have hdiv : 12 ∣ 21 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (12 ∣ 21 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 22 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 24 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 25 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 26 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 27 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 28 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 30 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 32 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 33 = 20 := by
        rw [show (33 : ℕ) = [3, 11].prod by norm_num]
        rw [totient_prod_primes [3, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 20 ∣ 33 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (20 ∣ 33 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 34 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 35 = 24 := by
        rw [show (35 : ℕ) = [5, 7].prod by norm_num]
        rw [totient_prod_primes [5, 7] (by decide) (by decide)]
        norm_num
      have hdiv : 24 ∣ 35 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (24 ∣ 35 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 36 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 38 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 39 = 24 := by
        rw [show (39 : ℕ) = [3, 13].prod by norm_num]
        rw [totient_prod_primes [3, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 24 ∣ 39 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (24 ∣ 39 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 40 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 42 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 44 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 45 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 46 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 48 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 49 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 50 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 51 = 32 := by
        rw [show (51 : ℕ) = [3, 17].prod by norm_num]
        rw [totient_prod_primes [3, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 32 ∣ 51 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (32 ∣ 51 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 52 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 54 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 55 = 40 := by
        rw [show (55 : ℕ) = [5, 11].prod by norm_num]
        rw [totient_prod_primes [5, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 40 ∣ 55 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (40 ∣ 55 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 56 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 57 = 36 := by
        rw [show (57 : ℕ) = [3, 19].prod by norm_num]
        rw [totient_prod_primes [3, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 36 ∣ 57 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (36 ∣ 57 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 58 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 60 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 62 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 63 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 64 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 65 = 48 := by
        rw [show (65 : ℕ) = [5, 13].prod by norm_num]
        rw [totient_prod_primes [5, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 48 ∣ 65 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (48 ∣ 65 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 66 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 68 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 69 = 44 := by
        rw [show (69 : ℕ) = [3, 23].prod by norm_num]
        rw [totient_prod_primes [3, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 44 ∣ 69 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (44 ∣ 69 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 70 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 72 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 74 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 75 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 76 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 77 = 60 := by
        rw [show (77 : ℕ) = [7, 11].prod by norm_num]
        rw [totient_prod_primes [7, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 60 ∣ 77 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (60 ∣ 77 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 78 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 80 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 81 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 82 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 84 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 85 = 64 := by
        rw [show (85 : ℕ) = [5, 17].prod by norm_num]
        rw [totient_prod_primes [5, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 64 ∣ 85 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (64 ∣ 85 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 86 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 87 = 56 := by
        rw [show (87 : ℕ) = [3, 29].prod by norm_num]
        rw [totient_prod_primes [3, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 56 ∣ 87 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (56 ∣ 87 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 88 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 90 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 91 = 72 := by
        rw [show (91 : ℕ) = [7, 13].prod by norm_num]
        rw [totient_prod_primes [7, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 72 ∣ 91 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (72 ∣ 91 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 92 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 93 = 60 := by
        rw [show (93 : ℕ) = [3, 31].prod by norm_num]
        rw [totient_prod_primes [3, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 60 ∣ 93 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (60 ∣ 93 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 94 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 95 = 72 := by
        rw [show (95 : ℕ) = [5, 19].prod by norm_num]
        rw [totient_prod_primes [5, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 72 ∣ 95 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (72 ∣ 95 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 96 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 98 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 99 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 100 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 102 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 104 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 105 = 48 := by
        rw [show (105 : ℕ) = [3, 5, 7].prod by norm_num]
        rw [totient_prod_primes [3, 5, 7] (by decide) (by decide)]
        norm_num
      have hdiv : 48 ∣ 105 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (48 ∣ 105 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 106 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 108 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 110 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 111 = 72 := by
        rw [show (111 : ℕ) = [3, 37].prod by norm_num]
        rw [totient_prod_primes [3, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 72 ∣ 111 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (72 ∣ 111 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 112 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 114 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 115 = 88 := by
        rw [show (115 : ℕ) = [5, 23].prod by norm_num]
        rw [totient_prod_primes [5, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 88 ∣ 115 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (88 ∣ 115 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 116 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 117 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 118 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 119 = 96 := by
        rw [show (119 : ℕ) = [7, 17].prod by norm_num]
        rw [totient_prod_primes [7, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 96 ∣ 119 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (96 ∣ 119 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 120 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 121 11 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 122 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 123 = 80 := by
        rw [show (123 : ℕ) = [3, 41].prod by norm_num]
        rw [totient_prod_primes [3, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 80 ∣ 123 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (80 ∣ 123 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 124 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 125 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 126 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 128 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 129 = 84 := by
        rw [show (129 : ℕ) = [3, 43].prod by norm_num]
        rw [totient_prod_primes [3, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 84 ∣ 129 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (84 ∣ 129 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 130 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 132 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 133 = 108 := by
        rw [show (133 : ℕ) = [7, 19].prod by norm_num]
        rw [totient_prod_primes [7, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 108 ∣ 133 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (108 ∣ 133 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 134 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 135 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 136 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 138 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 140 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 141 = 92 := by
        rw [show (141 : ℕ) = [3, 47].prod by norm_num]
        rw [totient_prod_primes [3, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 92 ∣ 141 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (92 ∣ 141 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 142 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 143 = 120 := by
        rw [show (143 : ℕ) = [11, 13].prod by norm_num]
        rw [totient_prod_primes [11, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 120 ∣ 143 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (120 ∣ 143 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 144 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 145 = 112 := by
        rw [show (145 : ℕ) = [5, 29].prod by norm_num]
        rw [totient_prod_primes [5, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 112 ∣ 145 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (112 ∣ 145 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 146 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 147 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 148 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 150 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 152 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 153 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 154 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 155 = 120 := by
        rw [show (155 : ℕ) = [5, 31].prod by norm_num]
        rw [totient_prod_primes [5, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 120 ∣ 155 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (120 ∣ 155 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 156 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 158 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 159 = 104 := by
        rw [show (159 : ℕ) = [3, 53].prod by norm_num]
        rw [totient_prod_primes [3, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 104 ∣ 159 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (104 ∣ 159 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 160 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 161 = 132 := by
        rw [show (161 : ℕ) = [7, 23].prod by norm_num]
        rw [totient_prod_primes [7, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 132 ∣ 161 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (132 ∣ 161 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 162 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 164 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 165 = 80 := by
        rw [show (165 : ℕ) = [3, 5, 11].prod by norm_num]
        rw [totient_prod_primes [3, 5, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 80 ∣ 165 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (80 ∣ 165 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 166 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 168 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 169 13 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 170 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 171 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 172 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 174 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 175 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 176 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 177 = 116 := by
        rw [show (177 : ℕ) = [3, 59].prod by norm_num]
        rw [totient_prod_primes [3, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 116 ∣ 177 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (116 ∣ 177 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 178 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 180 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 182 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 183 = 120 := by
        rw [show (183 : ℕ) = [3, 61].prod by norm_num]
        rw [totient_prod_primes [3, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 120 ∣ 183 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (120 ∣ 183 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 184 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 185 = 144 := by
        rw [show (185 : ℕ) = [5, 37].prod by norm_num]
        rw [totient_prod_primes [5, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 144 ∣ 185 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (144 ∣ 185 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 186 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 187 = 160 := by
        rw [show (187 : ℕ) = [11, 17].prod by norm_num]
        rw [totient_prod_primes [11, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 160 ∣ 187 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (160 ∣ 187 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 188 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 189 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 190 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 192 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 194 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 195 = 96 := by
        rw [show (195 : ℕ) = [3, 5, 13].prod by norm_num]
        rw [totient_prod_primes [3, 5, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 96 ∣ 195 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (96 ∣ 195 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 196 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 198 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 200 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 201 = 132 := by
        rw [show (201 : ℕ) = [3, 67].prod by norm_num]
        rw [totient_prod_primes [3, 67] (by decide) (by decide)]
        norm_num
      have hdiv : 132 ∣ 201 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (132 ∣ 201 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 202 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 203 = 168 := by
        rw [show (203 : ℕ) = [7, 29].prod by norm_num]
        rw [totient_prod_primes [7, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 168 ∣ 203 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (168 ∣ 203 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 204 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 205 = 160 := by
        rw [show (205 : ℕ) = [5, 41].prod by norm_num]
        rw [totient_prod_primes [5, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 160 ∣ 205 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (160 ∣ 205 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 206 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 207 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 208 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 209 = 180 := by
        rw [show (209 : ℕ) = [11, 19].prod by norm_num]
        rw [totient_prod_primes [11, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 180 ∣ 209 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (180 ∣ 209 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 210 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 212 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 213 = 140 := by
        rw [show (213 : ℕ) = [3, 71].prod by norm_num]
        rw [totient_prod_primes [3, 71] (by decide) (by decide)]
        norm_num
      have hdiv : 140 ∣ 213 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (140 ∣ 213 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 214 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 215 = 168 := by
        rw [show (215 : ℕ) = [5, 43].prod by norm_num]
        rw [totient_prod_primes [5, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 168 ∣ 215 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (168 ∣ 215 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 216 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 217 = 180 := by
        rw [show (217 : ℕ) = [7, 31].prod by norm_num]
        rw [totient_prod_primes [7, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 180 ∣ 217 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (180 ∣ 217 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 218 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 219 = 144 := by
        rw [show (219 : ℕ) = [3, 73].prod by norm_num]
        rw [totient_prod_primes [3, 73] (by decide) (by decide)]
        norm_num
      have hdiv : 144 ∣ 219 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (144 ∣ 219 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 220 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 221 = 192 := by
        rw [show (221 : ℕ) = [13, 17].prod by norm_num]
        rw [totient_prod_primes [13, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 192 ∣ 221 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (192 ∣ 221 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 222 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 224 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 225 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 226 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 228 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 230 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 231 = 120 := by
        rw [show (231 : ℕ) = [3, 7, 11].prod by norm_num]
        rw [totient_prod_primes [3, 7, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 120 ∣ 231 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (120 ∣ 231 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 232 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 234 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 235 = 184 := by
        rw [show (235 : ℕ) = [5, 47].prod by norm_num]
        rw [totient_prod_primes [5, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 184 ∣ 235 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (184 ∣ 235 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 236 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 237 = 156 := by
        rw [show (237 : ℕ) = [3, 79].prod by norm_num]
        rw [totient_prod_primes [3, 79] (by decide) (by decide)]
        norm_num
      have hdiv : 156 ∣ 237 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (156 ∣ 237 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 238 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 240 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 242 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 243 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 244 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 245 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 246 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 247 = 216 := by
        rw [show (247 : ℕ) = [13, 19].prod by norm_num]
        rw [totient_prod_primes [13, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 216 ∣ 247 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (216 ∣ 247 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 248 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 249 = 164 := by
        rw [show (249 : ℕ) = [3, 83].prod by norm_num]
        rw [totient_prod_primes [3, 83] (by decide) (by decide)]
        norm_num
      have hdiv : 164 ∣ 249 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (164 ∣ 249 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 250 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 252 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 253 = 220 := by
        rw [show (253 : ℕ) = [11, 23].prod by norm_num]
        rw [totient_prod_primes [11, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 220 ∣ 253 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (220 ∣ 253 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 254 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 255 = 128 := by
        rw [show (255 : ℕ) = [3, 5, 17].prod by norm_num]
        rw [totient_prod_primes [3, 5, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 128 ∣ 255 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (128 ∣ 255 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 256 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 258 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 259 = 216 := by
        rw [show (259 : ℕ) = [7, 37].prod by norm_num]
        rw [totient_prod_primes [7, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 216 ∣ 259 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (216 ∣ 259 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 260 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 261 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 262 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 264 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 265 = 208 := by
        rw [show (265 : ℕ) = [5, 53].prod by norm_num]
        rw [totient_prod_primes [5, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 208 ∣ 265 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (208 ∣ 265 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 266 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 267 = 176 := by
        rw [show (267 : ℕ) = [3, 89].prod by norm_num]
        rw [totient_prod_primes [3, 89] (by decide) (by decide)]
        norm_num
      have hdiv : 176 ∣ 267 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (176 ∣ 267 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 268 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 270 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 272 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 273 = 144 := by
        rw [show (273 : ℕ) = [3, 7, 13].prod by norm_num]
        rw [totient_prod_primes [3, 7, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 144 ∣ 273 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (144 ∣ 273 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 274 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 275 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 276 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 278 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 279 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 280 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 282 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 284 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 285 = 144 := by
        rw [show (285 : ℕ) = [3, 5, 19].prod by norm_num]
        rw [totient_prod_primes [3, 5, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 144 ∣ 285 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (144 ∣ 285 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 286 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 287 = 240 := by
        rw [show (287 : ℕ) = [7, 41].prod by norm_num]
        rw [totient_prod_primes [7, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 240 ∣ 287 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (240 ∣ 287 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 288 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 289 17 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 290 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 291 = 192 := by
        rw [show (291 : ℕ) = [3, 97].prod by norm_num]
        rw [totient_prod_primes [3, 97] (by decide) (by decide)]
        norm_num
      have hdiv : 192 ∣ 291 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (192 ∣ 291 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 292 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 294 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 295 = 232 := by
        rw [show (295 : ℕ) = [5, 59].prod by norm_num]
        rw [totient_prod_primes [5, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 232 ∣ 295 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (232 ∣ 295 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 296 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 297 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 298 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 299 = 264 := by
        rw [show (299 : ℕ) = [13, 23].prod by norm_num]
        rw [totient_prod_primes [13, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 264 ∣ 299 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (264 ∣ 299 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 300 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 301 = 252 := by
        rw [show (301 : ℕ) = [7, 43].prod by norm_num]
        rw [totient_prod_primes [7, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 252 ∣ 301 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (252 ∣ 301 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 302 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 303 = 200 := by
        rw [show (303 : ℕ) = [3, 101].prod by norm_num]
        rw [totient_prod_primes [3, 101] (by decide) (by decide)]
        norm_num
      have hdiv : 200 ∣ 303 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (200 ∣ 303 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 304 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 305 = 240 := by
        rw [show (305 : ℕ) = [5, 61].prod by norm_num]
        rw [totient_prod_primes [5, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 240 ∣ 305 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (240 ∣ 305 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 306 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 308 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 309 = 204 := by
        rw [show (309 : ℕ) = [3, 103].prod by norm_num]
        rw [totient_prod_primes [3, 103] (by decide) (by decide)]
        norm_num
      have hdiv : 204 ∣ 309 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (204 ∣ 309 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 310 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 312 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 314 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 315 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 316 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 318 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 319 = 280 := by
        rw [show (319 : ℕ) = [11, 29].prod by norm_num]
        rw [totient_prod_primes [11, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 280 ∣ 319 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (280 ∣ 319 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 320 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 321 = 212 := by
        rw [show (321 : ℕ) = [3, 107].prod by norm_num]
        rw [totient_prod_primes [3, 107] (by decide) (by decide)]
        norm_num
      have hdiv : 212 ∣ 321 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (212 ∣ 321 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 322 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 323 = 288 := by
        rw [show (323 : ℕ) = [17, 19].prod by norm_num]
        rw [totient_prod_primes [17, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 288 ∣ 323 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (288 ∣ 323 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 324 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 325 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 326 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 327 = 216 := by
        rw [show (327 : ℕ) = [3, 109].prod by norm_num]
        rw [totient_prod_primes [3, 109] (by decide) (by decide)]
        norm_num
      have hdiv : 216 ∣ 327 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (216 ∣ 327 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 328 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 329 = 276 := by
        rw [show (329 : ℕ) = [7, 47].prod by norm_num]
        rw [totient_prod_primes [7, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 276 ∣ 329 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (276 ∣ 329 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 330 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 332 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 333 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 334 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 335 = 264 := by
        rw [show (335 : ℕ) = [5, 67].prod by norm_num]
        rw [totient_prod_primes [5, 67] (by decide) (by decide)]
        norm_num
      have hdiv : 264 ∣ 335 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (264 ∣ 335 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 336 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 338 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 339 = 224 := by
        rw [show (339 : ℕ) = [3, 113].prod by norm_num]
        rw [totient_prod_primes [3, 113] (by decide) (by decide)]
        norm_num
      have hdiv : 224 ∣ 339 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (224 ∣ 339 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 340 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 341 = 300 := by
        rw [show (341 : ℕ) = [11, 31].prod by norm_num]
        rw [totient_prod_primes [11, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 300 ∣ 341 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (300 ∣ 341 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 342 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 343 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 344 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 345 = 176 := by
        rw [show (345 : ℕ) = [3, 5, 23].prod by norm_num]
        rw [totient_prod_primes [3, 5, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 176 ∣ 345 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (176 ∣ 345 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 346 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 348 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 350 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 351 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 352 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 354 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 355 = 280 := by
        rw [show (355 : ℕ) = [5, 71].prod by norm_num]
        rw [totient_prod_primes [5, 71] (by decide) (by decide)]
        norm_num
      have hdiv : 280 ∣ 355 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (280 ∣ 355 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 356 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 357 = 192 := by
        rw [show (357 : ℕ) = [3, 7, 17].prod by norm_num]
        rw [totient_prod_primes [3, 7, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 192 ∣ 357 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (192 ∣ 357 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 358 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 360 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 361 19 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 362 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 363 11 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 364 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 365 = 288 := by
        rw [show (365 : ℕ) = [5, 73].prod by norm_num]
        rw [totient_prod_primes [5, 73] (by decide) (by decide)]
        norm_num
      have hdiv : 288 ∣ 365 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (288 ∣ 365 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 366 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 368 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 369 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 370 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 371 = 312 := by
        rw [show (371 : ℕ) = [7, 53].prod by norm_num]
        rw [totient_prod_primes [7, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 312 ∣ 371 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (312 ∣ 371 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 372 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 374 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 375 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 376 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 377 = 336 := by
        rw [show (377 : ℕ) = [13, 29].prod by norm_num]
        rw [totient_prod_primes [13, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 336 ∣ 377 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (336 ∣ 377 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 378 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 380 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 381 = 252 := by
        rw [show (381 : ℕ) = [3, 127].prod by norm_num]
        rw [totient_prod_primes [3, 127] (by decide) (by decide)]
        norm_num
      have hdiv : 252 ∣ 381 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (252 ∣ 381 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 382 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 384 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 385 = 240 := by
        rw [show (385 : ℕ) = [5, 7, 11].prod by norm_num]
        rw [totient_prod_primes [5, 7, 11] (by decide) (by decide)]
        norm_num
      have hdiv : 240 ∣ 385 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (240 ∣ 385 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 386 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 387 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 388 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 390 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 391 = 352 := by
        rw [show (391 : ℕ) = [17, 23].prod by norm_num]
        rw [totient_prod_primes [17, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 352 ∣ 391 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (352 ∣ 391 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 392 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 393 = 260 := by
        rw [show (393 : ℕ) = [3, 131].prod by norm_num]
        rw [totient_prod_primes [3, 131] (by decide) (by decide)]
        norm_num
      have hdiv : 260 ∣ 393 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (260 ∣ 393 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 394 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 395 = 312 := by
        rw [show (395 : ℕ) = [5, 79].prod by norm_num]
        rw [totient_prod_primes [5, 79] (by decide) (by decide)]
        norm_num
      have hdiv : 312 ∣ 395 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (312 ∣ 395 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 396 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 398 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 399 = 216 := by
        rw [show (399 : ℕ) = [3, 7, 19].prod by norm_num]
        rw [totient_prod_primes [3, 7, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 216 ∣ 399 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (216 ∣ 399 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 400 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 402 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 403 = 360 := by
        rw [show (403 : ℕ) = [13, 31].prod by norm_num]
        rw [totient_prod_primes [13, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 403 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 403 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 404 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 405 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 406 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 407 = 360 := by
        rw [show (407 : ℕ) = [11, 37].prod by norm_num]
        rw [totient_prod_primes [11, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 407 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 407 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 408 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 410 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 411 = 272 := by
        rw [show (411 : ℕ) = [3, 137].prod by norm_num]
        rw [totient_prod_primes [3, 137] (by decide) (by decide)]
        norm_num
      have hdiv : 272 ∣ 411 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (272 ∣ 411 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 412 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 413 = 348 := by
        rw [show (413 : ℕ) = [7, 59].prod by norm_num]
        rw [totient_prod_primes [7, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 348 ∣ 413 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (348 ∣ 413 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 414 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 415 = 328 := by
        rw [show (415 : ℕ) = [5, 83].prod by norm_num]
        rw [totient_prod_primes [5, 83] (by decide) (by decide)]
        norm_num
      have hdiv : 328 ∣ 415 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (328 ∣ 415 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 416 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 417 = 276 := by
        rw [show (417 : ℕ) = [3, 139].prod by norm_num]
        rw [totient_prod_primes [3, 139] (by decide) (by decide)]
        norm_num
      have hdiv : 276 ∣ 417 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (276 ∣ 417 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 418 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 420 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 422 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 423 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 424 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 425 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 426 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 427 = 360 := by
        rw [show (427 : ℕ) = [7, 61].prod by norm_num]
        rw [totient_prod_primes [7, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 427 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 427 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 428 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 429 = 240 := by
        rw [show (429 : ℕ) = [3, 11, 13].prod by norm_num]
        rw [totient_prod_primes [3, 11, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 240 ∣ 429 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (240 ∣ 429 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 430 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 432 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 434 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 435 = 224 := by
        rw [show (435 : ℕ) = [3, 5, 29].prod by norm_num]
        rw [totient_prod_primes [3, 5, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 224 ∣ 435 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (224 ∣ 435 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 436 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 437 = 396 := by
        rw [show (437 : ℕ) = [19, 23].prod by norm_num]
        rw [totient_prod_primes [19, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 396 ∣ 437 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (396 ∣ 437 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 438 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 440 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 441 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 442 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 444 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 445 = 352 := by
        rw [show (445 : ℕ) = [5, 89].prod by norm_num]
        rw [totient_prod_primes [5, 89] (by decide) (by decide)]
        norm_num
      have hdiv : 352 ∣ 445 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (352 ∣ 445 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 446 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 447 = 296 := by
        rw [show (447 : ℕ) = [3, 149].prod by norm_num]
        rw [totient_prod_primes [3, 149] (by decide) (by decide)]
        norm_num
      have hdiv : 296 ∣ 447 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (296 ∣ 447 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 448 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 450 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 451 = 400 := by
        rw [show (451 : ℕ) = [11, 41].prod by norm_num]
        rw [totient_prod_primes [11, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 400 ∣ 451 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (400 ∣ 451 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 452 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 453 = 300 := by
        rw [show (453 : ℕ) = [3, 151].prod by norm_num]
        rw [totient_prod_primes [3, 151] (by decide) (by decide)]
        norm_num
      have hdiv : 300 ∣ 453 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (300 ∣ 453 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 454 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 455 = 288 := by
        rw [show (455 : ℕ) = [5, 7, 13].prod by norm_num]
        rw [totient_prod_primes [5, 7, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 288 ∣ 455 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (288 ∣ 455 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 456 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 458 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 459 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 460 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 462 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 464 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 465 = 240 := by
        rw [show (465 : ℕ) = [3, 5, 31].prod by norm_num]
        rw [totient_prod_primes [3, 5, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 240 ∣ 465 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (240 ∣ 465 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 466 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 468 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 469 = 396 := by
        rw [show (469 : ℕ) = [7, 67].prod by norm_num]
        rw [totient_prod_primes [7, 67] (by decide) (by decide)]
        norm_num
      have hdiv : 396 ∣ 469 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (396 ∣ 469 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 470 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 471 = 312 := by
        rw [show (471 : ℕ) = [3, 157].prod by norm_num]
        rw [totient_prod_primes [3, 157] (by decide) (by decide)]
        norm_num
      have hdiv : 312 ∣ 471 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (312 ∣ 471 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 472 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 473 = 420 := by
        rw [show (473 : ℕ) = [11, 43].prod by norm_num]
        rw [totient_prod_primes [11, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 420 ∣ 473 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (420 ∣ 473 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 474 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 475 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 476 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 477 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 478 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 480 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 481 = 432 := by
        rw [show (481 : ℕ) = [13, 37].prod by norm_num]
        rw [totient_prod_primes [13, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 481 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 481 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 482 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 483 = 264 := by
        rw [show (483 : ℕ) = [3, 7, 23].prod by norm_num]
        rw [totient_prod_primes [3, 7, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 264 ∣ 483 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (264 ∣ 483 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 484 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 485 = 384 := by
        rw [show (485 : ℕ) = [5, 97].prod by norm_num]
        rw [totient_prod_primes [5, 97] (by decide) (by decide)]
        norm_num
      have hdiv : 384 ∣ 485 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (384 ∣ 485 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 486 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 488 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 489 = 324 := by
        rw [show (489 : ℕ) = [3, 163].prod by norm_num]
        rw [totient_prod_primes [3, 163] (by decide) (by decide)]
        norm_num
      have hdiv : 324 ∣ 489 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (324 ∣ 489 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 490 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 492 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 493 = 448 := by
        rw [show (493 : ℕ) = [17, 29].prod by norm_num]
        rw [totient_prod_primes [17, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 448 ∣ 493 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (448 ∣ 493 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 494 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 495 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 496 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 497 = 420 := by
        rw [show (497 : ℕ) = [7, 71].prod by norm_num]
        rw [totient_prod_primes [7, 71] (by decide) (by decide)]
        norm_num
      have hdiv : 420 ∣ 497 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (420 ∣ 497 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 498 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 500 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 501 = 332 := by
        rw [show (501 : ℕ) = [3, 167].prod by norm_num]
        rw [totient_prod_primes [3, 167] (by decide) (by decide)]
        norm_num
      have hdiv : 332 ∣ 501 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (332 ∣ 501 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 502 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 504 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 505 = 400 := by
        rw [show (505 : ℕ) = [5, 101].prod by norm_num]
        rw [totient_prod_primes [5, 101] (by decide) (by decide)]
        norm_num
      have hdiv : 400 ∣ 505 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (400 ∣ 505 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 506 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 507 13 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 508 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 510 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 511 = 432 := by
        rw [show (511 : ℕ) = [7, 73].prod by norm_num]
        rw [totient_prod_primes [7, 73] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 511 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 511 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 512 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 513 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 514 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 515 = 408 := by
        rw [show (515 : ℕ) = [5, 103].prod by norm_num]
        rw [totient_prod_primes [5, 103] (by decide) (by decide)]
        norm_num
      have hdiv : 408 ∣ 515 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (408 ∣ 515 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 516 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 517 = 460 := by
        rw [show (517 : ℕ) = [11, 47].prod by norm_num]
        rw [totient_prod_primes [11, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 460 ∣ 517 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (460 ∣ 517 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 518 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 519 = 344 := by
        rw [show (519 : ℕ) = [3, 173].prod by norm_num]
        rw [totient_prod_primes [3, 173] (by decide) (by decide)]
        norm_num
      have hdiv : 344 ∣ 519 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (344 ∣ 519 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 520 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 522 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 524 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 525 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 526 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 527 = 480 := by
        rw [show (527 : ℕ) = [17, 31].prod by norm_num]
        rw [totient_prod_primes [17, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 527 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 527 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 528 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 529 23 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 530 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 531 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 532 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 533 = 480 := by
        rw [show (533 : ℕ) = [13, 41].prod by norm_num]
        rw [totient_prod_primes [13, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 533 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 533 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 534 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 535 = 424 := by
        rw [show (535 : ℕ) = [5, 107].prod by norm_num]
        rw [totient_prod_primes [5, 107] (by decide) (by decide)]
        norm_num
      have hdiv : 424 ∣ 535 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (424 ∣ 535 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 536 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 537 = 356 := by
        rw [show (537 : ℕ) = [3, 179].prod by norm_num]
        rw [totient_prod_primes [3, 179] (by decide) (by decide)]
        norm_num
      have hdiv : 356 ∣ 537 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (356 ∣ 537 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 538 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 539 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 540 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 542 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 543 = 360 := by
        rw [show (543 : ℕ) = [3, 181].prod by norm_num]
        rw [totient_prod_primes [3, 181] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 543 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 543 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 544 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 545 = 432 := by
        rw [show (545 : ℕ) = [5, 109].prod by norm_num]
        rw [totient_prod_primes [5, 109] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 545 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 545 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 546 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 548 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 549 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 550 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 551 = 504 := by
        rw [show (551 : ℕ) = [19, 29].prod by norm_num]
        rw [totient_prod_primes [19, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 504 ∣ 551 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (504 ∣ 551 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 552 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 553 = 468 := by
        rw [show (553 : ℕ) = [7, 79].prod by norm_num]
        rw [totient_prod_primes [7, 79] (by decide) (by decide)]
        norm_num
      have hdiv : 468 ∣ 553 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (468 ∣ 553 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 554 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 555 = 288 := by
        rw [show (555 : ℕ) = [3, 5, 37].prod by norm_num]
        rw [totient_prod_primes [3, 5, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 288 ∣ 555 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (288 ∣ 555 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 556 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 558 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 559 = 504 := by
        rw [show (559 : ℕ) = [13, 43].prod by norm_num]
        rw [totient_prod_primes [13, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 504 ∣ 559 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (504 ∣ 559 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 560 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 561 = 320 := by
        rw [show (561 : ℕ) = [3, 11, 17].prod by norm_num]
        rw [totient_prod_primes [3, 11, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 320 ∣ 561 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (320 ∣ 561 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 562 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 564 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 565 = 448 := by
        rw [show (565 : ℕ) = [5, 113].prod by norm_num]
        rw [totient_prod_primes [5, 113] (by decide) (by decide)]
        norm_num
      have hdiv : 448 ∣ 565 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (448 ∣ 565 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 566 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 567 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 568 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 570 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 572 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 573 = 380 := by
        rw [show (573 : ℕ) = [3, 191].prod by norm_num]
        rw [totient_prod_primes [3, 191] (by decide) (by decide)]
        norm_num
      have hdiv : 380 ∣ 573 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (380 ∣ 573 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 574 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 575 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 576 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 578 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 579 = 384 := by
        rw [show (579 : ℕ) = [3, 193].prod by norm_num]
        rw [totient_prod_primes [3, 193] (by decide) (by decide)]
        norm_num
      have hdiv : 384 ∣ 579 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (384 ∣ 579 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 580 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 581 = 492 := by
        rw [show (581 : ℕ) = [7, 83].prod by norm_num]
        rw [totient_prod_primes [7, 83] (by decide) (by decide)]
        norm_num
      have hdiv : 492 ∣ 581 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (492 ∣ 581 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 582 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 583 = 520 := by
        rw [show (583 : ℕ) = [11, 53].prod by norm_num]
        rw [totient_prod_primes [11, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 520 ∣ 583 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (520 ∣ 583 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 584 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 585 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 586 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 588 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 589 = 540 := by
        rw [show (589 : ℕ) = [19, 31].prod by norm_num]
        rw [totient_prod_primes [19, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 540 ∣ 589 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (540 ∣ 589 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 590 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 591 = 392 := by
        rw [show (591 : ℕ) = [3, 197].prod by norm_num]
        rw [totient_prod_primes [3, 197] (by decide) (by decide)]
        norm_num
      have hdiv : 392 ∣ 591 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (392 ∣ 591 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 592 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 594 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 595 = 384 := by
        rw [show (595 : ℕ) = [5, 7, 17].prod by norm_num]
        rw [totient_prod_primes [5, 7, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 384 ∣ 595 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (384 ∣ 595 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 596 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 597 = 396 := by
        rw [show (597 : ℕ) = [3, 199].prod by norm_num]
        rw [totient_prod_primes [3, 199] (by decide) (by decide)]
        norm_num
      have hdiv : 396 ∣ 597 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (396 ∣ 597 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 598 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 600 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 602 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 603 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 604 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 605 11 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 606 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 608 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 609 = 336 := by
        rw [show (609 : ℕ) = [3, 7, 29].prod by norm_num]
        rw [totient_prod_primes [3, 7, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 336 ∣ 609 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (336 ∣ 609 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 610 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 611 = 552 := by
        rw [show (611 : ℕ) = [13, 47].prod by norm_num]
        rw [totient_prod_primes [13, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 552 ∣ 611 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (552 ∣ 611 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 612 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 614 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 615 = 320 := by
        rw [show (615 : ℕ) = [3, 5, 41].prod by norm_num]
        rw [totient_prod_primes [3, 5, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 320 ∣ 615 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (320 ∣ 615 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 616 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 618 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 620 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 621 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 622 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 623 = 528 := by
        rw [show (623 : ℕ) = [7, 89].prod by norm_num]
        rw [totient_prod_primes [7, 89] (by decide) (by decide)]
        norm_num
      have hdiv : 528 ∣ 623 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (528 ∣ 623 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 624 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 625 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 626 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 627 = 360 := by
        rw [show (627 : ℕ) = [3, 11, 19].prod by norm_num]
        rw [totient_prod_primes [3, 11, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 627 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 627 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 628 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 629 = 576 := by
        rw [show (629 : ℕ) = [17, 37].prod by norm_num]
        rw [totient_prod_primes [17, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 576 ∣ 629 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (576 ∣ 629 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 630 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 632 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 633 = 420 := by
        rw [show (633 : ℕ) = [3, 211].prod by norm_num]
        rw [totient_prod_primes [3, 211] (by decide) (by decide)]
        norm_num
      have hdiv : 420 ∣ 633 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (420 ∣ 633 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 634 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 635 = 504 := by
        rw [show (635 : ℕ) = [5, 127].prod by norm_num]
        rw [totient_prod_primes [5, 127] (by decide) (by decide)]
        norm_num
      have hdiv : 504 ∣ 635 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (504 ∣ 635 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 636 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 637 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 638 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 639 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 640 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 642 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 644 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 645 = 336 := by
        rw [show (645 : ℕ) = [3, 5, 43].prod by norm_num]
        rw [totient_prod_primes [3, 5, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 336 ∣ 645 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (336 ∣ 645 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 646 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 648 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 649 = 580 := by
        rw [show (649 : ℕ) = [11, 59].prod by norm_num]
        rw [totient_prod_primes [11, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 580 ∣ 649 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (580 ∣ 649 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 650 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 651 = 360 := by
        rw [show (651 : ℕ) = [3, 7, 31].prod by norm_num]
        rw [totient_prod_primes [3, 7, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 360 ∣ 651 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (360 ∣ 651 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 652 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 654 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 655 = 520 := by
        rw [show (655 : ℕ) = [5, 131].prod by norm_num]
        rw [totient_prod_primes [5, 131] (by decide) (by decide)]
        norm_num
      have hdiv : 520 ∣ 655 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (520 ∣ 655 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 656 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 657 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 658 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 660 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 662 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 663 = 384 := by
        rw [show (663 : ℕ) = [3, 13, 17].prod by norm_num]
        rw [totient_prod_primes [3, 13, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 384 ∣ 663 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (384 ∣ 663 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 664 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 665 = 432 := by
        rw [show (665 : ℕ) = [5, 7, 19].prod by norm_num]
        rw [totient_prod_primes [5, 7, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 665 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 665 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 666 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 667 = 616 := by
        rw [show (667 : ℕ) = [23, 29].prod by norm_num]
        rw [totient_prod_primes [23, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 616 ∣ 667 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (616 ∣ 667 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 668 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 669 = 444 := by
        rw [show (669 : ℕ) = [3, 223].prod by norm_num]
        rw [totient_prod_primes [3, 223] (by decide) (by decide)]
        norm_num
      have hdiv : 444 ∣ 669 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (444 ∣ 669 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 670 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 671 = 600 := by
        rw [show (671 : ℕ) = [11, 61].prod by norm_num]
        rw [totient_prod_primes [11, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 600 ∣ 671 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (600 ∣ 671 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 672 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 674 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 675 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 676 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 678 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 679 = 576 := by
        rw [show (679 : ℕ) = [7, 97].prod by norm_num]
        rw [totient_prod_primes [7, 97] (by decide) (by decide)]
        norm_num
      have hdiv : 576 ∣ 679 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (576 ∣ 679 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 680 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 681 = 452 := by
        rw [show (681 : ℕ) = [3, 227].prod by norm_num]
        rw [totient_prod_primes [3, 227] (by decide) (by decide)]
        norm_num
      have hdiv : 452 ∣ 681 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (452 ∣ 681 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 682 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 684 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 685 = 544 := by
        rw [show (685 : ℕ) = [5, 137].prod by norm_num]
        rw [totient_prod_primes [5, 137] (by decide) (by decide)]
        norm_num
      have hdiv : 544 ∣ 685 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (544 ∣ 685 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 686 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 687 = 456 := by
        rw [show (687 : ℕ) = [3, 229].prod by norm_num]
        rw [totient_prod_primes [3, 229] (by decide) (by decide)]
        norm_num
      have hdiv : 456 ∣ 687 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (456 ∣ 687 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 688 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 689 = 624 := by
        rw [show (689 : ℕ) = [13, 53].prod by norm_num]
        rw [totient_prod_primes [13, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 624 ∣ 689 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (624 ∣ 689 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 690 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 692 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 693 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 694 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 695 = 552 := by
        rw [show (695 : ℕ) = [5, 139].prod by norm_num]
        rw [totient_prod_primes [5, 139] (by decide) (by decide)]
        norm_num
      have hdiv : 552 ∣ 695 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (552 ∣ 695 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 696 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 697 = 640 := by
        rw [show (697 : ℕ) = [17, 41].prod by norm_num]
        rw [totient_prod_primes [17, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 640 ∣ 697 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (640 ∣ 697 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 698 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 699 = 464 := by
        rw [show (699 : ℕ) = [3, 233].prod by norm_num]
        rw [totient_prod_primes [3, 233] (by decide) (by decide)]
        norm_num
      have hdiv : 464 ∣ 699 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (464 ∣ 699 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 700 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 702 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 703 = 648 := by
        rw [show (703 : ℕ) = [19, 37].prod by norm_num]
        rw [totient_prod_primes [19, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 648 ∣ 703 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (648 ∣ 703 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 704 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 705 = 368 := by
        rw [show (705 : ℕ) = [3, 5, 47].prod by norm_num]
        rw [totient_prod_primes [3, 5, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 368 ∣ 705 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (368 ∣ 705 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 706 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 707 = 600 := by
        rw [show (707 : ℕ) = [7, 101].prod by norm_num]
        rw [totient_prod_primes [7, 101] (by decide) (by decide)]
        norm_num
      have hdiv : 600 ∣ 707 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (600 ∣ 707 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 708 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 710 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 711 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 712 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 713 = 660 := by
        rw [show (713 : ℕ) = [23, 31].prod by norm_num]
        rw [totient_prod_primes [23, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 660 ∣ 713 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (660 ∣ 713 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 714 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 715 = 480 := by
        rw [show (715 : ℕ) = [5, 11, 13].prod by norm_num]
        rw [totient_prod_primes [5, 11, 13] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 715 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 715 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 716 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 717 = 476 := by
        rw [show (717 : ℕ) = [3, 239].prod by norm_num]
        rw [totient_prod_primes [3, 239] (by decide) (by decide)]
        norm_num
      have hdiv : 476 ∣ 717 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (476 ∣ 717 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 718 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 720 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 721 = 612 := by
        rw [show (721 : ℕ) = [7, 103].prod by norm_num]
        rw [totient_prod_primes [7, 103] (by decide) (by decide)]
        norm_num
      have hdiv : 612 ∣ 721 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (612 ∣ 721 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 722 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 723 = 480 := by
        rw [show (723 : ℕ) = [3, 241].prod by norm_num]
        rw [totient_prod_primes [3, 241] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 723 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 723 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 724 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 725 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 726 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 728 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 729 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 730 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 731 = 672 := by
        rw [show (731 : ℕ) = [17, 43].prod by norm_num]
        rw [totient_prod_primes [17, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 672 ∣ 731 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (672 ∣ 731 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 732 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 734 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 735 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 736 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 737 = 660 := by
        rw [show (737 : ℕ) = [11, 67].prod by norm_num]
        rw [totient_prod_primes [11, 67] (by decide) (by decide)]
        norm_num
      have hdiv : 660 ∣ 737 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (660 ∣ 737 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 738 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 740 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 741 = 432 := by
        rw [show (741 : ℕ) = [3, 13, 19].prod by norm_num]
        rw [totient_prod_primes [3, 13, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 741 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 741 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 742 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 744 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 745 = 592 := by
        rw [show (745 : ℕ) = [5, 149].prod by norm_num]
        rw [totient_prod_primes [5, 149] (by decide) (by decide)]
        norm_num
      have hdiv : 592 ∣ 745 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (592 ∣ 745 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 746 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 747 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 748 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 749 = 636 := by
        rw [show (749 : ℕ) = [7, 107].prod by norm_num]
        rw [totient_prod_primes [7, 107] (by decide) (by decide)]
        norm_num
      have hdiv : 636 ∣ 749 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (636 ∣ 749 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 750 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 752 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 753 = 500 := by
        rw [show (753 : ℕ) = [3, 251].prod by norm_num]
        rw [totient_prod_primes [3, 251] (by decide) (by decide)]
        norm_num
      have hdiv : 500 ∣ 753 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (500 ∣ 753 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 754 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 755 = 600 := by
        rw [show (755 : ℕ) = [5, 151].prod by norm_num]
        rw [totient_prod_primes [5, 151] (by decide) (by decide)]
        norm_num
      have hdiv : 600 ∣ 755 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (600 ∣ 755 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 756 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 758 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 759 = 440 := by
        rw [show (759 : ℕ) = [3, 11, 23].prod by norm_num]
        rw [totient_prod_primes [3, 11, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 440 ∣ 759 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (440 ∣ 759 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 760 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 762 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 763 = 648 := by
        rw [show (763 : ℕ) = [7, 109].prod by norm_num]
        rw [totient_prod_primes [7, 109] (by decide) (by decide)]
        norm_num
      have hdiv : 648 ∣ 763 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (648 ∣ 763 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 764 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 765 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 766 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 767 = 696 := by
        rw [show (767 : ℕ) = [13, 59].prod by norm_num]
        rw [totient_prod_primes [13, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 696 ∣ 767 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (696 ∣ 767 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 768 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 770 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 771 = 512 := by
        rw [show (771 : ℕ) = [3, 257].prod by norm_num]
        rw [totient_prod_primes [3, 257] (by decide) (by decide)]
        norm_num
      have hdiv : 512 ∣ 771 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (512 ∣ 771 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 772 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 774 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 775 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 776 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 777 = 432 := by
        rw [show (777 : ℕ) = [3, 7, 37].prod by norm_num]
        rw [totient_prod_primes [3, 7, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 432 ∣ 777 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (432 ∣ 777 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 778 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 779 = 720 := by
        rw [show (779 : ℕ) = [19, 41].prod by norm_num]
        rw [totient_prod_primes [19, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 720 ∣ 779 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (720 ∣ 779 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 780 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 781 = 700 := by
        rw [show (781 : ℕ) = [11, 71].prod by norm_num]
        rw [totient_prod_primes [11, 71] (by decide) (by decide)]
        norm_num
      have hdiv : 700 ∣ 781 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (700 ∣ 781 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 782 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 783 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 784 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 785 = 624 := by
        rw [show (785 : ℕ) = [5, 157].prod by norm_num]
        rw [totient_prod_primes [5, 157] (by decide) (by decide)]
        norm_num
      have hdiv : 624 ∣ 785 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (624 ∣ 785 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 786 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 788 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 789 = 524 := by
        rw [show (789 : ℕ) = [3, 263].prod by norm_num]
        rw [totient_prod_primes [3, 263] (by decide) (by decide)]
        norm_num
      have hdiv : 524 ∣ 789 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (524 ∣ 789 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 790 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 791 = 672 := by
        rw [show (791 : ℕ) = [7, 113].prod by norm_num]
        rw [totient_prod_primes [7, 113] (by decide) (by decide)]
        norm_num
      have hdiv : 672 ∣ 791 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (672 ∣ 791 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 792 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 793 = 720 := by
        rw [show (793 : ℕ) = [13, 61].prod by norm_num]
        rw [totient_prod_primes [13, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 720 ∣ 793 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (720 ∣ 793 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 794 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 795 = 416 := by
        rw [show (795 : ℕ) = [3, 5, 53].prod by norm_num]
        rw [totient_prod_primes [3, 5, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 416 ∣ 795 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (416 ∣ 795 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 796 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 798 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 799 = 736 := by
        rw [show (799 : ℕ) = [17, 47].prod by norm_num]
        rw [totient_prod_primes [17, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 736 ∣ 799 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (736 ∣ 799 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 800 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 801 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 802 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 803 = 720 := by
        rw [show (803 : ℕ) = [11, 73].prod by norm_num]
        rw [totient_prod_primes [11, 73] (by decide) (by decide)]
        norm_num
      have hdiv : 720 ∣ 803 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (720 ∣ 803 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 804 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 805 = 528 := by
        rw [show (805 : ℕ) = [5, 7, 23].prod by norm_num]
        rw [totient_prod_primes [5, 7, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 528 ∣ 805 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (528 ∣ 805 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 806 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 807 = 536 := by
        rw [show (807 : ℕ) = [3, 269].prod by norm_num]
        rw [totient_prod_primes [3, 269] (by decide) (by decide)]
        norm_num
      have hdiv : 536 ∣ 807 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (536 ∣ 807 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 808 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 810 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 812 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 813 = 540 := by
        rw [show (813 : ℕ) = [3, 271].prod by norm_num]
        rw [totient_prod_primes [3, 271] (by decide) (by decide)]
        norm_num
      have hdiv : 540 ∣ 813 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (540 ∣ 813 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 814 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 815 = 648 := by
        rw [show (815 : ℕ) = [5, 163].prod by norm_num]
        rw [totient_prod_primes [5, 163] (by decide) (by decide)]
        norm_num
      have hdiv : 648 ∣ 815 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (648 ∣ 815 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 816 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 817 = 756 := by
        rw [show (817 : ℕ) = [19, 43].prod by norm_num]
        rw [totient_prod_primes [19, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 756 ∣ 817 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (756 ∣ 817 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 818 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 819 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 820 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 822 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 824 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 825 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 826 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 828 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 830 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 831 = 552 := by
        rw [show (831 : ℕ) = [3, 277].prod by norm_num]
        rw [totient_prod_primes [3, 277] (by decide) (by decide)]
        norm_num
      have hdiv : 552 ∣ 831 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (552 ∣ 831 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 832 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 833 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 834 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 835 = 664 := by
        rw [show (835 : ℕ) = [5, 167].prod by norm_num]
        rw [totient_prod_primes [5, 167] (by decide) (by decide)]
        norm_num
      have hdiv : 664 ∣ 835 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (664 ∣ 835 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 836 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 837 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 838 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 840 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 841 29 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 842 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 843 = 560 := by
        rw [show (843 : ℕ) = [3, 281].prod by norm_num]
        rw [totient_prod_primes [3, 281] (by decide) (by decide)]
        norm_num
      have hdiv : 560 ∣ 843 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (560 ∣ 843 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 844 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 845 13 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 846 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 847 11 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 848 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 849 = 564 := by
        rw [show (849 : ℕ) = [3, 283].prod by norm_num]
        rw [totient_prod_primes [3, 283] (by decide) (by decide)]
        norm_num
      have hdiv : 564 ∣ 849 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (564 ∣ 849 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 850 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 851 = 792 := by
        rw [show (851 : ℕ) = [23, 37].prod by norm_num]
        rw [totient_prod_primes [23, 37] (by decide) (by decide)]
        norm_num
      have hdiv : 792 ∣ 851 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (792 ∣ 851 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 852 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 854 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 855 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 856 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 858 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 860 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 861 = 480 := by
        rw [show (861 : ℕ) = [3, 7, 41].prod by norm_num]
        rw [totient_prod_primes [3, 7, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 861 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 861 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 862 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 864 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 865 = 688 := by
        rw [show (865 : ℕ) = [5, 173].prod by norm_num]
        rw [totient_prod_primes [5, 173] (by decide) (by decide)]
        norm_num
      have hdiv : 688 ∣ 865 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (688 ∣ 865 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 866 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 867 17 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 868 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 869 = 780 := by
        rw [show (869 : ℕ) = [11, 79].prod by norm_num]
        rw [totient_prod_primes [11, 79] (by decide) (by decide)]
        norm_num
      have hdiv : 780 ∣ 869 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (780 ∣ 869 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 870 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 871 = 792 := by
        rw [show (871 : ℕ) = [13, 67].prod by norm_num]
        rw [totient_prod_primes [13, 67] (by decide) (by decide)]
        norm_num
      have hdiv : 792 ∣ 871 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (792 ∣ 871 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 872 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 873 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 874 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 875 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 876 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 878 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 879 = 584 := by
        rw [show (879 : ℕ) = [3, 293].prod by norm_num]
        rw [totient_prod_primes [3, 293] (by decide) (by decide)]
        norm_num
      have hdiv : 584 ∣ 879 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (584 ∣ 879 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 880 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 882 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 884 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 885 = 464 := by
        rw [show (885 : ℕ) = [3, 5, 59].prod by norm_num]
        rw [totient_prod_primes [3, 5, 59] (by decide) (by decide)]
        norm_num
      have hdiv : 464 ∣ 885 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (464 ∣ 885 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 886 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 888 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 889 = 756 := by
        rw [show (889 : ℕ) = [7, 127].prod by norm_num]
        rw [totient_prod_primes [7, 127] (by decide) (by decide)]
        norm_num
      have hdiv : 756 ∣ 889 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (756 ∣ 889 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 890 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 891 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 892 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 893 = 828 := by
        rw [show (893 : ℕ) = [19, 47].prod by norm_num]
        rw [totient_prod_primes [19, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 828 ∣ 893 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (828 ∣ 893 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 894 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 895 = 712 := by
        rw [show (895 : ℕ) = [5, 179].prod by norm_num]
        rw [totient_prod_primes [5, 179] (by decide) (by decide)]
        norm_num
      have hdiv : 712 ∣ 895 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (712 ∣ 895 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 896 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 897 = 528 := by
        rw [show (897 : ℕ) = [3, 13, 23].prod by norm_num]
        rw [totient_prod_primes [3, 13, 23] (by decide) (by decide)]
        norm_num
      have hdiv : 528 ∣ 897 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (528 ∣ 897 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 898 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 899 = 840 := by
        rw [show (899 : ℕ) = [29, 31].prod by norm_num]
        rw [totient_prod_primes [29, 31] (by decide) (by decide)]
        norm_num
      have hdiv : 840 ∣ 899 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (840 ∣ 899 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 900 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 901 = 832 := by
        rw [show (901 : ℕ) = [17, 53].prod by norm_num]
        rw [totient_prod_primes [17, 53] (by decide) (by decide)]
        norm_num
      have hdiv : 832 ∣ 901 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (832 ∣ 901 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 902 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 903 = 504 := by
        rw [show (903 : ℕ) = [3, 7, 43].prod by norm_num]
        rw [totient_prod_primes [3, 7, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 504 ∣ 903 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (504 ∣ 903 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 904 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 905 = 720 := by
        rw [show (905 : ℕ) = [5, 181].prod by norm_num]
        rw [totient_prod_primes [5, 181] (by decide) (by decide)]
        norm_num
      have hdiv : 720 ∣ 905 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (720 ∣ 905 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 906 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 908 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 909 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 910 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 912 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 913 = 820 := by
        rw [show (913 : ℕ) = [11, 83].prod by norm_num]
        rw [totient_prod_primes [11, 83] (by decide) (by decide)]
        norm_num
      have hdiv : 820 ∣ 913 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (820 ∣ 913 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 914 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 915 = 480 := by
        rw [show (915 : ℕ) = [3, 5, 61].prod by norm_num]
        rw [totient_prod_primes [3, 5, 61] (by decide) (by decide)]
        norm_num
      have hdiv : 480 ∣ 915 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (480 ∣ 915 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 916 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 917 = 780 := by
        rw [show (917 : ℕ) = [7, 131].prod by norm_num]
        rw [totient_prod_primes [7, 131] (by decide) (by decide)]
        norm_num
      have hdiv : 780 ∣ 917 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (780 ∣ 917 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 918 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 920 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 921 = 612 := by
        rw [show (921 : ℕ) = [3, 307].prod by norm_num]
        rw [totient_prod_primes [3, 307] (by decide) (by decide)]
        norm_num
      have hdiv : 612 ∣ 921 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (612 ∣ 921 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 922 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 923 = 840 := by
        rw [show (923 : ℕ) = [13, 71].prod by norm_num]
        rw [totient_prod_primes [13, 71] (by decide) (by decide)]
        norm_num
      have hdiv : 840 ∣ 923 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (840 ∣ 923 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 924 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 925 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 926 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 927 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 928 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 930 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 931 7 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 932 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 933 = 620 := by
        rw [show (933 : ℕ) = [3, 311].prod by norm_num]
        rw [totient_prod_primes [3, 311] (by decide) (by decide)]
        norm_num
      have hdiv : 620 ∣ 933 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (620 ∣ 933 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 934 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 935 = 640 := by
        rw [show (935 : ℕ) = [5, 11, 17].prod by norm_num]
        rw [totient_prod_primes [5, 11, 17] (by decide) (by decide)]
        norm_num
      have hdiv : 640 ∣ 935 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (640 ∣ 935 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 936 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 938 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 939 = 624 := by
        rw [show (939 : ℕ) = [3, 313].prod by norm_num]
        rw [totient_prod_primes [3, 313] (by decide) (by decide)]
        norm_num
      have hdiv : 624 ∣ 939 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (624 ∣ 939 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 940 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 942 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 943 = 880 := by
        rw [show (943 : ℕ) = [23, 41].prod by norm_num]
        rw [totient_prod_primes [23, 41] (by decide) (by decide)]
        norm_num
      have hdiv : 880 ∣ 943 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (880 ∣ 943 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 944 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 945 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 946 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 948 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 949 = 864 := by
        rw [show (949 : ℕ) = [13, 73].prod by norm_num]
        rw [totient_prod_primes [13, 73] (by decide) (by decide)]
        norm_num
      have hdiv : 864 ∣ 949 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (864 ∣ 949 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 950 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 951 = 632 := by
        rw [show (951 : ℕ) = [3, 317].prod by norm_num]
        rw [totient_prod_primes [3, 317] (by decide) (by decide)]
        norm_num
      have hdiv : 632 ∣ 951 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (632 ∣ 951 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 952 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 954 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 955 = 760 := by
        rw [show (955 : ℕ) = [5, 191].prod by norm_num]
        rw [totient_prod_primes [5, 191] (by decide) (by decide)]
        norm_num
      have hdiv : 760 ∣ 955 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (760 ∣ 955 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 956 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 957 = 560 := by
        rw [show (957 : ℕ) = [3, 11, 29].prod by norm_num]
        rw [totient_prod_primes [3, 11, 29] (by decide) (by decide)]
        norm_num
      have hdiv : 560 ∣ 957 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (560 ∣ 957 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 958 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 959 = 816 := by
        rw [show (959 : ℕ) = [7, 137].prod by norm_num]
        rw [totient_prod_primes [7, 137] (by decide) (by decide)]
        norm_num
      have hdiv : 816 ∣ 959 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (816 ∣ 959 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 960 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 961 31 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 962 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 963 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 964 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 965 = 768 := by
        rw [show (965 : ℕ) = [5, 193].prod by norm_num]
        rw [totient_prod_primes [5, 193] (by decide) (by decide)]
        norm_num
      have hdiv : 768 ∣ 965 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (768 ∣ 965 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 966 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 968 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 969 = 576 := by
        rw [show (969 : ℕ) = [3, 17, 19].prod by norm_num]
        rw [totient_prod_primes [3, 17, 19] (by decide) (by decide)]
        norm_num
      have hdiv : 576 ∣ 969 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (576 ∣ 969 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 970 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 972 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 973 = 828 := by
        rw [show (973 : ℕ) = [7, 139].prod by norm_num]
        rw [totient_prod_primes [7, 139] (by decide) (by decide)]
        norm_num
      have hdiv : 828 ∣ 973 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (828 ∣ 973 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 974 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 975 5 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 976 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 978 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 979 = 880 := by
        rw [show (979 : ℕ) = [11, 89].prod by norm_num]
        rw [totient_prod_primes [11, 89] (by decide) (by decide)]
        norm_num
      have hdiv : 880 ∣ 979 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (880 ∣ 979 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 980 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 981 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 982 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 984 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 985 = 784 := by
        rw [show (985 : ℕ) = [5, 197].prod by norm_num]
        rw [totient_prod_primes [5, 197] (by decide) (by decide)]
        norm_num
      have hdiv : 784 ∣ 985 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (784 ∣ 985 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 986 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 987 = 552 := by
        rw [show (987 : ℕ) = [3, 7, 47].prod by norm_num]
        rw [totient_prod_primes [3, 7, 47] (by decide) (by decide)]
        norm_num
      have hdiv : 552 ∣ 987 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (552 ∣ 987 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 988 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 989 = 924 := by
        rw [show (989 : ℕ) = [23, 43].prod by norm_num]
        rw [totient_prod_primes [23, 43] (by decide) (by decide)]
        norm_num
      have hdiv : 924 ∣ 989 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (924 ∣ 989 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 990 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 992 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 993 = 660 := by
        rw [show (993 : ℕ) = [3, 331].prod by norm_num]
        rw [totient_prod_primes [3, 331] (by decide) (by decide)]
        norm_num
      have hdiv : 660 ∣ 993 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (660 ∣ 993 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 994 hw.2.2 (by norm_num)
      omega
    · intro hw
      have hphi : Nat.totient 995 = 792 := by
        rw [show (995 : ℕ) = [5, 199].prod by norm_num]
        rw [totient_prod_primes [5, 199] (by decide) (by decide)]
        norm_num
      have hdiv : 792 ∣ 995 - 1 := by simpa [hphi] using hw.2.2
      have hnot : ¬ (792 ∣ 995 - 1) := by norm_num
      exact hnot hdiv
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 996 hw.2.2 (by norm_num)
      omega
    · exfalso
      exact hp (by norm_num [Nat.Prime])
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 998 hw.2.2 (by norm_num)
      omega
    · intro hw
      exfalso
      exact lehmer_composite_must_be_squarefree 999 3 hw.2.2 (by norm_num) ⟨by norm_num [Nat.Prime], by norm_num⟩
    · intro hw
      obtain ⟨k, hk⟩ := lehmer_composite_must_be_odd 1000 hw.2.2 (by norm_num)
      omega

#eval "LehmerTotientBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
