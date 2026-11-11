-- ShannonEntropyDPI.lean
-- Math 3.0 / Phase 45: Finite data-processing non-expansion
-- Bounded regression armor: a surjective deterministic channel cannot increase the
-- number of distinguishable states. This is the finite-set core of the data-processing
-- inequality; it is not a formalization of full Shannon entropy.

import Mathlib.Data.Fintype.Card
import Mathlib.Tactic

namespace Math30.InformationTheory

/-- A surjective deterministic channel cannot increase the number of distinguishable states. -/
theorem dpi_card_nonexpansive {α β : Type*} [Fintype α] [Fintype β]
    (f : α → β) (hf : Function.Surjective f) :
    Fintype.card β ≤ Fintype.card α :=
  Fintype.card_le_of_surjective f hf

/-- Two-stage processing is still non-expansive. -/
theorem dpi_composition {α β γ : Type*} [Fintype α] [Fintype β] [Fintype γ]
    (f : α → β) (g : β → γ)
    (hf : Function.Surjective f) (hg : Function.Surjective g) :
    Fintype.card γ ≤ Fintype.card α :=
  le_trans (Fintype.card_le_of_surjective g hg)
           (Fintype.card_le_of_surjective f hf)

end Math30.InformationTheory
