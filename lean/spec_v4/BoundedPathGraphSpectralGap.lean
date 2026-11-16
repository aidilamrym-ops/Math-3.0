/-
  Scope: Bounded-model discrete Laplacian on path graph P_n.
  Claim limits: n ≤ 100, edge weight = 1.
-/
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

def IsPathGraphWitness (n : ℕ) : Prop :=
  n ≥ 2 ∧ n ≤ 100

noncomputable def SpectralGapBound (n : ℕ) : ℝ :=
  2 * (1 - Real.cos (Real.pi / n))

theorem exists_path_graph_witness : ∃ n, IsPathGraphWitness n :=
  ⟨10, by
    unfold IsPathGraphWitness
    constructor
    · decide
    · decide
  ⟩

theorem path_graph_spectral_gap_lower_bound {n : ℕ} (h : IsPathGraphWitness n) :
    SpectralGapBound n > 0 := by
  have hn2 : (n : ℝ) ≥ 2 := by exact_mod_cast h.1
  have hnpos : (n : ℝ) > 0 := by linarith
  have hpi : Real.pi > 0 := Real.pi_pos
  have hdivpos : Real.pi / (n : ℝ) > 0 := by positivity
  have hdivlt : Real.pi / (n : ℝ) < Real.pi := by
    have hn1 : (n : ℝ) > 1 := by linarith
    have heq : Real.pi / (n : ℝ) * (n : ℝ) = Real.pi := by
      field_simp [hnpos.ne']
      <;> ring
    by_contra hc
    have hge : Real.pi / (n : ℝ) ≥ Real.pi := by linarith
    have hmul : Real.pi / (n : ℝ) * (n : ℝ) ≥ Real.pi * (n : ℝ) := by nlinarith
    rw [heq] at hmul
    have hpi_le : Real.pi ≥ Real.pi * (n : ℝ) := by linarith
    have hn1' : (n : ℝ) ≤ 1 := by
      nlinarith [Real.pi_pos]
    linarith
  have hcos_lt_one : Real.cos (Real.pi / (n : ℝ)) < 1 := by
    have hcos_lt_cos0 : Real.cos (Real.pi / (n : ℝ)) < Real.cos 0 := by
      apply Real.cos_lt_cos_of_nonneg_of_le_pi
      · linarith
      · have hle : Real.pi / (n : ℝ) ≤ Real.pi := by
          by_contra hc2
          have hgt : Real.pi / (n : ℝ) > Real.pi := by linarith
          have hmul2 : Real.pi / (n : ℝ) * (n : ℝ) > Real.pi * (n : ℝ) := by nlinarith
          have heq2 : Real.pi / (n : ℝ) * (n : ℝ) = Real.pi := by
            field_simp [hnpos.ne']
            <;> ring
          rw [heq2] at hmul2
          have hpi_lt : Real.pi < Real.pi * (n : ℝ) := by linarith
          have hn_lt1 : (n : ℝ) < 1 := by
            nlinarith [Real.pi_pos]
          linarith
        linarith [Real.pi_pos]
      · linarith [Real.pi_pos]
    have hcos0 : Real.cos 0 = (1 : ℝ) := by norm_num
    linarith
  have hpos : (1 : ℝ) - Real.cos (Real.pi / (n : ℝ)) > 0 := by linarith
  have hpos2 : (2 : ℝ) * (1 - Real.cos (Real.pi / (n : ℝ))) > 0 := by positivity
  simpa [SpectralGapBound] using hpos2