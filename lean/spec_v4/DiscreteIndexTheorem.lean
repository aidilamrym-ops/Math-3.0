-- DiscreteIndexTheorem.lean
-- Math 3.0 / Fase 56: Teorema Indeks Diskrit pada Kisi Hingga
--
-- Cakupan:
--   * operator diferensiasi diskrit (maju/mundur) pada grid berhingga ℤ/Nℤ;
--   * definisi operator Dirac diskrit 2×2;
--   * witness kernel eksplisit: spinor konstan pada siklus-3 dihancurkan
--     oleh operator Dirac.
--
-- Batas klaim:
--   * Ini BUKAN teorema indeks Atiyah-Singer dan BUKAN indeks operator
--     eliptik pada manifold Riemannian kontinu.
--   * Tidak ada klaim tentang geometri diferensial, spinor kontinu, atau
--     kategori topologi manifold mulus.
--   * Kesamaan indeks analitik = indeks topologi TIDAK dibuktikan di sini;
--     yang dibuktikan hanya aljabar matriks berhingga dan satu witness kernel.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Algebra.Ring.Parity
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteIndex

variable {n : ℕ} [NeZero n]

/-- Operator gradien diskrit (selisih maju) sebagai matriks `n × n` atas `ℤ`. -/
def discreteGrad (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- Contoh konkret operator gradien diskrit untuk rank 3. -/
def grad3 : Matrix (Fin 3) (Fin 3) ℤ := discreteGrad 3

/-- Determinan operator gradien siklik 3×3 adalah 0. -/
theorem grad3_det : grad3.det = 0 := by
  decide

/-- Operator divergensi diskrit sebagai transpos dari gradien. -/
def discreteDiv (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n)ᵀ

/-- Operator Dirac diskrit 2×2 berukuran `(Fin n × Bool) × (Fin n × Bool)`. -/
def discreteDirac (n : ℕ) [NeZero n] : Matrix (Fin n × Bool) (Fin n × Bool) ℤ :=
  of fun p q =>
    match p.2, q.2 with
    | false, true  => (discreteDiv n) p.1 q.1
    | true,  false => (discreteGrad n) p.1 q.1
    | false, false => 0
    | true,  true  => 0

/-- Sifat simetri off-diagonal dari operator Dirac diskrit. -/
theorem discreteDirac_off_diagonal (p q : Fin n × Bool) (hpq : p.2 = q.2) :
    discreteDirac n p q = 0 := by
  rcases p with ⟨i, b1⟩
  rcases q with ⟨j, b2⟩
  dsimp [discreteDirac]
  cases b1 <;> cases b2 <;> simp_all

/-- Spinor konstan pada siklus-3: komponen `false` bernilai 1, komponen
`true` bernilai 0. -/
def constantSpinor : Fin 3 × Bool → ℤ := fun p => if p.2 = false then 1 else 0

/-- Witness kernel: operator Dirac 3-siklus menghancurkan spinor konstan.
Ini adalah isi analitik yang dapat dibuktikan; bukan kesamaan indeks. -/
theorem discreteDirac_constantSpinor_kernel (p : Fin 3 × Bool) :
    (discreteDirac 3).mulVec constantSpinor p = 0 := by
  rcases p with ⟨i, b⟩
  cases b
  · rw [Matrix.mulVec, dotProduct]
    apply Finset.sum_eq_zero
    intro q _
    rcases q with ⟨j, c⟩
    cases c <;> simp [discreteDirac, constantSpinor]
  · fin_cases i <;> decide

end Math30.Topology.DiscreteIndex
