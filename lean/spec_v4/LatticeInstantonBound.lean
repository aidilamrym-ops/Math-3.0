-- LatticeInstantonBound.lean
-- Math 3.0 / Fase 53-54: Batas Instanton dan Rigiditas pada Kisi Hingga
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
--     self-dual lenyap;
--   * Fase 54: rigiditas kesamaan `Q_η(F)² = m · S(F) ↔ F = c · η`,
--     identitas defek jumlah kuadrat pasangan, dan batas stabilitas
--     kuantitatif;
--   * Fase 54: kuantisasi muatan integer, action gap `Q ≠ 0 → S ≥ 1`,
--     dan witness ketajaman gap.
--
-- Batas klaim:
--   * Ini BUKAN bukti mass gap Yang–Mills, bukan konstruksi instanton
--     kontinu, dan bukan bukti masalah Millennium.
--   * Tidak ada klaim tentang limit kontinum, moduli space, atau
--     eksistensi solusi persamaan self-dual di ruang 4-dimensi.
--   * Yang dibuktikan hanya ketaksamaan aljabar, karakterisasi
--     kesamaan, dan kuantisasi pada kisi hingga.

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

/-! ### Fase 54: Rigiditas kesamaan dan kuantisasi muatan -/

/-- Kuadrat komponen vektor tanda selalu satu. -/
lemma eta_sq (η : Config m) (hη : IsSignVector η) (i : Fin m) :
    η i ^ 2 = 1 := by
  rcases hη i with h | h <;> rw [h] <;> ring

/-- Jumlah kuadrat komponen terredupkan sama dengan aksi Euclidean. -/
lemma sum_eta_sq (η F : Config m) (hη : IsSignVector η) :
    (∑ i, (η i * F i) ^ 2) = action F := by
  unfold action
  refine Finset.sum_congr rfl ?_
  intro i _
  rw [mul_pow, eta_sq η hη i, one_mul]

/-- Identitas variansi: jumlah kuadrat selisih pasangan adalah dua kali
defek antara `m · S` dan `Q²`. -/
lemma variance_identity (x : Config m) :
    (∑ i, ∑ j, (x i - x j) ^ 2) =
      2 * ((m : ℝ) * ∑ i, (x i) ^ 2 - (∑ i, x i) ^ 2) := by
  have h : ∀ i j, (x i - x j) ^ 2 = x i ^ 2 - 2 * x i * x j + x j ^ 2 := by
    intro i j
    ring
  simp_rw [h]
  have hinner : ∀ i, (∑ j, (x i ^ 2 - 2 * x i * x j + x j ^ 2))
      = (m : ℝ) * x i ^ 2 - 2 * x i * (∑ j, x j) + (∑ j, x j ^ 2) := by
    intro i
    rw [Finset.sum_add_distrib, Finset.sum_sub_distrib]
    have h1 : (∑ _j : Fin m, x i ^ 2) = (m : ℝ) * x i ^ 2 := by
      simp [Finset.sum_const, nsmul_eq_mul]
    have h2 : (∑ j, 2 * x i * x j) = 2 * x i * (∑ j, x j) := by
      rw [← Finset.mul_sum]
    rw [h1, h2]
  simp_rw [hinner]
  rw [Finset.sum_add_distrib, Finset.sum_sub_distrib]
  have h3 : (∑ i, (m : ℝ) * x i ^ 2) = (m : ℝ) * ∑ i, x i ^ 2 := by
    rw [Finset.mul_sum]
  have h4 : (∑ i, 2 * x i * (∑ j, x j)) =
      2 * (∑ j, x j) * (∑ i, x i) := by
    calc
      (∑ i, 2 * x i * (∑ j, x j)) = (∑ i, 2 * x i) * (∑ j, x j) := by
        rw [Finset.sum_mul]
      _ = (2 * ∑ i, x i) * (∑ j, x j) := by
        rw [← Finset.mul_sum]
      _ = 2 * (∑ j, x j) * (∑ i, x i) := by
        ring
  have h5 : (∑ _i : Fin m, ∑ j : Fin m, x j ^ 2) =
      (m : ℝ) * ∑ j, x j ^ 2 := by
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  rw [h3, h4, h5]
  ring

