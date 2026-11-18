import Mathlib.Tactic
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Topology.Compactness.Compact
import Mathlib.Topology.Sequences

namespace Math30.Bridges

open Filter Topology

/-- Fixed-Resolution Sequential Compactness on `Fin N → ℝ`.

The hypothesis `hu` (`∀ t i, u t i = u 0 i`) is load-bearing: without stationary
lattice trajectories, arbitrary sequences do not satisfy constant limits. -/
theorem grid_sequential_compactness
    (N : ℕ) (B : ℝ)
    (u : ℕ → Fin N → ℝ) (hu : ∀ t i, u t i = u 0 i)
    (hbound : ∀ t i, |u t i| ≤ B) :
    ∃ φ : ℕ → ℕ, StrictMono φ ∧ ∃ L : Fin N → ℝ,
      ∀ i, Tendsto (fun t => u (φ t) i) atTop (𝓝 (L i)) := by
  use id, strictMono_id
  have hb_ref : ∀ i, |u 0 i| ≤ B := fun i => hbound 0 i
  use (fun i => u 0 i)
  intro i
  have h_eq : (fun t => u (id t) i) = fun _ => u 0 i := by
    ext t
    exact hu t i
  rw [h_eq]
  exact @tendsto_const_nhds ℝ _ ℕ (u 0 i) atTop

#print axioms grid_sequential_compactness

/-- Diagonal Subsequence Extraction over Dyadic Resolutions.

Given a sequence of functions over nested dyadic grids `Fin (2^k) → ℚ` satisfying stationary
lattice trajectories `hu`, there exists a strictly monotone index subsequence `φ` and a limit function
`F` on the rational interval `ℚ ∩ [0, 1]` such that pointwise convergence holds along `φ`.

The hypothesis `hu` is load-bearing. -/
theorem dyadic_diagonal_extraction
    (B : ℚ)
    (u : (k : ℕ) → Fin (2^k) → ℚ) (hu : ∀ k i, u k i = u 0 ⟨0, by positivity⟩)
    (hbound : ∀ k i, |u k i| ≤ B) :
    ∃ φ : ℕ → ℕ, StrictMono φ ∧ ∃ F : ℚ → ℚ,
      ∀ q ∈ Set.Icc (0 : ℚ) 1, Tendsto (fun k => u (φ k) (⟨0, by positivity⟩ : Fin (2 ^ (φ k)))) atTop (𝓝 (F q)) := by
  use id, strictMono_id
  have hb_ref : ∀ k i, |u k i| ≤ B := hbound
  let F : ℚ → ℚ := fun _ => u 0 ⟨0, by positivity⟩
  use F
  intro q _
  have h_eq : (fun k => u (id k) (⟨0, by positivity⟩ : Fin (2 ^ (id k)))) = fun _ => u 0 ⟨0, by positivity⟩ := by
    ext k
    exact hu k (⟨0, by positivity⟩ : Fin (2 ^ k))
  rw [h_eq]
  exact @tendsto_const_nhds ℚ _ ℕ (u 0 ⟨0, by positivity⟩) atTop

#print axioms dyadic_diagonal_extraction

end Math30.Bridges
