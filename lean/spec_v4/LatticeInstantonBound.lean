-- LatticeInstantonBound.lean
-- Math 3.0 / Fase 53: Batas Instanton pada Kisi Hingga
--
-- Cakupan:
--   * konfigurasi medan pada kisi hingga `Fin m → ℝ`;
--   * aksi Euclidean diskret `S(F) = ∑ F_i²` dan muatan topologi
--     terredupkan `Q_η(F) = ∑ η_i F_i` terhadap vektor tanda `η`;
--   * batas Cauchy–Schwarz `Q_η(F)² ≤ m · S(F)`, saturasi oleh
--     konfigurasi self-dual `F = c · η`, dan witness ketajaman;
--   * dekomposisi self-dual / anti-self-dual dengan batas BPS `|Q| ≤ S`;
--   * karakterisasi kesamaan: `Q = S` tepat ketika komponen
--     anti-self-dual lenyap, dan `Q = -S` tepat ketika komponen
--     self-dual lenyap.
--
-- Batas klaim:
--   * Ini BUKAN bukti mass gap Yang–Mills, bukan konstruksi instanton
--     kontinu, dan bukan bukti masalah Millennium.
--   * Tidak ada klaim tentang limit kontinum, moduli space, atau
--     eksistensi solusi persamaan self-dual di ruang 4-dimensi.
--   * Yang dibuktikan hanya ketaksamaan aljabar dan karakterisasi
--     kesamaan pada kisi hingga.

import Mathlib.Algebra.Order.Chebyshev
import Mathlib.Tactic

open Finset
open scoped BigOperators

namespace Math30.Gauge.LatticeInstanton

variable {m : ℕ}

/-- Konfigurasi medan pada kisi hingga dengan `m` tapak. -/
abbrev Config (m : ℕ) := Fin m → ℝ

/-- Vektor tanda: polarisasi topologi dengan komponen `±1`. -/
def IsSignVector (η : Config m) : Prop :=
  ∀ i, η i = 1 ∨ η i = -1

/-- Aksi Euclidean diskret `S(F) = ∑ F_i²`. -/
def action (F : Config m) : ℝ :=
  ∑ i, (F i) ^ 2

/-- Muatan topologi terhadap polarisasi `η`: `Q_η(F) = ∑ η_i F_i`. -/
def charge (η F : Config m) : ℝ :=
  ∑ i, η i * F i

/-- Batas instanton kisi hingga: `Q_η(F)² ≤ m · S(F)`.

Ini adalah ketaksamaan Cauchy–Schwarz pada `m` tapak: muatan topologi
terredupkan tidak dapat melebihi akar dari `m` kali aksi. -/
theorem instanton_bound (η F : Config m) (hη : IsSignVector η) :
    (charge η F) ^ 2 ≤ (m : ℝ) * action F := by
  have h := sq_sum_le_card_mul_sum_sq (s := (univ : Finset (Fin m)))
    (f := fun i => η i * F i)
  have hsq : (∑ i, (η i * F i) ^ 2) = action F := by
    unfold action
    refine Finset.sum_congr rfl ?_
    intro i _
    rcases hη i with h | h <;> rw [h] <;> ring
  calc
    (charge η F) ^ 2 = (∑ i, η i * F i) ^ 2 := rfl
    _ ≤ (Fintype.card (Fin m) : ℝ) * ∑ i, (η i * F i) ^ 2 := by
      simpa using h
    _ = (m : ℝ) * action F := by
      rw [hsq, Fintype.card_fin]

/-- Konfigurasi self-dual `F = c · η` menjenuhkan batas instanton. -/
theorem instanton_bound_saturated (η : Config m) (hη : IsSignVector η) (c : ℝ) :
    (charge η (fun i => c * η i)) ^ 2 =
      (m : ℝ) * action (fun i => c * η i) := by
  have hcharge : charge η (fun i => c * η i) = (m : ℝ) * c := by
    unfold charge
    calc
      (∑ i, η i * (c * η i)) = ∑ _i : Fin m, c := by
        refine Finset.sum_congr rfl ?_
        intro i _
        rcases hη i with h | h <;> rw [h] <;> ring
      _ = (m : ℝ) * c := by simp [mul_comm]
  have haction : action (fun i => c * η i) = (m : ℝ) * c ^ 2 := by
    unfold action
    calc
      (∑ i, (c * η i) ^ 2) = ∑ _i : Fin m, c ^ 2 := by
        refine Finset.sum_congr rfl ?_
        intro i _
        rcases hη i with h | h <;> rw [h] <;> ring
      _ = (m : ℝ) * c ^ 2 := by simp
  rw [hcharge, haction]
  ring