/-- Defek `m · S - Q²` sama dengan setengah jumlah kuadrat selisih
komponen terredupkan. -/
theorem instanton_bound_defect (η F : Config m) (hη : IsSignVector η) :
    (m : ℝ) * action F - (charge η F) ^ 2 =
      (1 / 2) * ∑ i, ∑ j, (η i * F i - η j * F j) ^ 2 := by
  have h := variance_identity (fun i => η i * F i)
  have hsq : (∑ i, (η i * F i) ^ 2) = action F := sum_eta_sq η F hη
  have hsum : (∑ i, η i * F i) = charge η F := rfl
  rw [hsq, hsum] at h
  linarith

/-- Batas titik demi titik: setiap selisih komponen terredupkan
dikontrol oleh defek total. -/
lemma instanton_bound_pointwise_defect (η F : Config m) (hη : IsSignVector η)
    (i j : Fin m) :
    (η i * F i - η j * F j) ^ 2 ≤
      2 * ((m : ℝ) * action F - (charge η F) ^ 2) := by
  let x : Config m := fun i => η i * F i
  have hdefect := instanton_bound_defect η F hη
  have hdouble : (∑ k, ∑ l, (x k - x l) ^ 2) =
      2 * ((m : ℝ) * action F - (charge η F) ^ 2) := by
    linarith
  have hinner_nonneg : ∀ k : Fin m, 0 ≤ (x i - x k) ^ 2 := fun k => sq_nonneg _
  have hinner_le : (x i - x j) ^ 2 ≤ ∑ k, (x i - x k) ^ 2 :=
    Finset.single_le_sum (f := fun k => (x i - x k) ^ 2)
      (fun k _ => hinner_nonneg k) (mem_univ j)
  have houter_nonneg : ∀ k : Fin m, 0 ≤ ∑ l, (x k - x l) ^ 2 :=
    fun k => Finset.sum_nonneg (fun l _ => sq_nonneg _)
  have houter_le : (∑ k, (x i - x k) ^ 2) ≤ ∑ k, ∑ l, (x k - x l) ^ 2 :=
    Finset.single_le_sum (f := fun k => ∑ l, (x k - x l) ^ 2)
      (fun k _ => houter_nonneg k) (mem_univ i)
  calc
    (η i * F i - η j * F j) ^ 2 = (x i - x j) ^ 2 := rfl
    _ ≤ ∑ k, (x i - x k) ^ 2 := hinner_le
    _ ≤ ∑ k, ∑ l, (x k - x l) ^ 2 := houter_le
    _ = 2 * ((m : ℝ) * action F - (charge η F) ^ 2) := hdouble

/-- Versi kuantitatif: jika defek aksi–muatan paling besar `ε`, maka
setiap selisih komponen terredupkan paling besar `2ε`. -/
theorem instanton_bound_stable (η F : Config m) (hη : IsSignVector η) {ε : ℝ}
    (h : (m : ℝ) * action F - (charge η F) ^ 2 ≤ ε) (i j : Fin m) :
    (η i * F i - η j * F j) ^ 2 ≤ 2 * ε := by
  have h2 := instanton_bound_pointwise_defect η F hη i j
  linarith

