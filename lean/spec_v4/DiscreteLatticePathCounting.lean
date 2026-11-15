-- DiscreteLatticePathCounting.lean
-- Math 3.0 / Fase 73: Penghitungan Jalan Kisi (Lattice Path Counting)

import Mathlib.Tactic

namespace Math30.Combinatorics.LatticePath

def binomial : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ => 0
  | n+1, k+1 => binomial n k + binomial n (k+1)

theorem pascal_identity (n k : Nat) :
  binomial (n+1) (k+1) = binomial n k + binomial n (k+1) := by
  rfl

theorem binomial_zero_right (n : Nat) : binomial n 0 = 1 := by
  cases n <;> rfl

theorem binomial_one_one : binomial 1 1 = 1 := by
  rfl

end Math30.Combinatorics.LatticePath
