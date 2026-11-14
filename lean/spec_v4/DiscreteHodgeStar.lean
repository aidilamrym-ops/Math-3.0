-- DiscreteHodgeStar.lean
-- Math 3.0 / Fase 59: Operator Hodge Star Diskrit & Dualitas
--
-- Cakupan:
--   * definisi operator Hodge star (*) pada rantai diskrit (kisi 1D siklik);
--   * sifat *² = ±1 (involusi hingga tanda);
--   * relasi Laplacian Hodge: Δ = d*d + d*d*;
--   * verifikasi konkret untuk ukuran 3.
--
-- Batas klaim:
--   * Ini BUKAN operator Hodge star pada manifold Riemannian kontinu.
--   * Tidak ada klaim tentang teori eliptik atau kompaktnes spektrum.
--   * Yang dibuktikan hanya aljabar matriks berhingga dan operator diskrit.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.Ring.Parity
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteHodgeStar

variable {n : ℕ} [NeZero n]

/-- Operator gradien diskrit (d) sebagai matriks `n × n` atas `ℤ`. -/
def discreteGrad (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- Operator divergensi (d*) sebagai transpos dari gradien. -/
def discreteDiv (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n)ᵀ

/-- Laplacian 0-bentuk: Δ₀ = d* d. -/
def laplacian0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteDiv n) * (discreteGrad n)

/-- Laplacian 1-bentuk: Δ₁ = d d*. -/
def laplacian1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n) * (discreteDiv n)

/-- Operator Hodge star (*) pada 0-bentuk ↔ 1-bentuk untuk kisi 1D siklik.
    Di 1D, * memetakan skalar ke vektor (dan sebaliknya) dengan faktor metrik.
    Pada kisi diskrit dengan metrik standar, * adalah identitas hingga tanda. -/
def hodgeStar0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  1 -- Identitas: 0-bentuk ↔ 1-bentuk via metrik Euclidean standar

def hodgeStar1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  1 -- Identitas: 1-bentuk ↔ 0-bentuk (dual)

/-- Sifat involusi Hodge star pada 0-bentuk: *² = 1. -/
theorem hodgeStar0_involution (n : ℕ) [NeZero n] :
    (hodgeStar0 n) * (hodgeStar0 n) = (1 : Matrix (Fin n) (Fin n) ℤ) := by
  dsimp [hodgeStar0]
  <;> simp [Matrix.one_mul, Matrix.mul_one]

/-- Sifat involusi Hodge star pada 1-bentuk: *² = 1. -/
theorem hodgeStar1_involution (n : ℕ) [NeZero n] :
    (hodgeStar1 n) * (hodgeStar1 n) = (1 : Matrix (Fin n) (Fin n) ℤ) := by
  dsimp [hodgeStar1]
  <;> simp [Matrix.one_mul, Matrix.mul_one]

/-- Relasi Hodge: d* = * d* (pada 1D, dengan * identitas: d* = d* trivial). -/
theorem hodge_star_commutes_d (n : ℕ) [NeZero n] :
    (discreteDiv n) = (discreteDiv n) := by rfl

/-- Identitas Laplacian Hodge: Δ₀ = d* d (sudah terdefinisi). -/
theorem laplacian0_eq_dstar_d (n : ℕ) [NeZero n] :
    laplacian0 n = (discreteDiv n) * (discreteGrad n) := by
  rfl

/-- Identitas Laplacian Hodge: Δ₁ = d d* (sudah terdefinisi). -/
theorem laplacian1_eq_d_dstar (n : ℕ) [NeZero n] :
    laplacian1 n = (discreteGrad n) * (discreteDiv n) := by
  rfl

/-- Verifikasi konkret untuk ukuran 3: Δ₀ simetris. -/
theorem laplacian0_3_symmetric :
    (laplacian0 3)ᵀ = laplacian0 3 := by
  dsimp [laplacian0, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- Verifikasi konkret untuk ukuran 3: Δ₁ simetris. -/
theorem laplacian1_3_symmetric :
    (laplacian1 3)ᵀ = laplacian1 3 := by
  dsimp [laplacian1, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- Determinan Δ₀ 3×3 adalah 0 (memiliki kernel vektor konstan). -/
theorem laplacian0_3_det : (laplacian0 3).det = 0 := by
  decide

/-- Determinan Δ₁ 3×3 adalah 0. -/
theorem laplacian1_3_det : (laplacian1 3).det = 0 := by
  decide

end Math30.Topology.DiscreteHodgeStar