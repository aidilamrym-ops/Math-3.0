-- DiscreteHodgeTheoremSpec.lean
-- Math 3.0 / Fase 72: Spesifikasi Teorema Hodge Diskrit (kernel Laplacian)
--
-- Cakupan:
--   * chain complex C0 -> C1 on the path P3 (3 vertices, 2 edges);
--   * d1: C1 -> C0 is the boundary [-1,1,0]; [0,-1,1];
--   * Laplacian0 = d1 d1^T and Laplacian1 = d1^T d1 are the combinatorial
--     graph Laplacians on 0-chains and 1-chains respectively;
--   * harmonic0 h iff h is constant; harmonic1 h iff h = 0.
--
-- Claim limits:
--   * finite linear algebra only; not the Hodge theorem for Riemannian manifolds.

import Mathlib.Tactic

namespace Math30.Topology.DiscreteHodgeTheoremSpec

abbrev Chain0 := Fin 3 → ℤ
abbrev Chain1 := Fin 2 → ℤ

def laplacian0 (f : Chain0) : Chain0 := fun v =>
  match v.val with
  | 0 => f 0 - f 1
  | 1 => f 1 - f 0 + (f 1 - f 2)
  | _ => f 2 - f 1

/-- Combinatorial Laplacian on 1-chains: d1^T d1 = [[2,-1],[-1,2]]. -/
def laplacian1 (a : Chain1) : Chain1 := fun e =>
  match e.val with
  | 0 => 2 * a 0 - a 1
  | _ => - a 0 + 2 * a 1

def harmonic0 (h : Chain0) : Prop := laplacian0 h = 0
def harmonic1 (h : Chain1) : Prop := laplacian1 h = 0

theorem harmonic0_iff_constant (h : Chain0) :
    harmonic0 h ↔ (h 0 = h 1 ∧ h 1 = h 2) := by
  constructor
  · intro hh
    have h0 := congrFun hh 0
    have h1 := congrFun hh 1
    have h2 := congrFun hh 2
    change laplacian0 h 0 = 0 at h0
    change laplacian0 h 1 = 0 at h1
    change laplacian0 h 2 = 0 at h2
    simp [laplacian0] at h0 h1 h2
    omega
  · rintro ⟨h01, h12⟩
    funext v
    fin_cases v <;> {
      simp [laplacian0]
      omega
    }

theorem harmonic1_iff_zero (h : Chain1) :
    harmonic1 h ↔ h = 0 := by
  constructor
  · intro hh
    have h0 := congrFun hh 0
    have h1 := congrFun hh 1
    change laplacian1 h 0 = 0 at h0
    change laplacian1 h 1 = 0 at h1
    simp [laplacian1] at h0 h1
    funext e
    fin_cases e <;> simp <;> omega
  · intro h0
    subst h0
    funext e
    fin_cases e <;> simp [laplacian1]

/-- Ground witness: the nonzero constant 0-cochain `3` is harmonic. -/
theorem harmonic0_constant_three : harmonic0 (fun _ : Fin 3 => (3 : ℤ)) := by
  funext v
  fin_cases v <;> simp [laplacian0]

/-- Ground witness: the zero 1-cochain is harmonic. -/
theorem harmonic1_zero : harmonic1 (fun _ : Fin 2 => (0 : ℤ)) := by
  funext e
  fin_cases e <;> simp [laplacian1]

/-- Non-example: the indicator of the first edge is not harmonic, so the
    harmonic 1-cochain space is genuinely a proper subspace. -/
theorem harmonic1_edge_indicator_not :
    ¬ harmonic1 (fun e : Fin 2 => if e = 0 then (1 : ℤ) else 0) := by
  intro h
  have hz := (harmonic1_iff_zero _).mp h
  have h0 := congrFun hz 0
  simp at h0

theorem hodge_spec_certificate :
    (∀ h : Chain0, harmonic0 h ↔ (h 0 = h 1 ∧ h 1 = h 2)) ∧
    (∀ h : Chain1, harmonic1 h ↔ h = 0) :=
  ⟨harmonic0_iff_constant, harmonic1_iff_zero⟩

#print axioms hodge_spec_certificate
#print axioms harmonic1_edge_indicator_not

end Math30.Topology.DiscreteHodgeTheoremSpec
