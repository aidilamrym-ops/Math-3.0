import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic

/-!
  GoldbachBoundedVerification.lean
  Math 3.0 Batch 20: range expansion (Goldbach 100 → 500).

  Scope: `goldbach_bounded_up_to_100` and `goldbach_bounded_up_to_500` are
  FORMAL_FINITE_THEOREMs. `goldbach_even_gt_six_odd_primes` is a structural
  FORMAL_GENERAL_THEOREM about decompositions of even n > 6.

  The full Goldbach Conjecture — every even n ≥ 4 is a sum of two primes —
  remains OPEN. No density or asymptotic claim is made.
-/

namespace Math30.Certificates

/-- Definition of Goldbach decomposability for an even integer. -/
def IsGoldbachDecomposable (n : ℕ) : Prop :=
  ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ p + q = n

/-- Bounded deterministic verification: for every even n with 4 ≤ n ≤ 100, n is Goldbach decomposable. -/
theorem goldbach_bounded_up_to_100 (n : ℕ) (hn : 4 ≤ n ∧ n ≤ 100 ∧ n % 2 = 0) : IsGoldbachDecomposable n := by
  rcases hn with ⟨h4, h100, heven⟩
  interval_cases n
  all_goals
    try omega
    (try { use 2, 2; norm_num [Nat.Prime] })
    (try { use 3, 3; norm_num [Nat.Prime] })
    (try { use 3, 5; norm_num [Nat.Prime] })
    (try { use 3, 7; norm_num [Nat.Prime] })
    (try { use 5, 7; norm_num [Nat.Prime] })
    (try { use 3, 11; norm_num [Nat.Prime] })
    (try { use 3, 13; norm_num [Nat.Prime] })
    (try { use 5, 13; norm_num [Nat.Prime] })
    (try { use 3, 17; norm_num [Nat.Prime] })
    (try { use 3, 19; norm_num [Nat.Prime] })
    (try { use 5, 19; norm_num [Nat.Prime] })
    (try { use 3, 23; norm_num [Nat.Prime] })
    (try { use 5, 23; norm_num [Nat.Prime] })
    (try { use 7, 23; norm_num [Nat.Prime] })
    (try { use 3, 29; norm_num [Nat.Prime] })
    (try { use 3, 31; norm_num [Nat.Prime] })
    (try { use 5, 31; norm_num [Nat.Prime] })
    (try { use 7, 31; norm_num [Nat.Prime] })
    (try { use 3, 37; norm_num [Nat.Prime] })
    (try { use 5, 37; norm_num [Nat.Prime] })
    (try { use 3, 41; norm_num [Nat.Prime] })
    (try { use 3, 43; norm_num [Nat.Prime] })
    (try { use 5, 43; norm_num [Nat.Prime] })
    (try { use 3, 47; norm_num [Nat.Prime] })
    (try { use 5, 47; norm_num [Nat.Prime] })
    (try { use 7, 47; norm_num [Nat.Prime] })
    (try { use 3, 53; norm_num [Nat.Prime] })
    (try { use 5, 53; norm_num [Nat.Prime] })
    (try { use 7, 53; norm_num [Nat.Prime] })
    (try { use 3, 59; norm_num [Nat.Prime] })
    (try { use 3, 61; norm_num [Nat.Prime] })
    (try { use 5, 61; norm_num [Nat.Prime] })
    (try { use 7, 61; norm_num [Nat.Prime] })
    (try { use 3, 67; norm_num [Nat.Prime] })
    (try { use 5, 67; norm_num [Nat.Prime] })
    (try { use 7, 67; norm_num [Nat.Prime] })
    (try { use 3, 73; norm_num [Nat.Prime] })
    (try { use 5, 73; norm_num [Nat.Prime] })
    (try { use 7, 73; norm_num [Nat.Prime] })
    (try { use 3, 79; norm_num [Nat.Prime] })
    (try { use 5, 79; norm_num [Nat.Prime] })
    (try { use 3, 83; norm_num [Nat.Prime] })
    (try { use 5, 83; norm_num [Nat.Prime] })
    (try { use 7, 83; norm_num [Nat.Prime] })
    (try { use 3, 89; norm_num [Nat.Prime] })
    (try { use 5, 89; norm_num [Nat.Prime] })
    (try { use 7, 89; norm_num [Nat.Prime] })
    (try { use 19, 79; norm_num [Nat.Prime] })
    (try { use 3, 97; norm_num [Nat.Prime] })

/-- Bounded deterministic verification: for every even n with 4 ≤ n ≤ 500,
    n is Goldbach decomposable. -/
