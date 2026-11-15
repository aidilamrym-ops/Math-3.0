-- DiscreteLefschetzFixedPoint.lean
-- Math 3.0 / Fase 66: Bilangan Lefschetz Diskrit (contoh P₃, refleksi)
--
-- Cakupan:
--   * kompleks rantai path P₃: simpul {0,1,2}, sisi e₀ = (0,1), e₁ = (1,2);
--   * refleksi σ: 0 ↦ 2, 1 ↦ 1, 2 ↦ 0 pada simpul, dengan tanda −1 pada sisi
--     (σ membalik orientasi);
--   * peta rantai σ_# memenuhi ∂ σ_# = σ_# ∂ (naturalitas batas);
--   * bilangan Lefschetz L = tr(C₀) − tr(C₁) = 1 − 0 = 1;
--   * H₁(P₃) = 0 (ker ∂₁ = 0), jadi tr(H₀) − tr(H₁) = 1;
--   * jumlah simpleks tetap: 1 simpul tetap, 0 sisi tetap (setwise).
--
-- Batas klaim:
--   * Ini BUKAN teorema Lefschetz–Hopf umum untuk kompleks simplicial arbitrer.
--   * Tidak ada klaim tentang indeks titik tetap interior, peta non-simplicial,
--     atau ruang kontinum.
--   * Yang dibuktikan hanya identitas numerik untuk satu peta simplicial eksplisit.

import Mathlib.Tactic

namespace Math30.Topology.DiscreteLefschetz

/-- Rantai 0 pada path P₃. -/
abbrev Chain0 := Fin 3 → ℤ

/-- Rantai 1 pada path P₃: dua sisi. -/
abbrev Chain1 := Fin 2 → ℤ

/-- Batas ∂₁: ∂e₀ = v₁ − v₀, ∂e₁ = v₂ − v₁. -/
def bdry (a : Chain1) (v : Fin 3) : ℤ :=
  match v.val with
  | 0 => - a 0
  | 1 => a 0 - a 1
  | _ => a 1

/-- Refleksi simpul: 0 ↦ 2, 1 ↦ 1, 2 ↦ 0. -/
def reflV (v : Fin 3) : Fin 3 :=
  match v.val with
  | 0 => 2
  | 1 => 1
  | _ => 0

/-- Refleksi sisi dengan pembalikan orientasi: e₀ ↦ −e₁, e₁ ↦ −e₀. -/
def reflE (a : Chain1) : Chain1 := fun i =>
  match i.val with
  | 0 => - a 1
  | _ => - a 0

/-- Peta tarik-balik pada 0-rantai: (σ_# f)(v) = f(σ v). -/
def pushV (f : Chain0) : Chain0 := fun v => f (reflV v)

/-- Basis 0-rantai di simpul j. -/
def basis0 (j : Fin 3) : Chain0 := fun i => if i = j then 1 else 0

/-- Basis 1-rantai di sisi j. -/
def basis1 (j : Fin 2) : Chain1 := fun i => if i = j then 1 else 0

/-- Jejak pada C₀ (matriks 3×3). -/
def trace0 (φ : Chain0 → Chain0) : ℤ :=
  φ (basis0 0) 0 + φ (basis0 1) 1 + φ (basis0 2) 2

/-- Jejak pada C₁ (matriks 2×2). -/
def trace1 (φ : Chain1 → Chain1) : ℤ :=
  φ (basis1 0) 0 + φ (basis1 1) 1

/-- Bilangan Lefschetz rantai: L = tr(C₀) − tr(C₁). -/
def lefschetz : ℤ := trace0 pushV - trace1 reflE

/-- Naturalitas batas: ∂ σ_# = σ_# ∂. -/
theorem chain_map (a : Chain1) : bdry (reflE a) = pushV (bdry a) := by
  funext v
  fin_cases v
  · simp [bdry, reflE, pushV, reflV]
  · simp [bdry, reflE, pushV, reflV]
    ring
  · simp [bdry, reflE, pushV, reflV]

/-- Jejak pada C₀ = 1 (hanya simpul 1 tetap). -/
theorem trace0_eq : trace0 pushV = 1 := by
  decide

/-- Jejak pada C₁ = 0 (tidak ada sisi tetap, kedua sisi bertukar dengan tanda). -/
theorem trace1_eq : trace1 reflE = 0 := by
  decide

/-- Bilangan Lefschetz refleksi: L = 1. -/
theorem lefschetz_eq : lefschetz = 1 := by
  simp [lefschetz, trace0_eq, trace1_eq]

/-- Jumlah simpul tetap refleksi = 1. -/
theorem fixed_vertex_count :
    (Finset.univ.filter (fun v : Fin 3 => reflV v = v)).card = 1 := by
  decide

/-- Tidak ada sisi tetap setwise (baik searah maupun terbalik). -/
theorem no_fixed_edge (i : Fin 2) :
    ¬ (reflE (basis1 i) = basis1 i) ∧ ¬ (reflE (basis1 i) = - basis1 i) := by
  fin_cases i <;> decide

/-- Jumlah sisi tetap setwise = 0. -/
theorem fixed_edge_count :
    (Finset.univ.filter (fun i : Fin 2 =>
      reflE (basis1 i) = basis1 i ∨ reflE (basis1 i) = - basis1 i)).card = 0 := by
  decide

/-- H₁(P₃) = 0: setiap 1-siklus adalah nol. -/
theorem kernel_bdry_zero (a : Chain1) (h : bdry a = 0) : a = 0 := by
  funext i
  have h0 := congrFun h (0 : Fin 3)
  have h1 := congrFun h (1 : Fin 3)
  have h2 := congrFun h (2 : Fin 3)
  simp [bdry] at h0 h1 h2
  fin_cases i <;> simp <;> omega

/-- Verifikasi gabungan: L = 1, satu simpul tetap, nol sisi tetap. -/
theorem lefschetz_refl_certificate :
    lefschetz = 1 ∧
    (Finset.univ.filter (fun v : Fin 3 => reflV v = v)).card = 1 ∧
    (Finset.univ.filter (fun i : Fin 2 =>
      reflE (basis1 i) = basis1 i ∨ reflE (basis1 i) = - basis1 i)).card = 0 :=
  ⟨lefschetz_eq, fixed_vertex_count, fixed_edge_count⟩

end Math30.Topology.DiscreteLefschetz
