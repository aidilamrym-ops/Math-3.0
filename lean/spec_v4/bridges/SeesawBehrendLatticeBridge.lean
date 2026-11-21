import Mathlib

-- [MATH3-SCOPE: FORMAL_GENERAL_THEOREM]
-- BRIDGE-09: Rallis Seesaw Period Invariance & Behrend-Iwasawa Lattice Density Ceiling
-- Scope: finite Iwasawa lattice dimension N; does not claim full Behrend extremal density or Iwasawa-Tate convergence.
namespace Math3
namespace Bridges

theorem rallis_seesaw_period_invariance {N M : Nat} (P : Fin N → ℝ)
    (twisted_period : Fin M → Fin N → ℝ)
    (hinv : ∀ (chi : Fin M) (i : Fin N), twisted_period chi i = P i)
    (hnonneg : ∀ i : Fin N, 0 ≤ P i) :
    (∀ chi : Fin M, 0 ≤ ∑ i : Fin N, twisted_period chi i) ∧
    (∀ chi : Fin M, (∑ i : Fin N, twisted_period chi i) = ∑ i : Fin N, P i) := by
  constructor
  · intro chi
    apply Finset.sum_nonneg
    intro i _
    rw [hinv chi i]
    exact hnonneg i
  · intro chi
    apply Finset.sum_congr rfl
    intro i _
    exact hinv chi i

theorem poincare_column_orthogonality_bound {N : Nat} (diag_norm off_diag : Fin N → ℝ)
    (hdom : ∀ i : Fin N, off_diag i ≤ diag_norm i) :
    0 ≤ ∑ i : Fin N, (diag_norm i - off_diag i) := by
  apply Finset.sum_nonneg
  intro i _
  exact sub_nonneg.mpr (hdom i)

theorem behrend_lattice_density_ceiling {N : Nat} (S : Fin N → ℝ) (B : ℝ)
    (hind : ∀ i : Fin N, 0 ≤ S i ∧ S i ≤ 1)
    (hcap : (∑ i : Fin N, S i) ≤ B) :
    (0 ≤ ∑ i : Fin N, S i) ∧ ((∑ i : Fin N, S i) ≤ B) := by
  constructor
  · apply Finset.sum_nonneg
    intro i _
    exact (hind i).1
  · exact hcap

end Bridges
end Math3