theorem goldbach_bounded_up_to_500 (n : ℕ)
    (hn : 4 ≤ n ∧ n ≤ 500 ∧ n % 2 = 0) : IsGoldbachDecomposable n := by
  obtain ⟨h4, h500, heven⟩ := hn
  obtain ⟨m, rfl⟩ := Nat.dvd_of_mod_eq_zero heven
  have hm2 : 2 ≤ m := by omega
  have hm250 : m ≤ 250 := by omega
  interval_cases m
  · exact ⟨2, 2, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 3, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 5, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 7, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 7, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 11, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 13, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 13, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 17, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 19, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 19, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 23, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 23, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 23, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 29, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 31, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 31, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 31, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 37, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 37, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 41, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 43, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 43, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 47, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 47, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 47, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 53, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 53, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 53, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 59, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 61, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 61, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 61, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 67, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 67, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 71, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 73, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 73, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 73, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 79, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 79, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 83, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 83, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 83, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 89, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 89, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 89, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 79, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 97, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 97, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 101, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 103, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 103, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 107, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 109, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 109, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 113, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 113, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 113, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 109, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 113, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 113, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 109, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 127, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 127, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 131, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 131, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 131, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 137, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 139, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 139, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 139, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 137, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 139, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 149, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 151, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 151, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 151, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 157, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 157, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 157, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 163, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 163, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 167, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 167, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 167, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 173, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 173, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 173, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 179, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 181, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 181, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 181, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 179, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 181, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 191, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 193, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 193, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 197, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 199, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 199, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 199, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 197, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 199, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 199, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 211, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 211, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 211, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨23, 197, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 211, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 211, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 223, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 223, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 227, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 229, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 229, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 233, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 233, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 233, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 239, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 241, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 241, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 241, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 239, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 241, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 251, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 251, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 251, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 257, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 257, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 257, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 263, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 263, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 263, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 269, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 271, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 271, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 271, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 277, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 277, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 281, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 283, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 283, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 283, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 281, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 283, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 293, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 293, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 293, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 283, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 293, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 293, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨31, 277, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 307, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 307, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 311, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 313, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 313, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 313, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 313, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 331, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 331, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 331, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 337, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 337, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 337, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨29, 317, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 337, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 347, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 349, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 349, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 353, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 353, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 353, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 359, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 359, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 359, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 349, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 367, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 367, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 367, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 373, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 373, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 373, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 379, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 379, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 383, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 383, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 383, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 389, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 389, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 389, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 379, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 397, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 397, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 401, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 401, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 401, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 397, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 409, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 409, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 409, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨17, 401, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 409, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 419, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 421, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 421, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 421, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 419, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 421, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 431, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 433, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 433, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 433, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 439, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 439, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 443, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 443, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 443, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 449, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 449, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 449, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨19, 439, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 457, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 457, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 461, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 463, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 463, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 467, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 467, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 467, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 463, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨11, 467, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 467, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 479, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 479, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 479, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨31, 457, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 487, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 487, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨3, 491, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨5, 491, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨7, 491, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩
  · exact ⟨13, 487, by norm_num [Nat.Prime], by norm_num [Nat.Prime], by norm_num⟩

/-- For any even n > 6, any Goldbach decomposition (p + q = n) must have p ≠ 2 and q ≠ 2. -/
theorem goldbach_even_gt_six_odd_primes (n : ℕ) (hn : 6 < n ∧ n % 2 = 0) (p q : ℕ) (hp : Nat.Prime p) (hq : Nat.Prime q) (hsum : p + q = n) : p ≠ 2 ∧ q ≠ 2 := by
  have h₁ : p ≠ 2 := by
    intro h
    have h₂ : p = 2 := h
    have h₃ : q = n - 2 := by
      have h₄ : p + q = n := hsum
      omega
    have h₅ : q = 2 := by
      have h₅₁ : q % 2 = 0 := by
        have h₅₂ : n % 2 = 0 := hn.2
        have h₅₃ : p = 2 := h₂
        omega
      have h₅₂ : Nat.Prime q := hq
      have h₅₃ : q = 2 := by
        have h₅₄ := Nat.Prime.eq_two_or_odd h₅₂
        cases h₅₄ with
        | inl h₅₄ => exact h₅₄
        | inr h₅₄ =>
          exfalso
          have h₅₅ : q % 2 = 1 := h₅₄
          omega
      exact h₅₃
    have h₆ : n = 4 := by
      have h₆₁ : p = 2 := h₂
      have h₆₂ : q = 2 := h₅
      omega
    omega
  have h₂ : q ≠ 2 := by
    intro h
    have h₃ : q = 2 := h
    have h₄ : p = n - 2 := by
      have h₅ : p + q = n := hsum
      omega
    have h₆ : p = 2 := by
      have h₆₁ : p % 2 = 0 := by
        have h₆₂ : n % 2 = 0 := hn.2
        have h₆₃ : q = 2 := h₃
        omega
      have h₆₂ : Nat.Prime p := hp
      have h₆₃ : p = 2 := by
        have h₆₄ := Nat.Prime.eq_two_or_odd h₆₂
        cases h₆₄ with
        | inl h₆₄ => exact h₆₄
        | inr h₆₄ =>
          exfalso
          have h₆₅ : p % 2 = 1 := h₆₄
          omega
      exact h₆₃
    have h₇ : n = 4 := by
      have h₇₁ : p = 2 := h₆
      have h₇₂ : q = 2 := h₃
      omega
    omega
  exact ⟨h₁, h₂⟩

#eval "GoldbachBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates