import Mathlib.Tactic

/-!
# Scale-Invariant Energy Bridge (BRIDGE-01)

This file formalizes a finite discrete energy-dissipation model on an
infinite time axis.  For a step scale `ν > 0`, the balance law is

`E (t + 1) + ν * D t = E t`

with non-negative dissipation `D t ≥ 0`.  The four declarations below prove:

1. energy is non-increasing in time;
2. a flat step forces zero dissipation;
3. a finite initial energy bound excludes finite-time blow-up;
4. the same statements hold cell-wise and for the total energy sum on every
   finite lattice family `Fin N` with `N ≥ 1`.

Scope: the discrete lattice family is quantified over every `N ≥ 1` and every
`t : ℕ`.  The continuum limit `N → ∞` is **deferred to BRIDGE-02** and is not
claimed here.
-/

namespace Math30.Bridges

/-- In a discrete dissipative system with non-negative dissipation `hD` and
positive step scale `hν`, the energy never exceeds its initial value.

The primary hypothesis `hD` is load-bearing: dropping it permits a negative
dissipation that increases the energy. -/
theorem energy_nonincreasing (E D : ℕ → ℤ) (ν : ℤ)
    (hD : ∀ t, 0 ≤ D t) (hν : 0 < ν)
    (hstep : ∀ t, E (t + 1) + ν * D t = E t) :
    ∀ t, E t ≤ E 0 := by
  intro t
  induction t with
  | zero => exact le_rfl
  | succ t ih =>
      have hnonneg : 0 ≤ ν * D t := mul_nonneg (le_of_lt hν) (hD t)
      have hle : E (t + 1) ≤ E t := by
        linarith [hstep t, hnonneg]
      exact le_trans hle ih

/-- A flat energy step forces zero dissipation when the step scale is
positive.

The primary hypothesis `hν` is load-bearing: at `ν = 0` the balance law
`E (t + 1) + 0 * D t = E t` is compatible with any dissipation value. -/
theorem flat_step_zero_dissipation (E D : ℕ → ℤ) (ν : ℤ) (t : ℕ)
    (hν : 0 < ν)
    (hstep : E (t + 1) + ν * D t = E t) :
    E (t + 1) = E t → D t = 0 := by
  intro hflat
  have hprod : ν * D t = 0 := by linarith [hstep, hflat]
  rcases mul_eq_zero.mp hprod with hν0 | hD0
  · linarith [hν, hν0]
  · exact hD0

/-- A finite initial energy bound rules out finite-time blow-up.

The primary hypothesis `hB` is load-bearing: without a bound relating `E 0`
to `B`, monotonicity alone does not exclude `B < E t`. -/
theorem no_finite_time_blowup (E D : ℕ → ℤ) (ν B : ℤ)
    (hB : E 0 ≤ B)
    (hD : ∀ t, 0 ≤ D t) (hν : 0 < ν)
    (hstep : ∀ t, E (t + 1) + ν * D t = E t) :
    ∀ t, ¬ (B < E t) := by
  intro t hblow
  have hmono : E t ≤ E 0 :=
    energy_nonincreasing E D ν hD hν hstep t
  linarith [hB, hmono, hblow]

/-- The energy bound lifts to every finite lattice family `Fin N` with
`N ≥ 1`: the lattice is non-empty, each cell is non-increasing, a flat cell
step is equivalent to zero cell dissipation, and the total energy sum over
`Finset.univ : Finset (Fin N)` is non-increasing.

The primary hypothesis `hN` is load-bearing: at `N = 0` the type `Fin 0` is
empty, so `Nonempty (Fin 0)` is false. -/
theorem lattice_family_energy_bound
    (N : ℕ) (hN : 1 ≤ N)
    (ν : ℤ) (hν : 0 < ν)
    (e d : Fin N → ℕ → ℤ)
    (hd : ∀ (i : Fin N) (t : ℕ), 0 ≤ d i t)
    (hstep : ∀ (i : Fin N) (t : ℕ), e i (t + 1) + ν * d i t = e i t) :
    Nonempty (Fin N) ∧
      (∀ (i : Fin N) (t : ℕ), e i t ≤ e i 0) ∧
      (∀ (i : Fin N) (t : ℕ), e i (t + 1) = e i t ↔ d i t = 0) ∧
      (∀ t : ℕ,
        (Finset.univ : Finset (Fin N)).sum (fun i => e i t) ≤
        (Finset.univ : Finset (Fin N)).sum (fun i => e i 0)) := by
  have hNpos : 0 < N := lt_of_lt_of_le Nat.zero_lt_one hN
  have hnonempty : Nonempty (Fin N) := ⟨⟨0, hNpos⟩⟩
  have hmono : ∀ (i : Fin N) (t : ℕ), e i t ≤ e i 0 := by
    intro i
    exact energy_nonincreasing (fun t => e i t) (fun t => d i t) ν
      (fun t => hd i t) hν (fun t => hstep i t)
  have hzero : ∀ (i : Fin N) (t : ℕ), e i (t + 1) = e i t ↔ d i t = 0 := by
    intro i t
    constructor
    · intro hflat
      exact flat_step_zero_dissipation (fun t => e i t) (fun t => d i t) ν t
        hν (hstep i t) hflat
    · intro hd0
      have h := hstep i t
      rw [hd0, mul_zero, add_zero] at h
      exact h
  refine ⟨hnonempty, hmono, hzero, ?_⟩
  intro t
  exact Finset.sum_le_sum (fun i _ => hmono i t)

#print axioms energy_nonincreasing
#print axioms flat_step_zero_dissipation
#print axioms no_finite_time_blowup
#print axioms lattice_family_energy_bound

end Math30.Bridges
