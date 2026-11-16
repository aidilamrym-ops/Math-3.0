-- DiscretePoincareDuality.lean
-- Math 3.0 / Fase 64: Dualitas Poincaré Diskrit (n = 1)
--
-- Cakupan:
--   * kompleks rantai siklus tertutup C3: simpul {0,1,2}, sisi (0,1),(1,2),(2,0);
--   * operator batas ∂₁ : C₁ → C₀ dan koboundary d⁰ : C₀ → C₁;
--   * siklus H₁ = ker ∂₁ ≅ ℤ (dibangkitkan oleh siklus fundamental);
--   * coker ∂₁ ≅ ℤ (lokalisasi H₀);
--   * pasangan evaluasi ⟨f, a⟩ = Σ f_i a_i  :  coker ∂₁ × ker ∂₁ → ℤ;
--   * pasangan turun ke hasil bagi (well-defined) dan non-degenerate (perfect);
--   * akibat: β₀ = β₁ = 1 (dualitas Betti untuk n = 1).
--
-- Batas klaim:
--   * Ini BUKAN dualitas Poincaré kontinu pada manifold mulus.
--   * Tidak ada klaim tentang koefisien medan umum, orientasi dimensi tinggi,
--     atau isomorfisme H^k ≅ H_{n-k} untuk n > 1.
--   * Yang dibuktikan hanya aljabar modul bebas hingga atas ℤ pada siklus C3.

import Mathlib.Tactic

namespace Math30.Topology.DiscretePoincareDuality

/-- Rantai 0 (0-chain) pada siklus C3: nilai di setiap simpul. -/
abbrev Chain0 := Fin 3 → ℤ

/-- Rantai 1 (1-chain) pada siklus C3: nilai di setiap sisi. -/
abbrev Chain1 := Fin 3 → ℤ

/-- Operator batas ∂₁: sisi i memiliki titik awal simpul i dan titik akhir i+1 (mod 3).
    (∂a) i = a(i-1) - a(i)  (dengan indeks siklik). -/
def bdry (a : Chain1) (i : Fin 3) : ℤ :=
  match i.val with
  | 0 => a 2 - a 0
  | 1 => a 0 - a 1
  | _ => a 1 - a 2

/-- Koboundary d⁰: (df) i = f(i+1) - f(i). -/
def cobdry (f : Chain0) (i : Fin 3) : ℤ :=
  match i.val with
  | 0 => f 1 - f 0
  | 1 => f 2 - f 1
  | _ => f 0 - f 2

/-- Jumlah total koordinat (peta augmentasi C₀ → ℤ). -/
def total (f : Chain0) : ℤ := f 0 + f 1 + f 2

/-- Siklus fundamental: semua sisi bernilai 1. -/
def fundamentalCycle : Chain1 := fun _ => 1

/-- Vektor basis C₀ di simpul j. -/
def basis (j : Fin 3) : Chain0 := fun i => if i = j then 1 else 0

/-- Pasangan evaluasi ⟨f, a⟩ = Σ f_i * a_i. -/
def pair (f : Chain0) (a : Chain1) : ℤ := f 0 * a 0 + f 1 * a 1 + f 2 * a 2

/-- Batas selalu berjumlah nol (siklus tertutup). -/
theorem total_bdry (b : Chain1) : total (bdry b) = 0 := by
  simp [total, bdry]

/-- Ker ∂₁ = siklus = rantai sisi konstan. -/
theorem bdry_eq_zero_iff_const (a : Chain1) :
    bdry a = 0 ↔ a 0 = a 1 ∧ a 1 = a 2 := by
  constructor
  · intro h
    have h0 := congrFun h ⟨0, by decide⟩
    have h1 := congrFun h ⟨1, by decide⟩
    simp [bdry] at h0 h1
    constructor <;> omega
  · rintro ⟨h01, h12⟩
    funext i
    fin_cases i <;> simp [bdry] <;> omega

/-- Ker ∂₁ ≅ ℤ: setiap siklus adalah kelipatan siklus fundamental. -/
theorem bdry_kernel_eq_one (a : Chain1) :
    bdry a = 0 ↔ ∃ c : ℤ, a = fun _ => c := by
  constructor
  · intro h
    obtain ⟨h01, h12⟩ := (bdry_eq_zero_iff_const a).1 h
    refine ⟨a 0, ?_⟩
    funext i
    fin_cases i <;> simp [h01, h12]
  · rintro ⟨c, rfl⟩
    funext i
    fin_cases i <;> simp [bdry]

