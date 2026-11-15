-- DiscreteHodgeDecomposition.lean
-- Math 3.0 / Fase 57 (rebuilt in Batch 10): Discrete Hodge Theory on the 3-Cycle
--
-- Scope:
--   * the cyclic lattice with sites `Fin n`, the forward difference
--       (d a)_i = a_{i+1} - a_i,
--     and its formal adjoint `delta = d^T`;
--   * the Hodge Laplacians `Delta_0 = delta d` and `Delta_1 = d delta`,
--     their symmetry, and the intertwining identities
--       d Delta_0 = Delta_1 d,   delta Delta_1 = Delta_0 delta;
--   * the Green identity `<d u, v> = <u, delta v>`;
--   * the explicit 3x3 Laplacian, its vanishing determinant, and the
--     characterisation of harmonic 0- and 1-cochains as the constant vectors;
--   * exactness on the 3-cycle: a cochain is in the image of `d` exactly when
--     its total sum is zero;
--   * the nonzero harmonic class: the constant cochain `1` is harmonic but not
--     exact, so the first cohomology of the 3-cycle is nontrivial;
--   * the orthogonal Hodge decomposition over the rationals:
--       v = d a + mean(v),   <d a, mean(v)> = 0,
--     where `mean(v)` is the constant cochain with value `(v_0+v_1+v_2)/3`.
--
-- Claim limits:
--   * finite cyclic lattice only; this is not the Hodge decomposition of a
--     Riemannian manifold or of a continuous de Rham complex;
--   * the integral statements are kernel and exactness computations; the
--     orthogonal direct-sum decomposition is stated over `Q`, because the
--     harmonic projection needs division by 3;
--   * no general elliptic theory and no global Hodge theorem.

import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Data.Int.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic

open Finset Matrix
open scoped BigOperators Matrix

namespace Math30.Topology.DiscreteHodge

variable {n : ℕ} [NeZero n]

/-- Forward difference on the cyclic lattice. -/
def discreteGrad (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- Formal adjoint of the forward difference: the transpose matrix. -/
def discreteDiv (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n)ᵀ

/-- Laplacian on 0-cochains: `Delta_0 = delta d`. -/
def laplacian0 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteDiv n) * (discreteGrad n)

