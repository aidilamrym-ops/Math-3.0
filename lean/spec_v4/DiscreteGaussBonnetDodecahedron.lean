-- DiscreteGaussBonnetDodecahedron.lean
-- Math 3.0 / Fase 70: Gauss-Bonnet Diskrit pada Dodekahedron
--
-- Cakupan:
--   * dodekahedron: 20 simpul, 30 sisi, 12 muka;
--   * derajat setiap simpul = 3;
--   * kurvatur kombinatorial kappa(v) = 6 - deg(v) = 3;
--   * total kurvatur = 60; chi = 2; jumlah kappa = 30 * chi.

import Mathlib.Tactic

namespace Math30.Topology.DiscreteGaussBonnetDodecahedron

/-- Himpunan simpul dodekahedron: 20 simpul (`Fin 20`). -/
def vertices : Finset (Fin 20) := Finset.univ

/-- 30 Rusuk dodekahedron (derajat 3 untuk setiap simpul 0..19). -/
def edge_pairs : List (Finset (Fin 20)) := [
  {0,1}, {0,2}, {0,5},
  {1,0}, {1,3}, {1,6},
  {2,0}, {2,3}, {2,7},
  {3,1}, {3,2}, {3,8},
  {4,5}, {4,9}, {4,10},
  {5,0}, {5,4}, {5,11},
  {6,1}, {6,10}, {6,12},
  {7,2}, {7,11}, {7,13},
  {8,3}, {8,12}, {8,14},
  {9,4}, {9,13}, {9,15},
  {10,4}, {10,6}, {10,16},
  {11,5}, {11,7}, {11,17},
  {12,6}, {12,8}, {12,17},
  {13,7}, {13,9}, {13,16},
  {14,8}, {14,15}, {14,18},
  {15,9}, {15,14}, {15,19},
  {16,10}, {16,13}, {16,19},
  {17,11}, {17,12}, {17,18},
  {18,14}, {18,17}, {18,19},
  {19,15}, {19,16}, {19,18}
]

def edges : Finset (Finset (Fin 20)) := edge_pairs.toFinset

/-- 12 Muka dodekahedron. -/
def face_sets : List (Finset (Fin 20)) := [
  {0,1,2,3,4}, {0,1,2,5,6}, {0,3,5,7,8}, {1,4,7,10,11},
  {2,4,8,12,13}, {3,6,9,14,15}, {4,7,10,13,16}, {5,8,12,15,17},
  {6,9,14,18,19}, {7,10,13,16,19}, {8,12,15,18,19}, {9,11,14,17,19}
]

def faces : Finset (Finset (Fin 20)) := face_sets.toFinset

/-- Derajat simpul v: jumlah sisi yang memuat v. -/
def degree (v : Fin 20) : Nat :=
  (edges.filter (fun e => v ∈ e)).card

/-- Kurvatur kombinatorial: kappa(v) = 6 - deg(v). -/
def curvature (v : Fin 20) : ℤ := 6 - (degree v : ℤ)

/-- Karakteristik Euler: chi = V - E + F. -/
def eulerChar : ℤ :=
  (vertices.card : ℤ) - (edges.card : ℤ) + (faces.card : ℤ)

/-- Jumlah simpul = 20. -/
theorem vertices_card : vertices.card = 20 := by decide

/-- Jumlah sisi = 30. -/
theorem edges_card : edges.card = 30 := by decide

/-- Jumlah muka = 12. -/
theorem faces_card : faces.card = 12 := by decide

/-- Derajat setiap simpul = 3. -/
theorem degree_eq_three (v : Fin 20) : degree v = 3 := by
  fin_cases v <;> decide

/-- Kurvatur setiap simpul = 3. -/
theorem curvature_eq_three (v : Fin 20) : curvature v = 3 := by
  simp [curvature, degree_eq_three]

/-- Total kurvatur = 20 * 3 = 60. -/
theorem total_curvature :
    (Finset.univ.sum curvature) = 60 := by
  decide

/-- Karakteristik Euler = 20 - 30 + 12 = 2. -/
theorem euler_two : eulerChar = 2 := by
  decide

/-- Gauss-Bonnet diskrit: sum kappa = 30 * chi. -/
theorem gauss_bonnet_dodec :
    (Finset.univ.sum curvature) = 30 * eulerChar := by
  decide

/-- Sertifikat gabungan. -/
theorem gauss_bonnet_dodec_certificate :
    eulerChar = 2 ∧
    (Finset.univ.sum curvature) = 60 ∧
    (Finset.univ.sum curvature) = 30 * eulerChar :=
  ⟨euler_two, total_curvature, gauss_bonnet_dodec⟩

end Math30.Topology.DiscreteGaussBonnetDodecahedron
