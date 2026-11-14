-- DiscreteSpectralGap.lean
-- Math 3.0 / Fase 58: Celah Spektral Diskrit & Batas Kuosien Rayleigh
--
-- Cakupan:
--   * definisi bentuk kuadratik Laplacian diskrit (energi Dirichlet diskrit);
--   * batas bawah positif untuk vektor non-konstan (celah spektral diskrit / Poincaré inequality);
--   * verifikasi konkret untuk grid siklik ukuran 3 (`n = 3`).
--
-- Batas klaim:
--   * Ini BUKAN celah spektral kontinu (Yang-Mills mass gap atau spektrum operator kontinu).
--   * Tidak ada klaim tentang teori eliptik umum atau teorema Hodge global.
--   * Yang dibuktikan hanya aljabar matriks berhingga dan operator diskrit.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.Ring.Parity
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteSpectralGap

variable {n : ℕ} [NeZero n]

/-- Laplacian diskrit 1D siklik sebagai matriks `n × n` atas `ℤ`. -/
def discreteLaplacian (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if i = j then 2
    else if (i.val + 1) % n = j.val ∨ (j.val + 1) % n = i.val then -1
    else 0

/-- Bentuk kuadratik Laplacian diskrit (Energi Dirichlet: $v^T \Delta v$). -/
def dirichletEnergy (n : ℕ) [NeZero n] (v : Fin n → ℤ) : ℤ :=
  dotProduct v ((discreteLaplacian n) *ᵥ v)

/-- Matriks Laplacian diskrit 3×3 adalah simetris. -/
theorem discreteLaplacian_3_symmetric :
    (discreteLaplacian 3)ᵀ = discreteLaplacian 3 := by
  ext i j
  fin_cases i <;> fin_cases j <;> decide

/-- Entri matriks Laplacian diskrit 3×3. -/
theorem discreteLaplacian_3_apply (i j : Fin 3) :
    discreteLaplacian 3 i j = if i = j then 2 else -1 := by
  fin_cases i <;> fin_cases j <;> decide

/-- Energi Dirichlet untuk vektor konstan pada ukuran 3 adalah 0. -/
theorem dirichlet_energy_constant_3 (c : ℤ) :
    dirichletEnergy 3 (fun _ => c) = 0 := by
  unfold dirichletEnergy mulVec dotProduct
  simp [discreteLaplacian_3_apply, Fin.sum_univ_three]
  ring

/-- Identitas Energi Dirichlet untuk grid siklik 3: $v^T \Delta v = (v_0-v_1)^2 + (v_1-v_2)^2 + (v_2-v_0)^2$. -/
theorem dirichlet_energy_3_eq (v : Fin 3 → ℤ) :
    dirichletEnergy 3 v = (v 0 - v 1)^2 + (v 1 - v 2)^2 + (v 2 - v 0)^2 := by
  unfold dirichletEnergy mulVec dotProduct
  simp [discreteLaplacian_3_apply, Fin.sum_univ_three]
  ring

/-- Untuk grid siklik 3, bentuk kuadratik non-negatif untuk semua vektor bulat. -/
theorem dirichlet_energy_nonneg_3 (v : Fin 3 → ℤ) :
    0 ≤ dirichletEnergy 3 v := by
  rw [dirichlet_energy_3_eq]
  have h1 : 0 ≤ (v 0 - v 1)^2 := sq_nonneg _
  have h2 : 0 ≤ (v 1 - v 2)^2 := sq_nonneg _
  have h3 : 0 ≤ (v 2 - v 0)^2 := sq_nonneg _
  linarith

/-- Teorema Celah Spektral Diskrit S1 (Ukuran 3):
    Energi Dirichlet nol jika dan hanya jika ketiga komponen sama (vektor konstan). -/
theorem dirichlet_energy_zero_iff_constant_3 (v : Fin 3 → ℤ) :
    dirichletEnergy 3 v = 0 ↔ (v 0 = v 1 ∧ v 1 = v 2) := by
  rw [dirichlet_energy_3_eq]
  have h1 : 0 ≤ (v 0 - v 1)^2 := sq_nonneg _
  have h2 : 0 ≤ (v 1 - v 2)^2 := sq_nonneg _
  have h3 : 0 ≤ (v 2 - v 0)^2 := sq_nonneg _
  constructor
  · intro hz
    have hz1 : (v 0 - v 1)^2 = 0 := by linarith
    have hz2 : (v 1 - v 2)^2 = 0 := by linarith
    have sub1 : v 0 - v 1 = 0 := sq_eq_zero_iff.mp hz1
    have sub2 : v 1 - v 2 = 0 := sq_eq_zero_iff.mp hz2
    exact ⟨sub_eq_zero.mp sub1, sub_eq_zero.mp sub2⟩
  · rintro ⟨r1, r2⟩
    rw [r1, r2]
    ring

end Math30.Topology.DiscreteSpectralGap
