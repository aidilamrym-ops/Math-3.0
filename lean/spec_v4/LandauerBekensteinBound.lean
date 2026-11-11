-- LandauerBekensteinBound.lean
-- Math 3.0 / Phase 46: Discrete thermodynamic information ledger
-- Bounded regression armor: energy accounting and finite capacity bounds.
-- These are accounting invariants, not a derivation of physical constants.

import Mathlib.Data.Int.Basic
import Mathlib.Tactic

namespace Math30.Thermo.Information

/-- Landauer ledger: with positive per-bit cost, the bit count never exceeds the
accounted energy. -/
theorem landauer_bits_le_energy (bits cost : ℕ) (hcost : 1 ≤ cost) :
    bits ≤ bits * cost := by
  nlinarith

/-- Finite capacity is bounded by the radius budget. -/
theorem bekenstein_capacity_le_radius (radius energy : ℕ) :
    min radius energy ≤ radius :=
  Nat.min_le_left _ _

/-- Finite capacity is bounded by the energy budget. -/
theorem bekenstein_capacity_le_energy (radius energy : ℕ) :
    min radius energy ≤ energy :=
  Nat.min_le_right _ _

end Math30.Thermo.Information