/-- Sharpness: untuk `m > 0` ada konfigurasi tak nol yang menjenuhkan batas. -/
theorem instanton_bound_sharp (m : ℕ) (hm : 0 < m) :
    ∃ (η F : Config m), IsSignVector η ∧ F ≠ 0 ∧
      (charge η F) ^ 2 = (m : ℝ) * action F ∧ 0 < action F := by
  let η : Config m := fun _ => 1
  let F : Config m := fun _ => 1
  have hη : IsSignVector η := fun _ => Or.inl rfl
  have hF : F ≠ 0 := by
    intro h
    have h0 := congrFun h ⟨0, hm⟩
    norm_num [F] at h0
  have haction : action F = (m : ℝ) := by
    unfold action F
    simp
  have hcharge : charge η F = (m : ℝ) := by
    unfold charge η F
    simp
  refine ⟨η, F, hη, hF, ?_, ?_⟩
  · rw [hcharge, haction]
    ring
  · rw [haction]
    exact_mod_cast hm

/-- Witness tanda: pada kisi dua tapak, konfigurasi `F = (1, -1)` dengan
polarisasi `η = (1, -1)` menjenuhkan batas dan memuat komponen negatif. -/
theorem instanton_bound_sharp_signed :
    ∃ (η F : Config 2), IsSignVector η ∧ F ≠ 0 ∧
      (charge η F) ^ 2 = (2 : ℝ) * action F ∧ F 0 = 1 ∧ F 1 = -1 := by
  let η : Config 2 := fun i => if i = 0 then 1 else -1
  let F : Config 2 := fun i => if i = 0 then 1 else -1
  have hη : IsSignVector η := by
    intro i
    fin_cases i <;> simp [η]
  have hF0 : F 0 = 1 := by simp [F]
  have hF1 : F 1 = -1 := by simp [F]
  have hF : F ≠ 0 := by
    intro h
    have h0 := congrFun h 0
    rw [hF0] at h0
    norm_num at h0
  have hcharge : charge η F = 2 := by
    unfold charge
    rw [Fin.sum_univ_two]
    simp [η, F]
    norm_num
  have haction : action F = 2 := by
    unfold action
    rw [Fin.sum_univ_two]
    simp [F]
    norm_num
  refine ⟨η, F, hη, hF, ?_, hF0, hF1⟩
  rw [hcharge, haction]
  norm_num

/-! ### Dekomposisi self-dual / anti-self-dual -/

/-- Aksi Euclidean dari pasangan komponen self-dual `a` dan anti-self-dual `b`. -/
def bpsAction (a b : Config m) : ℝ :=
  ∑ i, (a i ^ 2 + b i ^ 2)

/-- Muatan topologi dari dekomposisi: selisih kerapatan self-dual dan anti-self-dual. -/
def bpsCharge (a b : Config m) : ℝ :=
  ∑ i, (a i ^ 2 - b i ^ 2)

/-- Batas BPS kisi hingga: `|Q| ≤ S`. -/
theorem bps_bound (a b : Config m) : |bpsCharge a b| ≤ bpsAction a b := by
  have h1 : bpsCharge a b ≤ bpsAction a b := by
    unfold bpsCharge bpsAction
    refine Finset.sum_le_sum ?_
    intro i _
    nlinarith [sq_nonneg (b i)]
  have h2 : -bpsAction a b ≤ bpsCharge a b := by
    unfold bpsCharge bpsAction
    rw [← Finset.sum_neg_distrib]
    refine Finset.sum_le_sum ?_
    intro i _
    nlinarith [sq_nonneg (a i)]
  rw [abs_le]
  exact ⟨h2, h1⟩

/-- Komponen murni self-dual menjenuhkan batas BPS. -/
theorem bps_self_dual_saturates (a : Config m) :
    bpsCharge a 0 = bpsAction a 0 := by
  unfold bpsCharge bpsAction
  simp

