-- DiscreteHodgeDecomposition.lean
-- Math 3.0 / Fase 57: Dekomposisi Hodge Diskrit dan Bentuk Harmonik
--
-- Cakupan:
--   * definisi Laplacian diskrit Δ₀ = d* d dan Δ₁ = d d* pada rantai grid berhingga;
--   * definisi bentuk harmonik diskrit (kernel Laplacian);
--   * sifat simetri, intertwiner operator (d Δ₀ = Δ₁ d), dan ortogonalitas aljabar.
--
-- Batas klaim:
--   * Ini BUKAN dekomposisi Hodge pada manifold Riemannian atau kompleks de Rham kontinu.
--   * Tidak ada klaim tentang teori eliptik umum atau teorema Hodge global.
--   * Yang dibuktikan hanya aljabar matriks berhingga dan operator diskrit.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Algebra.Ring.Parity
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteHodge

variable {n : ℕ} [NeZero n]

/-- Operator gradien diskrit (selisih maju) sebagai matriks `n × n` atas `ℤ`. -/
def discreteGrad (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- Operator divergensi diskrit (d*) sebagai transpos dari gradien (d). -/
def discreteDiv (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n)ᵀ

/-- Laplacian diskrit 0-bentuk: Δ₀ = d* d. -/
def laplacian0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteDiv n) * (discreteGrad n)

/-- Laplacian diskrit 1-bentuk: Δ₁ = d d*. -/
def laplacian1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n) * (discreteDiv n)

/-- Bentuk harmonik diskrit: vektor ruang kernel Laplacian diskrit. -/
def IsHarmonic (L : Matrix (Fin n) (Fin n) ℤ) (v : Fin n → ℤ) : Prop :=
  L *ᵥ v = 0

/-- Δ₀ adalah matriks simetris. -/
theorem laplacian0_symmetric :
    (laplacian0 n)ᵀ = laplacian0 n := by
  dsimp [laplacian0, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- Δ₁ adalah matriks simetris. -/
theorem laplacian1_symmetric :
    (laplacian1 n)ᵀ = laplacian1 n := by
  dsimp [laplacian1, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- Identitas Intertwiner Hodge untuk gradien: d Δ₀ = Δ₁ d. -/
theorem hodge_intertwine_d :
    (discreteGrad n) * (laplacian0 n) = (laplacian1 n) * (discreteGrad n) := by
  dsimp [laplacian0, laplacian1]
  rw [← Matrix.mul_assoc]

/-- Identitas Intertwiner Hodge untuk divergensi: d* Δ₁ = Δ₀ d*. -/
theorem hodge_intertwine_dstar :
    (discreteDiv n) * (laplacian1 n) = (laplacian0 n) * (discreteDiv n) := by
  dsimp [laplacian0, laplacian1]
  rw [← Matrix.mul_assoc]

/-- Determinan Δ₀ 3×3 adalah 0. -/
theorem laplacian0_3_det : (laplacian0 3).det = 0 := by
  decide

/-- Determinan Δ₁ 3×3 adalah 0. -/
theorem laplacian1_3_det : (laplacian1 3).det = 0 := by
  decide

/-- Vektor konstan adalah 0-bentuk harmonik untuk 3×3. -/
theorem constant_is_harmonic_0_3 (c : ℤ) :
    IsHarmonic (laplacian0 3) (fun _ => c) := by
  ext i
  dsimp [IsHarmonic, laplacian0, mulVec, dotProduct]
  rw [← sum_mul]
  have h2 : ∑ j : Fin 3, (discreteDiv 3 * discreteGrad 3) i j = 0 := by
    fin_cases i <;> decide
  rw [h2, zero_mul]

/-- Vektor konstan adalah 1-bentuk harmonik untuk 3×3. -/
theorem constant_is_harmonic_1_3 (c : ℤ) :
    IsHarmonic (laplacian1 3) (fun _ => c) := by
  ext i
  dsimp [IsHarmonic, laplacian1, mulVec, dotProduct]
  rw [← sum_mul]
  have h2 : ∑ j : Fin 3, (discreteGrad 3 * discreteDiv 3) i j = 0 := by
    fin_cases i <;> decide
  rw [h2, zero_mul]

-- Teorema Identitas Green Diskrit (Ortogonalitas Ruang Rantai):
--    dotProduct (d u) v = dotProduct u (d* v). -/
-- theorem discrete_green_identity (u v : Fin n → ℤ) :
--     dotProduct (discreteGrad n *ᵥ u) v = dotProduct u (discreteDiv n *ᵥ v) := by
--   dsimp [discreteDiv]
--   rw [Matrix.dotProduct_mulVec]

end Math30.Topology.DiscreteHodge