/-- **Rigiditas kesamaan.** Untuk `m > 0`, batas instanton jenuh tepat
ketika `F` proporsional terhadap vektor tanda `η`. -/
theorem instanton_bound_eq_iff (η F : Config m) (hη : IsSignVector η) (hm : 0 < m) :
    (charge η F) ^ 2 = (m : ℝ) * action F ↔
      ∃ c : ℝ, F = fun i => c * η i := by
  constructor
  · intro heq
    let x : Config m := fun i => η i * F i
    have hxsum : (∑ i, x i) = charge η F := rfl
    have hxsq : (∑ i, x i ^ 2) = action F := sum_eta_sq η F hη
    have hdouble_zero : (∑ i, ∑ j, (x i - x j) ^ 2) = 0 := by
      have h := variance_identity x
      rw [hxsum, hxsq] at h
      rw [heq] at h
      linarith
    have hconst : ∀ i j, x i = x j := by
      intro i j
      have hinner_nonneg : ∀ k : Fin m, 0 ≤ (x i - x k) ^ 2 := fun k => sq_nonneg _
      have hinner_le : (x i - x j) ^ 2 ≤ ∑ k, (x i - x k) ^ 2 :=
        Finset.single_le_sum (f := fun k => (x i - x k) ^ 2)
          (fun k _ => hinner_nonneg k) (mem_univ j)
      have houter_nonneg : ∀ k : Fin m, 0 ≤ ∑ l, (x k - x l) ^ 2 :=
        fun k => Finset.sum_nonneg (fun l _ => sq_nonneg _)
      have houter_le : (∑ k, (x i - x k) ^ 2) ≤ ∑ k, ∑ l, (x k - x l) ^ 2 :=
        Finset.single_le_sum (f := fun k => ∑ l, (x k - x l) ^ 2)
          (fun k _ => houter_nonneg k) (mem_univ i)
      have hterm_zero : (x i - x j) ^ 2 = 0 := by
        have hle : (x i - x j) ^ 2 ≤ 0 := by
          calc
            (x i - x j) ^ 2 ≤ ∑ k, (x i - x k) ^ 2 := hinner_le
            _ ≤ ∑ k, ∑ l, (x k - x l) ^ 2 := houter_le
            _ = 0 := hdouble_zero
        exact le_antisymm hle (sq_nonneg _)
      have hsub : x i - x j = 0 := sq_eq_zero_iff.mp hterm_zero
      linarith
    refine ⟨x ⟨0, hm⟩, ?_⟩
    funext i
    have hxi : x i = x ⟨0, hm⟩ := hconst i ⟨0, hm⟩
    have hxidef : η i * F i = x ⟨0, hm⟩ := hxi
    have hsq : η i ^ 2 = 1 := eta_sq η hη i
    calc
      F i = 1 * F i := by ring
      _ = (η i ^ 2) * F i := by rw [hsq]
      _ = η i * (η i * F i) := by ring
      _ = η i * x ⟨0, hm⟩ := by rw [hxidef]
      _ = x ⟨0, hm⟩ * η i := by ring
  · rintro ⟨c, rfl⟩
    exact instanton_bound_saturated η hη c

/-! ### Kuantisasi muatan integer -/

/-- Konfigurasi medan integer pada kisi hingga. -/
abbrev ConfigZ (m : ℕ) := Fin m → ℤ

/-- Vektor tanda integer dengan komponen `±1`. -/
def IsSignVectorZ (η : ConfigZ m) : Prop :=
  ∀ i, η i = 1 ∨ η i = -1

/-- Aksi Euclidean integer `S(F) = ∑ F_i²`. -/
def actionZ (F : ConfigZ m) : ℤ :=
  ∑ i, (F i) ^ 2

/-- Muatan topologi integer `Q_η(F) = ∑ η_i F_i`. -/
def chargeZ (η F : ConfigZ m) : ℤ :=
  ∑ i, η i * F i

lemma etaZ_sq (η : ConfigZ m) (hη : IsSignVectorZ η) (i : Fin m) :
    η i ^ 2 = 1 := by
  rcases hη i with h | h <;> rw [h] <;> ring

lemma sum_etaZ_sq (η F : ConfigZ m) (hη : IsSignVectorZ η) :
    (∑ i, (η i * F i) ^ 2) = actionZ F := by
  unfold actionZ
  refine Finset.sum_congr rfl ?_
  intro i _
  rw [mul_pow, etaZ_sq η hη i, one_mul]

