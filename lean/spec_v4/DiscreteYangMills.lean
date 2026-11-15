-- DiscreteYangMills.lean
-- Math 3.0 / Fase 61 (rebuilt in Batch 9): Finite Lattice Yang-Mills
--
-- Scope:
--   * a finite 4-torus of sites `Fin 4 -> ZMod L`;
--   * GL(N, C)-valued link variables `U_mu(x)` on every oriented edge; the
--     general gauge-invariance proof uses only invertibility plus trace
--     cyclicity. A concrete determinant-one unitary GL(2, C) link is included
--     as an SU(2) witness;
--   * the plaquette Wilson loop
--       W_{mu nu}(x) = U_mu(x) U_nu(x+mu) U_mu(x+nu)^-1 U_nu(x)^-1;
--   * gauge transformations U_mu(x) -> g(x) U_mu(x) g(x+mu)^-1;
--   * plaquette gauge covariance W -> g(x) W g(x)^-1 and the resulting
--     invariance of Re Tr W under trace cyclicity;
--   * the Wilson action
--       S_beta(U) = beta * sum_{x,mu,nu} (1 - Re Tr W_{mu nu}(x) / N);
--   * the trivial connection has W = 1 and S_beta = 0;
--   * a concrete determinant-one unitary GL(2, C) link produces a non-identity
--     plaquette, so the model is not vacuous.
--
-- Claim limits:
--   * finite lattice model only; links are GL(N, C) matrices, not a continuum
--     gauge field;
--   * the action is defined for N > 0 and L > 0 (`NeZero N`, `NeZero L`);
--     degenerate sizes are outside the model;
--   * no mass gap, confinement, continuum limit, or QCD claim;
--   * the sum runs over ordered pairs (mu, nu), so each geometric plaquette
--     appears twice; that convention is absorbed into beta and no physical
--     normalization of beta is asserted.

import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic

open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteYangMills

/-- Link group: invertible N x N complex matrices. -/
abbrev LinkGroup (N : ℕ) := Matrix.GeneralLinearGroup (Fin N) ℂ

/-- Sites of the finite 4-torus of side length L. -/
abbrev Site (L : ℕ) := Fin 4 → ZMod L

/-- The four coordinate directions. -/
abbrev Dir := Fin 4

/-- A lattice gauge field assigns a link variable to every site and direction. -/
abbrev DiscreteGaugeField (N L : ℕ) := Site L → Dir → LinkGroup N

/-- Translation by one lattice step in direction `d`. -/
def shift {L : ℕ} (d : Dir) (x : Site L) : Site L :=
  Function.update x d (x d + 1)

/-- Unit translations in different directions commute. -/
theorem shift_comm {L : ℕ} (d e : Dir) (x : Site L) :
    shift d (shift e x) = shift e (shift d x) := by
  by_cases h : d = e
  · subst h
    rfl
  · funext i
    by_cases hid : i = d
    · subst hid
      simp [shift, h]
    · by_cases hie : i = e
      · subst hie
        simp [shift, hid]
      · simp [shift, hid, hie]

/-- Plaquette Wilson loop at site `x` in the coordinate plane `(mu, nu)`. -/
def plaquette {N L : ℕ} (U : DiscreteGaugeField N L) (x : Site L)
    (mu nu : Dir) : LinkGroup N :=
  U x mu * U (shift mu x) nu * (U (shift nu x) mu)⁻¹ * (U x nu)⁻¹

/-- Gauge transformation of a lattice gauge field. -/
def gaugeTransform {N L : ℕ} (g : Site L → LinkGroup N)
    (U : DiscreteGaugeField N L) : DiscreteGaugeField N L :=
  fun x mu => g x * U x mu * (g (shift mu x))⁻¹

/-- The plaquette is gauge-covariant: it transforms by conjugation at `x`. -/
theorem plaquette_gaugeTransform {N L : ℕ} (g : Site L → LinkGroup N)
    (U : DiscreteGaugeField N L) (x : Site L) (mu nu : Dir) :
    plaquette (gaugeTransform g U) x mu nu =
      g x * plaquette U x mu nu * (g x)⁻¹ := by
  unfold plaquette gaugeTransform
  rw [shift_comm mu nu x]
  group

/-- The trace of a conjugate matrix equals the original trace. -/
theorem trace_conj {N : ℕ} (g : LinkGroup N) (W : Matrix (Fin N) (Fin N) ℂ) :
    Matrix.trace ((g : Matrix (Fin N) (Fin N) ℂ) * W *
      ((g⁻¹ : LinkGroup N) : Matrix (Fin N) (Fin N) ℂ)) = Matrix.trace W := by
  rw [Matrix.trace_mul_cycle]
  simp

/-- Wilson action with normalization by the matrix size `N`. -/
noncomputable def wilsonAction {N L : ℕ} [NeZero N] [NeZero L] (beta : ℝ)
    (U : DiscreteGaugeField N L) : ℝ :=
  beta * ∑ x : Site L, ∑ mu : Dir, ∑ nu : Dir,
    (1 - (Matrix.trace ((plaquette U x mu nu : LinkGroup N) :
      Matrix (Fin N) (Fin N) ℂ)).re / (N : ℝ))

