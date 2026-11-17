-- DiscreteMorseTheory.lean
-- Math 3.0 / Fase 62: Teori Morse Diskrit
--
-- Cakupan:
--   * definisi fungsi Morse diskrit pada graf hingga (tiap vertex punya
--     paling banyak 1 tetangga bernilai lebih kecil dan 1 lebih besar);
--   * definisi sel kritis indeks 0 (minimum lokal) dan indeks 1 (maksimum lokal);
--   * gradien diskrit dan struktur kompleks Morse hingga;
--   * verifikasi konkret untuk interval 1D dan siklus C4.
--
-- Batas klaim:
--   * Ini BUKAN teori Morse kontinu pada manifold mulus.
--   * Tidak ada klaim tentang handlebody, h-cobordisme, teori Smale,
--     atau homologi Morse penuh.
--   * `Cycle4Graph` adalah siklus C4, BUKAN 1-skeleton torus T²; nama lama
--     "torus" hanya label historis dan telah dihapus.
--   * `critical_count_*` hanyalah batas kardinalitas; ini bukan ketidaksamaan
--     Morse homologis (mᵢ ≥ bᵢ) karena homologi tidak dihitung di sini.
--   * Yang dibuktikan hanya aljabar hingga pada Finset berhingga.

import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Tactic

open Finset

namespace Math30.Topology.DiscreteMorse

/-- Kompleks simplicial diskrit: himpunan vertex dan edge (graf hingga). -/
structure SimplicialComplex (V : Type*) where
  vertices : Finset V
  edges : Finset (V × V)

/-- Tetangga vertex v dalam kompleks. -/
def neighbors {V : Type*} [DecidableEq V] (K : SimplicialComplex V) (v : V) : Finset V :=
  (K.edges.filter (fun e => e.1 = v)).image (fun e => e.2) ∪
  (K.edges.filter (fun e => e.2 = v)).image (fun e => e.1)

/-- Fungsi Morse diskrit: tiap vertex punya ≤ 1 tetangga lebih kecil
    dan ≤ 1 tetangga lebih besar. -/
def DiscreteMorseFunction {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) : Prop :=
  ∀ v ∈ K.vertices,
    (Finset.filter (fun u => f u < f v) (neighbors K v)).card ≤ 1 ∧
    (Finset.filter (fun u => f u > f v) (neighbors K v)).card ≤ 1

/-- Sel kritis indeks 0: minimum lokal (tidak ada tetangga lebih kecil). -/
def IsCriticalIndex0 {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) (v : V) : Prop :=
  v ∈ K.vertices ∧ (Finset.filter (fun u => f u < f v) (neighbors K v)).card = 0

/-- Sel kritis indeks 1: maksimum lokal (tidak ada tetangga lebih besar). -/
def IsCriticalIndex1 {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) (v : V) : Prop :=
  v ∈ K.vertices ∧ (Finset.filter (fun u => f u > f v) (neighbors K v)).card = 0

/-- Gradien diskrit: pasangan (v, w) dengan f(w) > f(v) pada edge. -/
def DiscreteGradient {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) : Finset (V × V) :=
  K.edges.filter (fun e => f e.1 < f e.2)

/-- Himpunan sel kritis indeks 0 (minimum lokal). -/
def critical0 {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) : Finset V :=
  K.vertices.filter (fun v => (Finset.filter (fun u => f u < f v) (neighbors K v)).card = 0)

/-- Himpunan sel kritis indeks 1 (maksimum lokal). -/
def critical1 {V : Type*} [DecidableEq V] (f : V → ℕ) (K : SimplicialComplex V) : Finset V :=
  K.vertices.filter (fun v => (Finset.filter (fun u => f u > f v) (neighbors K v)).card = 0)

/-- Kompleks Morse: rantai dibangun dari sel kritis dan gradien. -/
structure MorseComplex (V : Type*) [DecidableEq V] where
  critical0 : Finset V
  critical1 : Finset V
  gradient : Finset (V × V)

/-- Graf interval 1D: 0 -- 1 -- 2. -/
def IntervalGraph : SimplicialComplex (Fin 3) :=
  { vertices := Finset.univ,
    edges := { (0, 1), (1, 2) } }

/-- Fungsi Morse pada interval: f(i) = i. -/
def intervalMorseFunction : Fin 3 → ℕ :=
  fun i => i.val

/-- Verifikasi fungsi Morse pada interval. -/
theorem interval_is_morse :
    DiscreteMorseFunction intervalMorseFunction IntervalGraph := by
  intro v _hv
  fin_cases v
  all_goals decide

