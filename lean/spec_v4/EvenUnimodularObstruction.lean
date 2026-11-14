-- EvenUnimodularObstruction.lean
-- Math 3.0 / Fase 52: Bayangan Aljabar Teorema Donaldson
--
-- Cakupan:
--   * bentuk kuadratik genap dan unimodular pada kisi hingga ℤ^n;
--   * bukti bahwa bentuk genap unimodular tidak dapat didiagonalisasi
--     oleh kongruensi unimodular atas ℤ untuk rank positif;
--   * witness H = [[0,1],[1,0]], intersection form dari S² × S².
--
-- Batas klaim:
--   * Ini BUKAN teorema Donaldson dan BUKAN bukti SPC4.
--   * Tidak ada klaim tentang manifold halus 4-dimensi, ruang moduli
--     instanton, atau struktur eksotis R⁴.
--   * Yang dibuktikan hanya obstruksi paritas aljabar murni.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.Ring.Parity
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

open Finset
open scoped BigOperators Matrix

namespace Math30.Topology.EvenUnimodular

variable {n : ℕ}

/-- Bentuk kuadratik yang diasosiasikan dengan matriks simetris `G`. -/
def qform (G : Matrix (Fin n) (Fin n) ℤ) (x : Fin n → ℤ) : ℤ :=
  x ⬝ᵥ (G *ᵥ x)

/-- `G` disebut bentuk genap bila semua nilai kuadratiknya bilangan genap. -/
def EvenForm (G : Matrix (Fin n) (Fin n) ℤ) : Prop :=
  ∀ x : Fin n → ℤ, Even (qform G x)

/-- Matriks diagonal: semua entri di luar diagonal utama nol. -/
def IsDiagonal (D : Matrix (Fin n) (Fin n) ℤ) : Prop :=
  ∀ i j, i ≠ j → D i j = 0

/-- Matriks unimodular atas `ℤ`: determinannya `1` atau `-1`. -/
def IsUnimodular (P : Matrix (Fin n) (Fin n) ℤ) : Prop :=
  P.det = 1 ∨ P.det = -1

/-- Bentuk kuadratik invariant di bawah kongruensi `G ↦ Pᵀ G P`. -/
theorem qform_congruent (G P : Matrix (Fin n) (Fin n) ℤ) (x : Fin n → ℤ) :
    qform (Pᵀ * G * P) x = qform G (P *ᵥ x) := by
  unfold qform
  rw [← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec,
    Matrix.dotProduct_transpose_mulVec, dotProduct_comm]

/-- Sifat genap diwariskan oleh kongruensi. -/
theorem EvenForm.congr {G : Matrix (Fin n) (Fin n) ℤ}
    (hG : EvenForm G) (P : Matrix (Fin n) (Fin n) ℤ) :
    EvenForm (Pᵀ * G * P) := by
  intro x
  rw [qform_congruent]
  exact hG (P *ᵥ x)

/-- Entri diagonal dari bentuk genap adalah genap. -/
theorem even_diagonal_of_evenForm {D : Matrix (Fin n) (Fin n) ℤ}
    (hD : EvenForm D) (i : Fin n) :
    Even (D i i) := by
  have h := hD (Pi.single i 1)
  simp only [qform, Matrix.dotProduct_mulVec, Matrix.single_one_vecMul] at h
  simpa using h

/-- Jika `D` diagonal dan setiap entri diagonalnya genap, maka `2^n` membagi `det D`. -/
theorem two_pow_dvd_det_of_diagonal_even {D : Matrix (Fin n) (Fin n) ℤ}
    (hdiag : IsDiagonal D)
    (heven : ∀ i, Even (D i i)) :
    (2 : ℤ) ^ n ∣ D.det := by
  have hD : D = Matrix.diagonal (fun i => D i i) := by
    ext i j
    by_cases h : i = j
    · subst h
      rw [Matrix.diagonal_apply_eq]
    · rw [Matrix.diagonal_apply_ne _ h, hdiag i j h]
  rw [hD, Matrix.det_diagonal]
  have heven' : ∀ i, ∃ k : ℤ, D i i = 2 * k := by
    intro i
    rcases heven i with ⟨k, hk⟩
    exact ⟨k, by rw [hk]; ring⟩
  choose k hk using heven'
  have hprod : (∏ i, D i i) = (2 : ℤ) ^ n * ∏ i, k i := by
    calc
      (∏ i, D i i) = ∏ i, (2 * k i) := Finset.prod_congr rfl (fun i _ => hk i)
      _ = (∏ i, (2 : ℤ)) * ∏ i, k i := Finset.prod_mul_distrib
      _ = (2 : ℤ) ^ n * ∏ i, k i := by simp
  rw [hprod]
  exact ⟨_, rfl⟩

