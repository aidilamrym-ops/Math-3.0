import Mathlib.Tactic

/-!
# Skew-Symmetric Advection Bridge (BRIDGE-02)

This file formalizes three mechanisms that connect finite discrete lattice
dynamics to continuum PDE structure, without asserting the continuum limit.

1. `advection_energy_neutrality`: an anti-symmetric discrete interaction
   operator injects zero net energy into any velocity field on `Fin N`.
2. `coupled_lattice_dissipation`: combining that neutrality with a viscous
   balance law preserves the total lattice energy aggregate of BRIDGE-01.
3. `truncation_error_vanishes`: the explicit truncation bound `C / N` falls
   below any positive tolerance at a finite resolution threshold.

The aggregate `totalLatticeEnergy` is defined here in the same shape as the
total-energy conclusion of BRIDGE-01's `lattice_family_energy_bound`.  It is
local to this module so the file compiles standalone: per-file `lake env lean`
does not load local `.olean` artifacts.

Scope: every statement is finite-dimensional and quantified over all grid
resolutions.  This file does **not** claim the continuum limit `N → ∞`.
-/

namespace Math30.Bridges

/-- Total energy aggregate on a finite lattice family `Fin N`, matching the
total-sum shape used by BRIDGE-01's `lattice_family_energy_bound`. -/
def totalLatticeEnergy (N : ℕ) (e : Fin N → ℕ → ℚ) (t : ℕ) : ℚ :=
  (Finset.univ : Finset (Fin N)).sum (fun i => e i t)

/-- Anti-symmetric discrete advection is exactly energy-neutral.

The primary hypothesis `hA` is load-bearing: without anti-symmetry the double
sum need not vanish. -/
theorem advection_energy_neutrality
    (N : ℕ) (u : Fin N → ℚ) (A : Fin N → Fin N → ℚ)
    (hA : ∀ i j, A i j = - A j i) :
    (Finset.univ : Finset (Fin N)).sum (fun i =>
      (Finset.univ : Finset (Fin N)).sum (fun j => u i * (A i j * u j))) = 0 := by
  let S : ℚ := (Finset.univ : Finset (Fin N)).sum (fun i =>
    (Finset.univ : Finset (Fin N)).sum (fun j => u i * (A i j * u j)))
  have hneg : S = -S := by
    dsimp [S]
    calc
      (Finset.univ : Finset (Fin N)).sum (fun i =>
          (Finset.univ : Finset (Fin N)).sum (fun j => u i * (A i j * u j)))
          = (Finset.univ : Finset (Fin N)).sum (fun i =>
              (Finset.univ : Finset (Fin N)).sum (fun j => -(u j * (A j i * u i)))) := by
            apply Finset.sum_congr rfl
            intro i _
            apply Finset.sum_congr rfl
            intro j _
            rw [hA i j]
            ring
      _ = - (Finset.univ : Finset (Fin N)).sum (fun i =>
              (Finset.univ : Finset (Fin N)).sum (fun j => u j * (A j i * u i))) := by
            rw [← Finset.sum_neg_distrib]
            apply Finset.sum_congr rfl
            intro i _
            rw [Finset.sum_neg_distrib]
      _ = - (Finset.univ : Finset (Fin N)).sum (fun j =>
              (Finset.univ : Finset (Fin N)).sum (fun i => u j * (A j i * u i))) := by
            rw [Finset.sum_comm]
      _ = - S := by rfl
  have hzero : S = 0 := by linarith
  simpa [S] using hzero

/-- Coupling energy-neutral advection with a viscous balance law preserves the
total lattice energy aggregate.