/-- Sel kritis indeks 0 pada interval: vertex 0. -/
theorem interval_critical0 :
    IsCriticalIndex0 intervalMorseFunction IntervalGraph 0 := by
  simp only [IsCriticalIndex0]
  constructor
  · simp [IntervalGraph]
  · decide

/-- Sel kritis indeks 1 pada interval: vertex 2. -/
theorem interval_critical1 :
    IsCriticalIndex1 intervalMorseFunction IntervalGraph 2 := by
  simp only [IsCriticalIndex1]
  constructor
  · simp [IntervalGraph]
  · decide

/-- Gradien diskrit pada interval: (0,1) dan (1,2). -/
theorem interval_gradient :
    DiscreteGradient intervalMorseFunction IntervalGraph = { (0, 1), (1, 2) } := by
  decide

/-- Jumlah minimum pada interval: tepat 1. -/
theorem interval_critical0_card :
    (critical0 intervalMorseFunction IntervalGraph).card = 1 := by
  decide

/-- Kompleks Morse untuk interval. -/
def intervalMorseComplex : MorseComplex (Fin 3) :=
  { critical0 := critical0 intervalMorseFunction IntervalGraph,
    critical1 := critical1 intervalMorseFunction IntervalGraph,
    gradient := DiscreteGradient intervalMorseFunction IntervalGraph }

/-- Siklus C4: 0 -- 1 -- 2 -- 3 -- 0. Ini bukan 1-skeleton torus. -/
def Cycle4Graph : SimplicialComplex (Fin 4) :=
  { vertices := Finset.univ,
    edges := { (0, 1), (1, 2), (2, 3), (3, 0) } }

/-- Fungsi Morse pada siklus: f = [0, 1, 1, 0]. -/
def cycle4MorseFunction : Fin 4 → ℕ :=
  fun i => match i.val with
    | 0 => 0
    | 1 => 1
    | 2 => 1
    | _ => 0

/-- Verifikasi fungsi Morse pada siklus C4. -/
theorem cycle4_is_morse :
    DiscreteMorseFunction cycle4MorseFunction Cycle4Graph := by
  intro v _hv
  fin_cases v
  all_goals decide

/-- Sel kritis indeks 0 pada siklus: vertex 0. -/
theorem cycle4_critical_min :
    IsCriticalIndex0 cycle4MorseFunction Cycle4Graph 0 := by
  simp only [IsCriticalIndex0]
  constructor
  · simp [Cycle4Graph]
  · decide

/-- Sel kritis indeks 1 pada siklus: vertex 2. -/
theorem cycle4_critical_max :
    IsCriticalIndex1 cycle4MorseFunction Cycle4Graph 2 := by
  simp only [IsCriticalIndex1]
  constructor
  · simp [Cycle4Graph]
  · decide

/-- Jumlah minimum pada siklus: tepat 2. -/
theorem cycle4_critical0_card :
    (critical0 cycle4MorseFunction Cycle4Graph).card = 2 := by
  decide

/-- Jumlah maksimum pada siklus: tepat 2. -/
theorem cycle4_critical1_card :
    (critical1 cycle4MorseFunction Cycle4Graph).card = 2 := by
  decide

/-- Pada C4, sel kritis indeks 0 dan 1 berjumlah sama; selisihnya nol. -/
theorem cycle4_critical_euler :
    (critical0 cycle4MorseFunction Cycle4Graph).card -
      (critical1 cycle4MorseFunction Cycle4Graph).card = 0 := by
  decide

/-- Batas kardinalitas interval: #minimum ≥ 1 (bukan ketidaksamaan Morse homologis). -/
theorem critical_count_interval_ge_one :
    (critical0 intervalMorseFunction IntervalGraph).card ≥ 1 := by
  have h := interval_critical0_card
  omega

/-- Batas kardinalitas siklus C4: #minimum ≥ 1 dan #maksimum ≥ 1. -/
theorem critical_count_cycle4_ge_one :
    (critical0 cycle4MorseFunction Cycle4Graph).card ≥ 1 ∧
    (critical1 cycle4MorseFunction Cycle4Graph).card ≥ 1 := by
  have h0 := cycle4_critical0_card
  have h1 := cycle4_critical1_card
  constructor <;> omega

/-- Spektrum kritis interval dan siklus C4 untuk analisis Betti/Morse berhingga. -/
theorem morse_critical_spectrum_relation :
    (critical0 intervalMorseFunction IntervalGraph).card = 1 ∧
    (critical0 cycle4MorseFunction Cycle4Graph).card = 2 := by
  constructor
  · exact interval_critical0_card
  · exact cycle4_critical0_card

#print axioms interval_is_morse
#print axioms cycle4_is_morse
#print axioms cycle4_critical_euler
#print axioms morse_critical_spectrum_relation

end Math30.Topology.DiscreteMorse