/-- `2^n` tidak membagi `1` untuk `n > 0`. -/
theorem not_two_pow_dvd_one {n : ℕ} (hn : 0 < n) : ¬ (2 : ℤ) ^ n ∣ 1 := by
  intro h
  have hle : (2 : ℤ) ^ n ≤ 1 := Int.le_of_dvd (by norm_num) h
  have hge : (2 : ℤ) ^ 1 ≤ (2 : ℤ) ^ n :=
    pow_le_pow_right₀ (by norm_num : (1 : ℤ) ≤ 2) (by omega : 1 ≤ n)
  norm_num at hge
  linarith

/-- `2^n` tidak membagi `-1` untuk `n > 0`. -/
theorem not_two_pow_dvd_neg_one {n : ℕ} (hn : 0 < n) : ¬ (2 : ℤ) ^ n ∣ -1 := by
  intro h
  exact not_two_pow_dvd_one hn (dvd_neg.mp h)

/-- Tidak ada bentuk genap unimodular diagonal pada rank positif. -/
theorem even_unimodular_diagonal_absurd {D : Matrix (Fin n) (Fin n) ℤ}
    (hdiag : IsDiagonal D)
    (heven : EvenForm D)
    (hdet : IsUnimodular D)
    (hn : 0 < n) : False := by
  have hdiag_even : ∀ i, Even (D i i) :=
    fun i => even_diagonal_of_evenForm heven i
  have hdiv : (2 : ℤ) ^ n ∣ D.det :=
    two_pow_dvd_det_of_diagonal_even hdiag hdiag_even
  rcases hdet with h | h
  · rw [h] at hdiv
    exact not_two_pow_dvd_one hn hdiv
  · rw [h] at hdiv
    exact not_two_pow_dvd_neg_one hn hdiv

/-- Determinan tidak berubah di bawah kongruensi oleh matriks unimodular. -/
theorem det_congruent {G D P : Matrix (Fin n) (Fin n) ℤ}
    (hD : D = Pᵀ * G * P) (hP : IsUnimodular P) :
    D.det = G.det := by
  subst hD
  rw [Matrix.det_mul, Matrix.det_mul, Matrix.det_transpose]
  rcases hP with h | h <;> rw [h] <;> ring

/-- Teorema inti: bentuk genap unimodular tidak dapat didiagonalisasi atas `ℤ`. -/
theorem even_unimodular_not_diagonalizable
    {G D P : Matrix (Fin n) (Fin n) ℤ}
    (hG_even : EvenForm G)
    (hG_det : IsUnimodular G)
    (hD_diag : IsDiagonal D)
    (hD : D = Pᵀ * G * P)
    (hP : IsUnimodular P)
    (hn : 0 < n) : False := by
  have hD_even : EvenForm D := by
    rw [hD]
    exact hG_even.congr P
  have hD_det : IsUnimodular D := by
    have h := det_congruent hD hP
    change D.det = 1 ∨ D.det = -1
    rw [h]
    exact hG_det
  exact even_unimodular_diagonal_absurd hD_diag hD_even hD_det hn

/-- Bentuk hiperbolik `H = [[0,1],[1,0]]`, intersection form dari `S² × S²`. -/
def hyperbolic : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 1, 0]

/-- Bentuk hiperbolik adalah bentuk genap. -/
theorem hyperbolic_even : EvenForm hyperbolic := by
  intro x
  simp [qform, hyperbolic, Matrix.vecHead, Matrix.vecTail]
  exact ⟨x 0 * x 1, by ring⟩

/-- Determinan bentuk hiperbolik adalah `-1`, jadi ia unimodular. -/
theorem hyperbolic_det : hyperbolic.det = -1 := by
  simp [hyperbolic, Matrix.det_fin_two_of]

/-- `H` genap dan unimodular, tetapi tidak dapat didiagonalisasi atas `ℤ`. -/
theorem hyperbolic_not_diagonalizable :
    ¬ ∃ (D P : Matrix (Fin 2) (Fin 2) ℤ),
        IsDiagonal D ∧
        D = Pᵀ * hyperbolic * P ∧
        IsUnimodular P := by
  rintro ⟨D, P, hdiag, hD, hP⟩
  exact even_unimodular_not_diagonalizable hyperbolic_even (Or.inr hyperbolic_det)
    hdiag hD hP (by norm_num)

end Math30.Topology.EvenUnimodular
