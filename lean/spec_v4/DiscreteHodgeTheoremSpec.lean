-- DiscreteHodgeTheoremSpec.lean
-- Math 3.0 / Fase 72: Spesifikasi Teorema Hodge Diskrit (kernel Laplacian, dekomposisi harmonik)

import Mathlib.Tactic

namespace Math30.Topology.DiscreteHodgeTheoremSpec

abbrev Chain0 := Fin 3 → ℤ
abbrev Chain1 := Fin 2 → ℤ

def laplacian0 (f : Chain0) : Chain0 := fun v =>
  match v.val with
  | 0 => f 0 - f 1
  | 1 => f 1 - f 0 + (f 1 - f 2)
  | _ => f 2 - f 1

def laplacian1 (a : Chain1) : Chain1 := fun e =>
  match e.val with
  | 0 => a 0
  | _ => a 1

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
      simp [harmonic0, laplacian0]
      omega
    }

theorem harmonic1_iff_zero (h : Chain1) :
    harmonic1 h ↔ h = 0 := by
  constructor
  · intro hh
    funext e
    have he := congrFun hh e
    fin_cases e <;> {
      change laplacian1 h _ = 0 at he
      simp [laplacian1] at he
      exact he
    }
  · intro h0
    subst h0
    funext e
    fin_cases e <;> rfl

theorem hodge_spec_certificate :
    (∀ h : Chain0, harmonic0 h ↔ (h 0 = h 1 ∧ h 1 = h 2)) ∧
    (∀ h : Chain1, harmonic1 h ↔ h = 0) :=
  ⟨harmonic0_iff_constant, harmonic1_iff_zero⟩

end Math30.Topology.DiscreteHodgeTheoremSpec
