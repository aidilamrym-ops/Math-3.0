-- DiscretePersistentHomology.lean
-- Math 3.0 / Fase 65: Homologi Persisten Diskrit (filtrasi graf, n = 1)
--
-- Cakupan:
--   * filtrasi graf pada 3 simpul: simpul lahir di t = 0, sisi lahir di t = 1, 2, 3;
--   * bilangan Betti β₀(t), β₁(t) sebagai fungsi tingkat filtrasi;
--   * dekomposisi interval: [(0,1), (0,2), (0,∞)] untuk H₀ dan [(3,∞)] untuk H₁;
--   * β_k(t) = jumlah interval yang hidup pada t (birth ≤ t < death);
--   * identitas Euler β₀ + E = β₁ + V pada setiap tingkat.
--
-- Batas klaim:
--   * Ini BUKAN teorema stabilitas (Bottleneck / Gromov–Hausdorff) kontinu.
--   * Tidak ada klaim tentang filtrasi Vietoris–Rips umum, koefisien medan,
--     atau algoritma matriks reduksi untuk kompleks arbitrer.
--   * Yang dibuktikan hanya contoh hingga eksplisit: filtrasi graf 3 simpul
--     dengan dekomposisi interval yang dihitung langsung.

import Mathlib.Tactic

namespace Math30.Topology.DiscretePersistentHomology

/-- Sisi pada graf 3 simpul: sisi 0 = (0,1), sisi 1 = (1,2), sisi 2 = (2,0). -/
abbrev Edge := Fin 3

/-- Waktu kelahiran sisi: e₀ di t = 1, e₁ di t = 2, e₂ di t = 3. -/
def ebirth : Edge → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 2
  | _ => 3

/-- Jumlah sisi yang sudah lahir pada tingkat t. -/
def numEdges (t : Nat) : Nat :=
  (if 1 ≤ t then 1 else 0) + (if 2 ≤ t then 1 else 0) + (if 3 ≤ t then 1 else 0)

/-- Jumlah komponen terhubung K_t (semua simpul lahir di t = 0). -/
def comps : Nat → Nat
  | 0 => 3
  | 1 => 2
  | _ => 1

/-- β₀(t): komponen terhubung. -/
def betti0 (t : Nat) : Nat := comps t

/-- β₁(t): siklus independen; β₁ = E - V + c dengan V = 3. -/
def betti1 (t : Nat) : Nat := numEdges t + comps t - 3

/-- Interval kelahiran–kematian untuk H₀. `none` berarti tak pernah mati. -/
def intervals0 : List (Nat × Option Nat) :=
  [(0, some 1), (0, some 2), (0, none)]

/-- Interval kelahiran–kematian untuk H₁: siklus lahir di t = 3, abadi. -/
def intervals1 : List (Nat × Option Nat) :=
  [(3, none)]

/-- Interval (b, d) hidup pada t bila b ≤ t dan (d = none atau t < d). -/
def alive (t : Nat) : Nat × Option Nat → Bool
  | (b, some d) => decide (b ≤ t ∧ t < d)
  | (b, none) => decide (b ≤ t)

/-- Nilai β₀: 3 sebelum t = 1, 2 di t = 1, 1 sejak t = 2. -/
theorem betti0_eq (t : Nat) :
    betti0 t = 3 - (if 1 ≤ t then 1 else 0) - (if 2 ≤ t then 1 else 0) := by
  match t with
  | 0 => rfl
  | 1 => rfl
  | 2 => rfl
  | n + 3 => simp [betti0, comps]

/-- Nilai β₁: nol sampai t = 2, satu sejak t = 3 (siklus tertutup). -/
theorem betti1_eq (t : Nat) :
    betti1 t = if 3 ≤ t then 1 else 0 := by
  match t with
  | 0 => rfl
  | 1 => rfl
  | 2 => rfl
  | n + 3 => simp [betti1, numEdges, comps]

/-- β₀ dihitung oleh interval H₀ yang hidup. -/
theorem betti0_eq_alive (t : Nat) :
    betti0 t = (intervals0.filter (alive t)).length := by
  match t with
  | 0 => rfl
  | 1 => rfl
  | 2 => rfl
  | n + 3 => simp [betti0, comps, intervals0, alive]

/-- β₁ dihitung oleh interval H₁ yang hidup. -/
theorem betti1_eq_alive (t : Nat) :
    betti1 t = (intervals1.filter (alive t)).length := by
  match t with
  | 0 => rfl
  | 1 => rfl
  | 2 => rfl
  | n + 3 => simp [betti1, numEdges, comps, intervals1, alive]

/-- Identitas Euler pada setiap tingkat: β₀ + E = β₁ + V, dengan V = 3. -/
theorem euler_characteristic (t : Nat) :
    betti0 t + numEdges t = betti1 t + 3 := by
  have h : 3 ≤ numEdges t + comps t := by
    match t with
    | 0 => decide
    | 1 => decide
    | 2 => decide
    | n + 3 => simp [numEdges, comps]
  simp only [betti0, betti1]
  omega

/-- β₀ tidak bertambah saat filtrasi maju (kelas hanya mati). -/
theorem betti0_monotone {s t : Nat} (hst : s ≤ t) : betti0 t ≤ betti0 s := by
  rw [betti0_eq, betti0_eq]
  split_ifs <;> omega

/-- β₁ tidak berkurang saat filtrasi maju (kelas hanya lahir). -/
theorem betti1_monotone {s t : Nat} (hst : s ≤ t) : betti1 s ≤ betti1 t := by
  rw [betti1_eq, betti1_eq]
  split_ifs <;> omega

/-- Dua interval H₀ berhingga (mati di t = 1 dan t = 2). -/
theorem intervals0_finite_count :
    (intervals0.filter (fun p => p.2.isSome)).length = 2 := by
  decide

/-- Satu interval H₁ tak berhingga (siklus fundamental). -/
theorem intervals1_infinite_count :
    (intervals1.filter (fun p => p.2.isNone)).length = 1 := by
  decide

/-- Verifikasi tabel: (t, β₀, β₁) untuk t = 0..4. -/
theorem betti_table :
    (betti0 0, betti1 0) = (3, 0) ∧
    (betti0 1, betti1 1) = (2, 0) ∧
    (betti0 2, betti1 2) = (1, 0) ∧
    (betti0 3, betti1 3) = (1, 1) ∧
    (betti0 4, betti1 4) = (1, 1) := by
  decide

/-- Spektrum bilangan Betti untuk seluruh rentang waktu t = 0..3. -/
theorem betti_spectrum_range :
    [betti0 0, betti0 1, betti0 2, betti0 3] = [3, 2, 1, 1] ∧
    [betti1 0, betti1 1, betti1 2, betti1 3] = [0, 0, 0, 1] := by
  constructor <;> decide

#print axioms betti_table
#print axioms betti_spectrum_range

end Math30.Topology.DiscretePersistentHomology
