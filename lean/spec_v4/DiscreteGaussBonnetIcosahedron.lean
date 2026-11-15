-- DiscreteGaussBonnetIcosahedron.lean
-- Math 3.0 / Fase 69: Gauss-Bonnet Diskrit pada Ikosahedron (permukaan triangulasi)
--
-- Cakupan:
--   * kompleks simplicial hingga: ikosahedron, 12 simpul, 30 sisi, 20 muka segitiga;
--   * derajat setiap simpul = 5; kurvatur kappa(v) = 6 - 5 = 1;
--   * total kurvatur = 12; chi = 12 - 30 + 20 = 2;
--   * identitas Gauss-Bonnet diskrit: jumlah kappa = 6 * chi.

import Mathlib.Tactic

namespace Math30.Topology.DiscreteGaussBonnetIcosahedron

/-- Himpunan simpul ikosahedron: 12 simpul (`Fin 12`). -/
def vertices : Finset (Fin 12) := Finset.univ

/-- 30 Rusuk ikosahedron sebagai pasangan (i, j) dengan i < j. -/
def edge_pairs : List (Finset (Fin 12)) := [
  {0,1}, {0,2}, {0,3}, {0,4}, {0,5},
  {1,2}, {1,5}, {1,6}, {1,7},
  {2,3}, {2,7}, {2,8},
  {3,4}, {3,8}, {3,9},
  {4,5}, {4,9}, {4,10},
  {5,6}, {5,10},
  {6,7}, {6,10}, {6,11},
  {7,8}, {7,11},
  {8,9}, {8,11},
  {9,10}, {9,11},
  {10,11}
]

def edges : Finset (Finset (Fin 12)) := edge_pairs.toFinset

/-- 20 Muka segitiga ikosahedron. -/
def face_triples : List (Finset (Fin 12)) := [
  {0,1,2}, {0,2,3}, {0,3,4}, {0,4,5}, {0,5,1},
  {1,2,7}, {1,6,7}, {1,5,6},
  {2,3,8}, {2,7,8},
  {3,4,9}, {3,8,9},
  {4,5,10}, {4,9,10},
  {5,6,10},
  {6,7,11}, {7,8,11}, {8,9,11}, {9,10,11}, {6,10,11}
]

def faces : Finset (Finset (Fin 12)) := face_triples.toFinset

/-- Derajat simpul v: jumlah sisi yang memuat v. -/
def degree (v : Fin 12) : Nat :=
  (edges.filter (fun e => v ∈ e)).card

/-- Kurvatur kombinatorial: kappa(v) = 6 - deg(v). -/
def curvature (v : Fin 12) : ℤ := 6 - (degree v : ℤ)

/-- Karakteristik Euler: chi = V - E + F. -/
def eulerChar : ℤ :=
  (vertices.card : ℤ) - (edges.card : ℤ) + (faces.card : ℤ)

/-- Jumlah simpul = 12. -/
theorem vertices_card : vertices.card = 12 := by decide

/-- Jumlah sisi = 30. -/
theorem edges_card : edges.card = 30 := by decide

/-- Jumlah muka = 20. -/
theorem faces_card : faces.card = 20 := by decide

/-- Derajat setiap simpul ikosahedron = 5. -/
theorem degree_eq_five (v : Fin 12) : degree v = 5 := by
  fin_cases v <;> decide

/-- Kurvatur setiap simpul = 1. -/
theorem curvature_eq_one (v : Fin 12) : curvature v = 1 := by
  simp [curvature, degree_eq_five]

/-- Total kurvatur = 12 * 1 = 12. -/
theorem total_curvature :
    curvature 0 + curvature 1 + curvature 2 + curvature 3 +
    curvature 4 + curvature 5 + curvature 6 + curvature 7 +
    curvature 8 + curvature 9 + curvature 10 + curvature 11 = 12 := by
  decide

/-- Karakteristik Euler ikosahedron = 12 - 30 + 20 = 2. -/
theorem euler_two : eulerChar = 2 := by
  decide

/-- Gauss-Bonnet diskrit: jumlah kappa = 6 * chi. -/
theorem gauss_bonnet_icosa :
    curvature 0 + curvature 1 + curvature 2 + curvature 3 +
    curvature 4 + curvature 5 + curvature 6 + curvature 7 +
    curvature 8 + curvature 9 + curvature 10 + curvature 11 = 6 * eulerChar := by
  decide

/-- Sertifikat gabungan: chi = 2, total kurvatur = 12, dan Gauss-Bonnet. -/
theorem gauss_bonnet_icosa_certificate :
    eulerChar = 2 ∧
    curvature 0 + curvature 1 + curvature 2 + curvature 3 +
    curvature 4 + curvature 5 + curvature 6 + curvature 7 +
    curvature 8 + curvature 9 + curvature 10 + curvature 11 = 12 ∧
    curvature 0 + curvature 1 + curvature 2 + curvature 3 +
    curvature 4 + curvature 5 + curvature 6 + curvature 7 +
    curvature 8 + curvature 9 + curvature 10 + curvature 11 = 6 * eulerChar :=
  ⟨euler_two, total_curvature, gauss_bonnet_icosa⟩

end Math30.Topology.DiscreteGaussBonnetIcosahedron