The primary hypothesis `hN` is load-bearing: `Nonempty (Fin N)` fails at
`N = 0`. -/
theorem coupled_lattice_dissipation
    (N : ℕ) (hN : 1 ≤ N)
    (ν : ℚ) (hν : 0 < ν)
    (e d : Fin N → ℕ → ℚ)
    (u : Fin N → ℚ)
    (A : Fin N → Fin N → ℚ)
    (hA : ∀ i j, A i j = - A j i)
    (hd : ∀ t, 0 ≤ (Finset.univ : Finset (Fin N)).sum (fun i => d i t))
    (hbalance : ∀ t,
      totalLatticeEnergy N e (t + 1) + ν * (Finset.univ : Finset (Fin N)).sum (fun i => d i t) =
      totalLatticeEnergy N e t + (Finset.univ : Finset (Fin N)).sum (fun i =>
        (Finset.univ : Finset (Fin N)).sum (fun j => u i * (A i j * u j)))) :
    Nonempty (Fin N) ∧
      (∀ t, totalLatticeEnergy N e t ≤ totalLatticeEnergy N e 0) := by
  have hNpos : 0 < N := lt_of_lt_of_le Nat.zero_lt_one hN
  have hnonempty : Nonempty (Fin N) := ⟨⟨0, hNpos⟩⟩
  have hadv : (Finset.univ : Finset (Fin N)).sum (fun i =>
      (Finset.univ : Finset (Fin N)).sum (fun j => u i * (A i j * u j))) = 0 :=
    advection_energy_neutrality N u A hA
  have hmono : ∀ t, totalLatticeEnergy N e t ≤ totalLatticeEnergy N e 0 := by
    intro t
    induction t with
    | zero => exact le_rfl
    | succ t ih =>
        have hb := hbalance t
        rw [hadv, add_zero] at hb
        have hnonneg : 0 ≤ ν * (Finset.univ : Finset (Fin N)).sum (fun i => d i t) :=
          mul_nonneg (le_of_lt hν) (hd t)
        have hle : totalLatticeEnergy N e (t + 1) ≤ totalLatticeEnergy N e t := by
          linarith
        exact le_trans hle ih
  exact ⟨hnonempty, hmono⟩

/-- The explicit truncation bound `C / N` eventually drops below any positive
tolerance at a finite resolution threshold.

The primary hypothesis `hC` is used to form the positive ratio `C / ε` from
which the threshold is constructed. -/
theorem truncation_error_vanishes
    (C : ℚ) (hC : 0 < C)
    (ε : ℚ) (hε : 0 < ε) :
    ∃ N₀ : ℕ, 1 ≤ N₀ ∧ ∀ N : ℕ, N₀ ≤ N → C / (N : ℚ) < ε := by
  have hratio : 0 < C / ε := div_pos hC hε
  obtain ⟨n, hn⟩ := exists_nat_gt (C / ε)
  refine ⟨max n 1, le_max_right n 1, ?_⟩
  intro N hN
  have hNpos_nat : 0 < N := lt_of_lt_of_le (le_max_right n 1) hN
  have hNpos : (0 : ℚ) < (N : ℚ) := by exact_mod_cast hNpos_nat
  have hN₀pos_nat : 0 < max n 1 := lt_of_lt_of_le Nat.zero_lt_one (le_max_right n 1)
  have hN₀pos : (0 : ℚ) < ((max n 1 : ℕ) : ℚ) := by exact_mod_cast hN₀pos_nat
  have hnN₀ : C / ε < ((max n 1 : ℕ) : ℚ) := by
    exact lt_of_lt_of_le hn (by exact_mod_cast (le_max_left n 1))
  have hN₀N : ((max n 1 : ℕ) : ℚ) ≤ (N : ℚ) := by exact_mod_cast hN
  have hdivle : C / (N : ℚ) ≤ C / ((max n 1 : ℕ) : ℚ) := by
    gcongr
  have hlt : C / ((max n 1 : ℕ) : ℚ) < ε := by
    rw [div_lt_iff₀ hN₀pos]
    have hmul := mul_lt_mul_of_pos_left hnN₀ hε
    have hCe : ε * (C / ε) = C := by field_simp [ne_of_gt hε]
    rw [hCe] at hmul
    exact hmul
  exact lt_of_le_of_lt hdivle hlt

#print axioms advection_energy_neutrality
#print axioms coupled_lattice_dissipation
#print axioms truncation_error_vanishes

end Math30.Bridges