/-- Batas instanton integer: `Q_η(F)² ≤ m · S(F)` atas `ℤ`. -/
theorem chargeZ_sq_le (η F : ConfigZ m) (hη : IsSignVectorZ η) :
    (chargeZ η F) ^ 2 ≤ (m : ℤ) * actionZ F := by
  have h := sq_sum_le_card_mul_sum_sq (s := (univ : Finset (Fin m)))
    (f := fun i => η i * F i)
  have hsq : (∑ i, (η i * F i) ^ 2) = actionZ F := sum_etaZ_sq η F hη
  calc
    (chargeZ η F) ^ 2 = (∑ i, η i * F i) ^ 2 := rfl
    _ ≤ (Fintype.card (Fin m) : ℤ) * ∑ i, (η i * F i) ^ 2 := by
      simpa using h
    _ = (m : ℤ) * actionZ F := by
      rw [hsq, Fintype.card_fin]

lemma actionZ_nonneg (F : ConfigZ m) : 0 ≤ actionZ F := by
  unfold actionZ
  exact Finset.sum_nonneg (fun i _ => sq_nonneg (F i))

lemma actionZ_eq_zero_iff (F : ConfigZ m) : actionZ F = 0 ↔ F = 0 := by
  constructor
  · intro h
    funext i
    have hterm := (Finset.sum_eq_zero_iff_of_nonneg (s := (univ : Finset (Fin m)))
      (f := fun j => (F j) ^ 2) (fun j _ => sq_nonneg (F j))).mp
      (by simpa [actionZ] using h) i (mem_univ i)
    exact sq_eq_zero_iff.mp hterm
  · intro h
    simp [actionZ, h]

/-- Muatan integer tak nol memaksa aksi positif. -/
theorem chargeZ_ne_zero_actionZ_pos (η F : ConfigZ m) (hη : IsSignVectorZ η)
    (hQ : chargeZ η F ≠ 0) : 0 < actionZ F := by
  have hnonneg : 0 ≤ actionZ F := actionZ_nonneg F
  rcases lt_or_eq_of_le hnonneg with hpos | hzero
  · exact hpos
  · have hle : (chargeZ η F) ^ 2 ≤ 0 := by
      have h := chargeZ_sq_le η F hη
      rw [← hzero, mul_zero] at h
      exact h
    have hsq_nonneg : 0 ≤ (chargeZ η F) ^ 2 := sq_nonneg _
    have hq : chargeZ η F = 0 := by nlinarith
    exact absurd hq hQ

/-- **Action gap diskret.** Muatan integer tak nol memerlukan aksi
paling sedikit satu. -/
theorem chargeZ_ne_zero_actionZ_ge_one (η F : ConfigZ m) (hη : IsSignVectorZ η)
    (hQ : chargeZ η F ≠ 0) : 1 ≤ actionZ F := by
  have hpos := chargeZ_ne_zero_actionZ_pos η F hη hQ
  omega

/-- Ketajaman action gap: ada konfigurasi muatan tak nol dengan aksi `1`. -/
theorem action_gap_sharp (m : ℕ) (hm : 0 < m) :
    ∃ (η F : ConfigZ m), IsSignVectorZ η ∧ chargeZ η F ≠ 0 ∧ actionZ F = 1 := by
  let i0 : Fin m := ⟨0, hm⟩
  let η : ConfigZ m := fun _ => 1
  let F : ConfigZ m := fun i => if i = i0 then 1 else 0
  have hη : IsSignVectorZ η := fun _ => Or.inl rfl
  have hcharge : chargeZ η F = 1 := by
    unfold chargeZ
    simp [η, F]
  have haction : actionZ F = 1 := by
    unfold actionZ
    simp [F]
  refine ⟨η, F, hη, ?_, haction⟩
  rw [hcharge]
  norm_num

end Math30.Gauge.LatticeInstanton