/-- Im ∂₁ = {f | total f = 0}: penjumlahan turun ke coker ∂₁. -/
theorem total_eq_zero_iff_mem (f : Chain0) :
    total f = 0 ↔ ∃ b : Chain1, bdry b = f := by
  constructor
  · intro hf
    have hf' : f 0 + f 1 + f 2 = 0 := by simpa [total] using hf
    refine ⟨fun i => match i.val with
      | 0 => 0
      | 1 => - f 1
      | _ => f 0, ?_⟩
    funext i
    fin_cases i
    · simp [bdry]
    · simp [bdry]
    · simp [bdry]
      omega
  · rintro ⟨b, rfl⟩
    exact total_bdry b

/-- Pasangan evaluasi terhadap vektor basis: ⟨e_j, a⟩ = a_j. -/
theorem pair_basis (j : Fin 3) (a : Chain1) : pair (basis j) a = a j := by
  fin_cases j <;> simp [pair, basis]

/-- Pasangan terhadap vektor satu: ⟨f, 1⟩ = total f. -/
theorem pair_one_right (f : Chain0) : pair f fundamentalCycle = total f := by
  simp [pair, total, fundamentalCycle]

/-- Linearitas pasangan pada argumen pertama. -/
theorem pair_add (f g : Chain0) (a : Chain1) :
    pair (f + g) a = pair f a + pair g a := by
  simp [pair, Pi.add_apply, add_mul]
  ring

/-- Batas adalah nol di bawah pasangan dengan siklus (Stokes diskrit). -/
theorem pair_bdry_zero {a b : Chain1} (ha : bdry a = 0) :
    pair (bdry b) a = 0 := by
  rw [bdry_kernel_eq_one] at ha
  obtain ⟨c, rfl⟩ := ha
  simp [pair, bdry]
  ring

/-- Pasangan turun ke coker ∂₁ × ker ∂₁: penambahan batas tidak mengubah nilai. -/
theorem pair_descends {f b : Chain0} {a : Chain1} (ha : bdry a = 0) :
    pair (f + bdry b) a = pair f a := by
  rw [pair_add, pair_bdry_zero ha, add_zero]

/-- Non-degenerasi kiri: kelas nol di coker ∂₁ terdeteksi oleh siklus. -/
theorem pair_nondegenerate_left (f : Chain0)
    (h : ∀ a : Chain1, bdry a = 0 → pair f a = 0) : total f = 0 := by
  have hker : bdry fundamentalCycle = 0 := by
    rw [bdry_kernel_eq_one]
    exact ⟨1, rfl⟩
  have h1 := h fundamentalCycle hker
  simpa [pair_one_right] using h1

/-- Non-degenerasi kanan: rantai nol terdeteksi oleh kelas C₀.  The cycle
    hypothesis is not needed: vanishing against every basis vector already
    forces the chain to be zero. -/
theorem pair_nondegenerate_right (a : Chain1)
    (h : ∀ f : Chain0, pair f a = 0) : a = 0 := by
  funext i
  have hi := h (basis i)
  simpa [pair_basis] using hi

/-- Dualitas Poincaré diskrit n = 1 (siklus C3):
    ker ∂₁ ≅ ℤ, coker ∂₁ ≅ ℤ, dan pasangan evaluasi perfect. -/
theorem poincare_duality_circle :
    (∀ a : Chain1, bdry a = 0 ↔ ∃ c : ℤ, a = fun _ => c) ∧
    (∀ f : Chain0, total f = 0 ↔ ∃ b : Chain1, bdry b = f) ∧
    (∀ f : Chain0, (∀ a : Chain1, bdry a = 0 → pair f a = 0) → total f = 0) ∧
    (∀ a : Chain1, (∀ f : Chain0, pair f a = 0) → a = 0) :=
  ⟨bdry_kernel_eq_one, total_eq_zero_iff_mem,
   pair_nondegenerate_left, pair_nondegenerate_right⟩

/-- Verifikasi numerik: evaluasi siklus fundamental oleh vektor satu = 3. -/
theorem pair_fundamental_eval :
    pair (fun _ => (1 : ℤ)) fundamentalCycle = 3 := by
  decide

end Math30.Topology.DiscretePoincareDuality
