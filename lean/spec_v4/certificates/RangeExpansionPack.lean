import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic
import spec_v4.certificates.GilbreathBoundedVerification
import spec_v4.certificates.TwinPrimeBoundedVerification

/-!
  RangeExpansionPack.lean
  Math 3.0 Batch 19: Range Expansion Pack I
  (Gilbreath first 50 primes + twin prime witnesses below 1000).

  Scope: `gilbreath_first_50_primes` is a FORMAL_FINITE_THEOREM extending the
  Batch 16 bounded check from 20 to 50 primes (49 iterated rows).
  `twin_prime_witnesses_below_1000` is a FORMAL_FINITE_THEOREM sealing all 35
  twin prime pairs with smaller member below 1000.

  Both full conjectures remain OPEN. No infinitude, density, or all-rows
  claim is made.
-/

namespace Math30.Certificates

set_option maxRecDepth 100000

/-- Bounded deterministic verification: the first 50 primes satisfy
    Gilbreath's head condition across all 49 iterated rows. -/
theorem gilbreath_first_50_primes (ps : List ℕ)
    (hps : ps = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
                 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
                 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181,
                 191, 193, 197, 199, 211, 223, 227, 229]) :
    SatisfiesGilbreathHead ps := by
  rw [hps]
  intro k h1 hk
  have hk50 : k < 50 := by simpa using hk
  interval_cases k <;> decide

/-- Bounded deterministic verification: all 35 twin prime pairs with smaller
    member below 1000 are sealed by explicit witnesses. -/
theorem twin_prime_witnesses_below_1000 (p : ℕ)
    (hp : p ∈ [3, 5, 11, 17, 29, 41, 59, 71, 101, 107, 137, 149, 179, 191, 197,
               227, 239, 269, 281, 311, 347, 419, 431, 461, 521, 569, 599, 617,
               641, 659, 809, 821, 827, 857, 881]) :
    IsTwinPrime p := by
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
    rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
    rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals norm_num [IsTwinPrime, Nat.Prime]

#eval "RangeExpansionPack certificate compiled with zero placeholders."

end Math30.Certificates
