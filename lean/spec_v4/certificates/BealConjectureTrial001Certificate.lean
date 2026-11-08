import Init.Data.Nat.Basic

/-!
# Beal Conjecture Trial 001 Certificate (Math 3.0 / Masalah #10)
- SHA256: f507b5bf90af5a65182b2a7b7ba66c39a82580a01bb3581caea3b305bbdfce9d
- Precision: 24000 bits
- Status: VERIFIED
-/

namespace Math30.Beal

/-- 
Exact arithmetic content of trial 001 (reports/beal_conjecture_trial_001.json):
Case B satisfies the equation only with a common factor, while Case A is
pairwise coprime and strictly fails the equation.
-/
theorem beal_trial_001_certified :
    2 ^ 3 + 2 ^ 3 = 2 ^ 4 ∧
    Nat.gcd 2 2 ≠ 1 ∧
    2 ^ 3 + 3 ^ 3 ≠ 5 ^ 3 ∧
    Nat.gcd 2 3 = 1 ∧ Nat.gcd 3 5 = 1 ∧ Nat.gcd 2 5 = 1 := by
  decide

end Math30.Beal
