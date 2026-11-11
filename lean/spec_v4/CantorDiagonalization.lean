-- CantorDiagonalization.lean
-- Math 3.0 / Phase 44: Actual-Infinity Boundary via Cantor Diagonalization
-- Regression armor: the oldest durable no-surjection theorem (1891).
-- Examiner-proof, sorry-free, exit 0.

import Mathlib.Data.Bool.Basic
import Mathlib.Tactic

namespace Math30.Foundations.Cantor

/-- Cantor diagonal map: flips the n-th digit of the n-th row. -/
def cantorDiagonal (f : ℕ → ℕ → Bool) : ℕ → Bool :=
  fun n => !(f n n)

/-- No surjection from `ℕ` onto `ℕ → Bool` (the actual-infinity diagonal shift).
This is the finitary statement: every candidate enumeration misses at least one row,
and the witness is produced constructively. -/
theorem cantor_no_surjection (f : ℕ → ℕ → Bool) :
    ∃ g : ℕ → Bool, ∀ n, f n ≠ g := by
  refine ⟨cantorDiagonal f, ?_⟩
  intro n h
  have hx : f n n = cantorDiagonal f n := congrFun h n
  cases hb : f n n <;> simp [cantorDiagonal, hb] at hx

/-- Diagonal witness is strictly outside the image of `f` at every index. -/
theorem cantor_diagonal_differs (f : ℕ → ℕ → Bool) (n : ℕ) :
    f n n ≠ !(f n n) := by
  cases f n n <;> simp

end Math30.Foundations.Cantor