/-- The plaquette-trace sum is invariant under a gauge transformation. -/
theorem sum_plaquette_trace_gaugeTransform {N L : ℕ} [NeZero N] [NeZero L]
    (U : DiscreteGaugeField N L) (g : Site L → LinkGroup N) :
    (∑ x : Site L, ∑ mu : Dir, ∑ nu : Dir,
      (1 - (Matrix.trace ((plaquette (gaugeTransform g U) x mu nu : LinkGroup N) :
        Matrix (Fin N) (Fin N) ℂ)).re / (N : ℝ))) =
    (∑ x : Site L, ∑ mu : Dir, ∑ nu : Dir,
      (1 - (Matrix.trace ((plaquette U x mu nu : LinkGroup N) :
        Matrix (Fin N) (Fin N) ℂ)).re / (N : ℝ))) := by
  apply Finset.sum_congr rfl
  intro x _
  apply Finset.sum_congr rfl
  intro mu _
  apply Finset.sum_congr rfl
  intro nu _
  rw [plaquette_gaugeTransform]
  simp only [Matrix.GeneralLinearGroup.coe_mul]
  rw [trace_conj]

/-- The Wilson action is invariant under gauge transformations. -/
theorem wilsonAction_gaugeInvariant {N L : ℕ} [NeZero N] [NeZero L] (beta : ℝ)
    (U : DiscreteGaugeField N L) (g : Site L → LinkGroup N) :
    wilsonAction beta (gaugeTransform g U) = wilsonAction beta U := by
  unfold wilsonAction
  rw [sum_plaquette_trace_gaugeTransform]

/-- Trivial gauge field: every link is the identity. -/
def trivialConnection {N L : ℕ} : DiscreteGaugeField N L := fun _ _ => 1

/-- The trivial connection has identity plaquettes. -/
theorem plaquette_trivial {N L : ℕ} (x : Site L) (mu nu : Dir) :
    plaquette (trivialConnection : DiscreteGaugeField N L) x mu nu = 1 := by
  simp [plaquette, trivialConnection]

/-- The Wilson action of the trivial connection is zero. -/
theorem wilsonAction_trivial {N L : ℕ} [NeZero N] [NeZero L] (beta : ℝ) :
    wilsonAction beta (trivialConnection : DiscreteGaugeField N L) = 0 := by
  unfold wilsonAction
  simp [plaquette_trivial, Matrix.trace_one]

/-- A determinant-one unitary GL(2, C) link: the diagonal SU(2) element `diag(i, -i)`. -/
noncomputable def su2Link : LinkGroup 2 :=
  Matrix.GeneralLinearGroup.mkOfDetNeZero
    (!![Complex.I, 0; 0, -Complex.I] : Matrix (Fin 2) (Fin 2) ℂ)
    (by simp [Matrix.det_fin_two])

/-- A connection on the 2x2x2x2 torus with one non-identity link at the origin. -/
noncomputable def su2Connection : DiscreteGaugeField 2 2 :=
  fun x mu => if x = 0 ∧ mu = 0 then su2Link else 1

/-- The origin plaquette of the witness connection is exactly `su2Link`. -/
theorem plaquette_su2Connection :
    plaquette su2Connection 0 0 1 = su2Link := by
  simp [plaquette, su2Connection, shift]

/-- The witness link is not the identity matrix. -/
theorem su2Link_matrix_ne_one :
    (su2Link : Matrix (Fin 2) (Fin 2) ℂ) ≠ 1 := by
  intro h
  have h00 := congrFun (congrFun h 0) 0
  simp [su2Link] at h00
  have him := congrArg Complex.im h00
  simp at him

/-- The witness link has determinant one. -/
theorem su2Link_det_one :
    Matrix.det (su2Link : Matrix (Fin 2) (Fin 2) ℂ) = 1 := by
  simp [su2Link, Matrix.det_fin_two]

/-- The witness link is unitary (both star-multiplication sides). -/
theorem su2Link_unitary :
    (su2Link : Matrix (Fin 2) (Fin 2) ℂ) *
        star (su2Link : Matrix (Fin 2) (Fin 2) ℂ) = 1 ∧
      star (su2Link : Matrix (Fin 2) (Fin 2) ℂ) *
        (su2Link : Matrix (Fin 2) (Fin 2) ℂ) = 1 := by
  constructor <;>
    ext i j <;> fin_cases i <;> fin_cases j <;>
    simp [su2Link, Matrix.mul_apply, Matrix.star_apply, Complex.conj_I]

/-- The witness link is traceless. -/
theorem su2Link_trace_zero :
    Matrix.trace (su2Link : Matrix (Fin 2) (Fin 2) ℂ) = 0 := by
  simp [su2Link, Matrix.trace_fin_two]

/-- The Wilson-action summand at the origin is 1 for the witness. -/
theorem wilsonAction_summand_su2Connection :
    1 - (Matrix.trace ((plaquette su2Connection 0 0 1 : LinkGroup 2) :
      Matrix (Fin 2) (Fin 2) ℂ)).re / (2 : ℝ) = 1 := by
  rw [plaquette_su2Connection, su2Link_trace_zero]
  norm_num

/-- The witness plaquette is not the identity, so the lattice model is non-vacuous. -/
theorem plaquette_su2Connection_ne_one :
    plaquette su2Connection 0 0 1 ≠ 1 := by
  intro h
  rw [plaquette_su2Connection] at h
  apply su2Link_matrix_ne_one
  simpa using congrArg (fun u : LinkGroup 2 => (u : Matrix (Fin 2) (Fin 2) ℂ)) h

end Math30.Topology.DiscreteYangMills