/-- Laplacian on 1-cochains: `Delta_1 = d delta`. -/
def laplacian1 (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℤ :=
  (discreteGrad n) * (discreteDiv n)

/-- A cochain is harmonic when it lies in the kernel of the Laplacian. -/
def IsHarmonic (L : Matrix (Fin n) (Fin n) ℤ) (v : Fin n → ℤ) : Prop :=
  L *ᵥ v = 0

/-- `Delta_0` is symmetric. -/
theorem laplacian0_symmetric (n : ℕ) [NeZero n] :
    (laplacian0 n)ᵀ = laplacian0 n := by
  dsimp [laplacian0, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- `Delta_1` is symmetric. -/
theorem laplacian1_symmetric (n : ℕ) [NeZero n] :
    (laplacian1 n)ᵀ = laplacian1 n := by
  dsimp [laplacian1, discreteDiv]
  rw [transpose_mul, transpose_transpose]

/-- The gradient intertwines the two Laplacians: `d Delta_0 = Delta_1 d`. -/
theorem hodge_intertwine_d (n : ℕ) [NeZero n] :
    (discreteGrad n) * (laplacian0 n) = (laplacian1 n) * (discreteGrad n) := by
  dsimp [laplacian0, laplacian1]
  rw [← Matrix.mul_assoc]

/-- The divergence intertwines the two Laplacians: `delta Delta_1 = Delta_0 delta`. -/
theorem hodge_intertwine_dstar (n : ℕ) [NeZero n] :
    (discreteDiv n) * (laplacian1 n) = (laplacian0 n) * (discreteDiv n) := by
  dsimp [laplacian0, laplacian1]
  rw [← Matrix.mul_assoc]

/-- Green identity: `delta = d^T` is the formal adjoint of `d`. -/
theorem green_identity (n : ℕ) [NeZero n] (u v : Fin n → ℤ) :
    dotProduct (discreteGrad n *ᵥ u) v =
      dotProduct u (discreteDiv n *ᵥ v) := by
  rw [dotProduct_comm (discreteGrad n *ᵥ u) v]
  rw [← Matrix.dotProduct_transpose_mulVec]
  rfl

/-- The 3x3 matrix of `Delta_0` on the 3-cycle. -/
theorem laplacian0_3_eq :
    laplacian0 3 = !![2, -1, -1; -1, 2, -1; -1, -1, 2] := by
  ext i j
  fin_cases i <;> fin_cases j <;> decide

/-- The 3x3 matrix of `Delta_1` on the 3-cycle. -/
theorem laplacian1_3_eq :
    laplacian1 3 = !![2, -1, -1; -1, 2, -1; -1, -1, 2] := by
  ext i j
  fin_cases i <;> fin_cases j <;> decide

/-- The 3x3 `Delta_0` is singular. -/
theorem laplacian0_3_det : (laplacian0 3).det = 0 := by
  rw [laplacian0_3_eq]
  decide

/-- The 3x3 `Delta_1` is singular. -/
theorem laplacian1_3_det : (laplacian1 3).det = 0 := by
  rw [laplacian1_3_eq]
  decide

/-- A constant 0-cochain is harmonic on the 3-cycle. -/
theorem constant_is_harmonic_0_3 (c : ℤ) :
    IsHarmonic (laplacian0 3) (fun _ => c) := by
  ext i
  dsimp [IsHarmonic, laplacian0, mulVec, dotProduct]
  rw [← sum_mul]
  have h2 : ∑ j : Fin 3, (discreteDiv 3 * discreteGrad 3) i j = 0 := by
    fin_cases i <;> decide
  rw [h2, zero_mul]

/-- A constant 1-cochain is harmonic on the 3-cycle. -/
theorem constant_is_harmonic_1_3 (c : ℤ) :
    IsHarmonic (laplacian1 3) (fun _ => c) := by
  ext i
  dsimp [IsHarmonic, laplacian1, mulVec, dotProduct]
  rw [← sum_mul]
  have h2 : ∑ j : Fin 3, (discreteGrad 3 * discreteDiv 3) i j = 0 := by
    fin_cases i <;> decide
  rw [h2, zero_mul]

/-- Every harmonic 0-cochain on the 3-cycle is constant. -/
theorem harmonic_0_3_constant (v : Fin 3 → ℤ)
    (h : IsHarmonic (laplacian0 3) v) : ∃ c : ℤ, v = fun _ => c := by
  rw [IsHarmonic, laplacian0_3_eq] at h
  have h0 := congrFun h 0
  have h1 := congrFun h 1
  have h2 := congrFun h 2
  simp [Matrix.mulVec, dotProduct, Fin.sum_univ_three] at h0 h1 h2
  have hv1 : v 1 = v 0 := by omega
  have hv2 : v 2 = v 0 := by omega
  refine ⟨v 0, ?_⟩
  funext i
  fin_cases i
  · rfl
  · exact hv1
  · exact hv2

/-- Every harmonic 1-cochain on the 3-cycle is constant. -/
theorem harmonic_1_3_constant (v : Fin 3 → ℤ)
    (h : IsHarmonic (laplacian1 3) v) : ∃ c : ℤ, v = fun _ => c := by
  rw [IsHarmonic, laplacian1_3_eq] at h
  have h0 := congrFun h 0
  have h1 := congrFun h 1
  have h2 := congrFun h 2
  simp [Matrix.mulVec, dotProduct, Fin.sum_univ_three] at h0 h1 h2
  have hv1 : v 1 = v 0 := by omega
  have hv2 : v 2 = v 0 := by omega
  refine ⟨v 0, ?_⟩
  funext i
  fin_cases i
  · rfl
  · exact hv1
  · exact hv2

/-- Harmonic 0-cochains on the 3-cycle are exactly the constants. -/
theorem isHarmonic_0_3_iff (v : Fin 3 → ℤ) :
    IsHarmonic (laplacian0 3) v ↔ ∃ c : ℤ, v = fun _ => c :=
  ⟨harmonic_0_3_constant v, fun ⟨c, hc⟩ => hc ▸ constant_is_harmonic_0_3 c⟩

/-- Harmonic 1-cochains on the 3-cycle are exactly the constants. -/
theorem isHarmonic_1_3_iff (v : Fin 3 → ℤ) :
    IsHarmonic (laplacian1 3) v ↔ ∃ c : ℤ, v = fun _ => c :=
  ⟨harmonic_1_3_constant v, fun ⟨c, hc⟩ => hc ▸ constant_is_harmonic_1_3 c⟩

/-- The total sum of a gradient on the 3-cycle vanishes. -/
theorem sum_grad_3 (a : Fin 3 → ℤ) :
    (∑ i : Fin 3, (discreteGrad 3 *ᵥ a) i) = 0 := by
  simp [discreteGrad, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  ring

/-- A 1-cochain with zero total sum is a gradient on the 3-cycle. -/
theorem exists_grad_of_sum_zero_3 (v : Fin 3 → ℤ)
    (h : (∑ i : Fin 3, v i) = 0) :
    ∃ a : Fin 3 → ℤ, discreteGrad 3 *ᵥ a = v := by
  simp [Fin.sum_univ_three] at h
  refine ⟨![0, v 0, v 0 + v 1], ?_⟩
  funext i
  have h2 : v 2 = -v 0 - v 1 := by omega
  fin_cases i
  · simp [discreteGrad, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  · simp [discreteGrad, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  · simp [discreteGrad, Matrix.mulVec, dotProduct, Fin.sum_univ_three, h2]
    ring

/-- Exact 1-cochains on the 3-cycle are exactly the zero-sum cochains. -/
theorem range_grad_3 (v : Fin 3 → ℤ) :
    (∃ a : Fin 3 → ℤ, discreteGrad 3 *ᵥ a = v) ↔
      (∑ i : Fin 3, v i) = 0 := by
  constructor
  · rintro ⟨a, ha⟩
    simpa [ha] using sum_grad_3 a
  · exact exists_grad_of_sum_zero_3 v

/-- The constant cochain `1` is not exact on the 3-cycle. -/
theorem constant_one_not_exact_3 :
    ¬ ∃ a : Fin 3 → ℤ, discreteGrad 3 *ᵥ a = (fun _ => 1) := by
  intro h
  have hsum := (range_grad_3 (fun _ => 1)).mp h
  norm_num [Fin.sum_univ_three] at hsum

-- Rational form of the same operators, used for the orthogonal splitting.

/-- Forward difference over the rationals. -/
def discreteGradQ (n : ℕ) [NeZero n] : Matrix (Fin n) (Fin n) ℚ :=
  of fun i j =>
    if j = i then -1
    else if (i.val + 1) % n = j.val then 1
    else 0

/-- The total sum of a rational gradient on the 3-cycle vanishes. -/
theorem sum_grad_3Q (a : Fin 3 → ℚ) :
    (∑ i : Fin 3, (discreteGradQ 3 *ᵥ a) i) = 0 := by
  simp [discreteGradQ, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  ring

/-- A rational 1-cochain with zero total sum is a gradient. -/
theorem exists_grad_of_sum_zero_3Q (v : Fin 3 → ℚ)
    (h : (∑ i : Fin 3, v i) = 0) :
    ∃ a : Fin 3 → ℚ, discreteGradQ 3 *ᵥ a = v := by
  simp [Fin.sum_univ_three] at h
  refine ⟨![0, v 0, v 0 + v 1], ?_⟩
  funext i
  have h2 : v 2 = -v 0 - v 1 := by linarith
  fin_cases i
  · simp [discreteGradQ, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  · simp [discreteGradQ, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  · simp [discreteGradQ, Matrix.mulVec, dotProduct, Fin.sum_univ_three, h2]
    ring

/-- Mean value of a rational 0-cochain on three sites. -/
noncomputable def mean3 (v : Fin 3 → ℚ) : ℚ :=
  (v 0 + v 1 + v 2) / 3

/-- Centering a rational 0-cochain makes its total sum vanish. -/
theorem sum_sub_mean3 (v : Fin 3 → ℚ) :
    (∑ i : Fin 3, (v i - mean3 v)) = 0 := by
  simp [Fin.sum_univ_three, mean3]
  ring

/-- The gradient part is orthogonal to the constant part. -/
theorem dotProduct_grad_const_3 (a : Fin 3 → ℚ) (c : ℚ) :
    dotProduct (discreteGradQ 3 *ᵥ a) (fun _ => c) = 0 := by
  simp only [dotProduct]
  rw [← Finset.sum_mul, sum_grad_3Q]
  simp

/-- Orthogonal Hodge decomposition on the rational 3-cycle:
    every 1-cochain splits into an exact gradient plus its mean value, and the
    two summands are orthogonal. -/
theorem hodge_decomposition_3 (v : Fin 3 → ℚ) :
    ∃ a : Fin 3 → ℚ,
      v = discreteGradQ 3 *ᵥ a + (fun _ => mean3 v) ∧
      dotProduct (discreteGradQ 3 *ᵥ a) (fun _ => mean3 v) = 0 := by
  obtain ⟨a, ha⟩ :=
    exists_grad_of_sum_zero_3Q (fun i => v i - mean3 v) (sum_sub_mean3 v)
  refine ⟨a, ?_, dotProduct_grad_const_3 a (mean3 v)⟩
  funext i
  rw [Pi.add_apply, congrFun ha i]
  ring

end Math30.Topology.DiscreteHodge
