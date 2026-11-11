-- EuclidFermatArmor.lean
-- Math 3.0 / Phase 48: Euclid infinitude + finite Fermat residue checks
-- Bounded regression armor: Euclid's theorem is imported from Mathlib and re-exported
-- through this certificate; the Fermat entries are machine-checked finite instances,
-- not a full formalization of Fermat's little theorem.

import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Tactic

namespace Math30.NumberTheory.Foundation

/-- Euclid's theorem: for every bound there is a larger prime. -/
theorem euclid_infinite_primes (n : ℕ) : ∃ p, n < p ∧ Nat.Prime p := by
  obtain ⟨p, hp, hprime⟩ := Nat.exists_infinite_primes (n + 1)
  exact ⟨p, Nat.lt_of_succ_le hp, hprime⟩

/-- Fermat residue check at p = 5, a = 2. -/
theorem fermat_five_two : 2 ^ 5 % 5 = 2 % 5 := by decide

/-- Fermat residue check at p = 7, a = 3. -/
theorem fermat_seven_three : 3 ^ 7 % 7 = 3 % 7 := by decide

/-- Fermat residue check at p = 11, a = 5. -/
theorem fermat_eleven_five : 5 ^ 11 % 11 = 5 % 11 := by decide

end Math30.NumberTheory.Foundation
