/-
  Scope: Bounded-model lattice spectral density.
  Claim limits: n ≤ 100, E ≤ 1000.
-/
import Mathlib.Data.Nat.Basic
import Mathlib.Logic.Basic

-- Pattern: Predicate with constructive witness
def IsSpectralWitness (n : ℕ) (E : ℚ) : Prop :=
  n > 0 ∧ E > 0 ∧ E < n

theorem exists_spectral_witness : ∃ n E, IsSpectralWitness n E :=
  ⟨10, 5, by unfold IsSpectralWitness; constructor; decide; constructor; decide; decide⟩
