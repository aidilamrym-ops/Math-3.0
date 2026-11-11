-- ErdosSzekeresRamsey.lean
-- Math 3.0 / Phase 49: Finite pigeonhole and length-2 Erdos-Szekeres instance
-- Bounded regression armor: the finite pigeonhole principle and the smallest
-- (k = l = 2) Erdos-Szekeres case. These are honest finite instances, not the full
-- Erdos-Szekeres or Ramsey theorems.

import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Tactic

namespace Math30.Combinatorics.Finite

/-- Finite pigeonhole principle: more pigeons than holes forces a collision. -/
theorem pigeonhole_finite {α β : Type*} [Fintype α] [Fintype β]
    (f : α → β) (h : Fintype.card β < Fintype.card α) :
    ∃ x y, x ≠ y ∧ f x = f y :=
  Fintype.exists_ne_map_eq_of_card_lt f h

/-- Erdos-Szekeres smallest case: any two distinct naturals are comparable, hence
admit a monotone subsequence of length two. -/
theorem erdos_szekeres_pair (a b : ℕ) (hne : a ≠ b) :
    a < b ∨ b < a := by
  omega

/-- A two-coloring of a single edge always has a monochromatic representative. -/
theorem ramsey_one_edge (c : Fin 1 → Fin 2) :
    ∃ e : Fin 1, c e = 0 ∨ c e = 1 := by
  refine ⟨0, ?_⟩
  have hval : (c 0).val = 0 ∨ (c 0).val = 1 := by
    have hlt : (c 0).val < 2 := (c 0).isLt
    omega
  rcases hval with h0 | h1
  · left
    exact Fin.eq_of_val_eq (by simpa using h0)
  · right
    exact Fin.eq_of_val_eq (by simpa using h1)

end Math30.Combinatorics.Finite