/-- Komponen murni anti-self-dual menjenuhkan batas BPS dengan tanda negatif. -/
theorem bps_anti_self_dual_saturates (b : Config m) :
    bpsCharge 0 b = -bpsAction 0 b := by
  unfold bpsCharge bpsAction
  simp

/-- Kesamaan `Q = S` memaksa komponen anti-self-dual lenyap. -/
theorem bps_equality_forces_anti_self_dual_zero (a b : Config m)
    (h : bpsCharge a b = bpsAction a b) : b = 0 := by
  have hzero : (∑ i, (b i) ^ 2) = 0 := by
    have h2 : bpsAction a b - bpsCharge a b = 0 := by linarith
    have hsum : bpsAction a b - bpsCharge a b = ∑ i, 2 * b i ^ 2 := by
      unfold bpsAction bpsCharge
      rw [← Finset.sum_sub_distrib]
      refine Finset.sum_congr rfl ?_
      intro i _
      ring
    have h2' : (∑ i, 2 * b i ^ 2) = 0 := by linarith
    rw [← Finset.mul_sum] at h2'
    nlinarith
  funext i
  have hb := (Finset.sum_eq_zero_iff_of_nonneg (s := (univ : Finset (Fin m)))
    (f := fun j => (b j) ^ 2) (fun j _ => sq_nonneg (b j))).mp (by simpa using hzero)
    i (mem_univ i)
  exact sq_eq_zero_iff.mp hb

/-- Kesamaan `Q = -S` memaksa komponen self-dual lenyap. -/
theorem bps_equality_forces_self_dual_zero (a b : Config m)
    (h : bpsCharge a b = -bpsAction a b) : a = 0 := by
  have hzero : (∑ i, (a i) ^ 2) = 0 := by
    have h2 : bpsAction a b + bpsCharge a b = 0 := by linarith
    have hsum : bpsAction a b + bpsCharge a b = ∑ i, 2 * a i ^ 2 := by
      unfold bpsAction bpsCharge
      rw [← Finset.sum_add_distrib]
      refine Finset.sum_congr rfl ?_
      intro i _
      ring
    have h2' : (∑ i, 2 * a i ^ 2) = 0 := by linarith
    rw [← Finset.mul_sum] at h2'
    nlinarith
  funext i
  have ha := (Finset.sum_eq_zero_iff_of_nonneg (s := (univ : Finset (Fin m)))
    (f := fun j => (a j) ^ 2) (fun j _ => sq_nonneg (a j))).mp (by simpa using hzero)
    i (mem_univ i)
  exact sq_eq_zero_iff.mp ha

/-- Karakterisasi kesamaan: `Q = S` tepat ketika komponen anti-self-dual lenyap. -/
theorem bps_equality_iff_anti_self_dual_zero (a b : Config m) :
    bpsCharge a b = bpsAction a b ↔ b = 0 := by
  constructor
  · exact bps_equality_forces_anti_self_dual_zero a b
  · intro h
    rw [h]
    exact bps_self_dual_saturates a

/-- Karakterisasi kesamaan: `Q = -S` tepat ketika komponen self-dual lenyap. -/
theorem bps_equality_iff_self_dual_zero (a b : Config m) :
    bpsCharge a b = -bpsAction a b ↔ a = 0 := by
  constructor
  · exact bps_equality_forces_self_dual_zero a b
  · intro h
    rw [h]
    exact bps_anti_self_dual_saturates b

/-- Sharpness batas BPS: ada konfigurasi tak nol dengan `|Q| = S`. -/
theorem bps_bound_sharp (m : ℕ) (hm : 0 < m) :
    ∃ (a b : Config m), (a ≠ 0 ∨ b ≠ 0) ∧
      |bpsCharge a b| = bpsAction a b := by
  let a : Config m := fun _ => 1
  have ha : a ≠ 0 := by
    intro h
    have h0 := congrFun h ⟨0, hm⟩
    norm_num [a] at h0
  refine ⟨a, 0, Or.inl ha, ?_⟩
  rw [bps_self_dual_saturates]
  exact abs_of_nonneg (by unfold bpsAction; positivity)

end Math30.Gauge.LatticeInstanton
