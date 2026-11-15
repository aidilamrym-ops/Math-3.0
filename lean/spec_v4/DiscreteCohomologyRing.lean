-- DiscreteCohomologyRing.lean
-- Math 3.0 / Fase 63: Cup Product Diskrit & Gelanggang Kohomologi H⁰
--
-- Cakupan:
--   * 0-cochain dan 1-cochain pada kompleks interval 3-vertex;
--   * koboundary diskrit d⁰;
--   * cup product (0×0, 1×0, 0×1) dengan konvensi simpul pertama;
--   * aturan Leibniz d⁰(f ∪ g) = (d⁰f) ∪ g + f ∪ (d⁰g);
--   * kosisel (cocycle) iff konstan  ⟹  H⁰ ≅ ℤ;
--   * produk kosisel tetap kosisel  ⟹  struktur gelanggang H⁰.
--
-- Batas klaim:
--   * Ini BUKAN kohomologi kontinu atau teori berkas/simplicial umum.
--   * Tidak ada klaim tentang H^k untuk k > 0, produk cup berderajat,
--     atau invarian topologi.
--   * Yang dibuktikan hanya aljabar hingga pada interval 3-vertex.

import Mathlib.Tactic

namespace Math30.Topology.DiscreteCohomologyRing

/-- 0-cochain pada kompleks interval 3-vertex: fungsi vertex → ℤ. -/
abbrev Cochain0 := Fin 3 → ℤ

/-- 1-cochain pada 2 edge interval: fungsi edge → ℤ. -/
abbrev Cochain1 := Fin 2 → ℤ

/-- Koboundary diskrit d⁰: f ↦ (f(1)-f(0), f(2)-f(1)). -/
def d0 (f : Cochain0) (i : Fin 2) : ℤ :=
  match i.val with
  | 0 => f 1 - f 0
  | _ => f 2 - f 1

/-- 0-cochain f adalah kosisel bila d⁰ f = 0. -/
def IsCocycle (f : Cochain0) : Prop := d0 f = 0

/-- Cup product 0×0: perkalian titikwise. -/
def cup0 (f g : Cochain0) : Cochain0 := fun v => f v * g v

/-- Cup product 1×0 dengan konvensi simpul pertama:
    (a ∪ g)(e) = a(e) · g(e.2). -/
def cup10 (a : Cochain1) (g : Cochain0) (i : Fin 2) : ℤ :=
  match i.val with
  | 0 => a 0 * g 1
  | _ => a 1 * g 2

/-- Cup product 0×1 dengan konvensi simpul pertama:
    (f ∪ b)(e) = f(e.1) · b(e). -/
def cup01 (f : Cochain0) (b : Cochain1) (i : Fin 2) : ℤ :=
  match i.val with
  | 0 => f 0 * b 0
  | _ => f 1 * b 1

/-- Aturan Leibniz diskrit untuk pasangan fungsional 0-cochain. -/
theorem leibniz (f g : Cochain0) :
    d0 (cup0 f g) = cup10 (d0 f) g + cup01 f (d0 g) := by
  funext i
  fin_cases i <;> simp [d0, cup0, cup10, cup01] <;> ring

/-- Kosisel pada interval: d⁰ f = 0 iff f konstan pada ketiga simpul. -/
theorem cocycle_iff_const (f : Cochain0) :
    IsCocycle f ↔ f 0 = f 1 ∧ f 1 = f 2 := by
  constructor
  · intro h
    have h0 := congrFun h ⟨0, by decide⟩
    have h1 := congrFun h ⟨1, by decide⟩
    simp [d0] at h0 h1
    constructor <;> omega
  · rintro ⟨h01, h12⟩
    funext i
    fin_cases i <;> simp [d0] <;> omega

/-- Kosisel ditentukan sepenuhnya oleh nilainya di simpul 0. -/
theorem cocycle_determined_by_zero {f : Cochain0} (hf : IsCocycle f) :
    f = fun _ => f 0 := by
  rw [cocycle_iff_const] at hf
  funext v
  fin_cases v <;> simp [hf.1, hf.2]

/-- Karakterisasi H⁰: kernel d⁰ = kosisel konstan (dimensi 1 atas ℤ). -/
theorem cocycle_iff_exists_const (f : Cochain0) :
    IsCocycle f ↔ ∃ c : ℤ, f = fun _ => c := by
  constructor
  · intro hf
    exact ⟨f 0, cocycle_determined_by_zero hf⟩
  · rintro ⟨c, rfl⟩
    rw [cocycle_iff_const]
    exact ⟨rfl, rfl⟩

/-- Produk cup dua kosisel tetap kosisel (tertutup). -/
theorem cocycle_cup {f g : Cochain0} (hf : IsCocycle f) (hg : IsCocycle g) :
    IsCocycle (cup0 f g) := by
  rw [cocycle_iff_const] at *
  obtain ⟨hf0, hf1⟩ := hf
  obtain ⟨hg0, hg1⟩ := hg
  constructor <;> simp [cup0, hf0, hf1, hg0, hg1]

/-- Unit gelanggang: fungsi konstan 1 adalah kosisel. -/
theorem cocycle_one : IsCocycle (fun _ => (1 : ℤ)) := by
  rw [cocycle_iff_const]
  exact ⟨rfl, rfl⟩

/-- Cup product komutatif. -/
theorem cup0_comm (f g : Cochain0) : cup0 f g = cup0 g f := by
  funext v
  simp [cup0, mul_comm]

/-- Cup product asosiatif. -/
theorem cup0_assoc (f g h : Cochain0) :
    cup0 (cup0 f g) h = cup0 f (cup0 g h) := by
  funext v
  simp [cup0, mul_assoc]

/-- Graded sign trivial pada H⁰: cup unit kiri. -/
theorem cup0_one_left (f : Cochain0) : cup0 (fun _ => (1 : ℤ)) f = f := by
  funext v
  simp [cup0]

end Math30.Topology.DiscreteCohomologyRing
