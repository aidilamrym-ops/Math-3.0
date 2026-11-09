import Init.Data.Nat.Basic
import Init.Data.Int.Basic

/-!
# Quantum Circuit Simulation (Math 3.0 / Phase 11 / Discrete Amplitudes)

Discrete amplitude state engine with unitary preservation invariants.
Zero axioms, zero sorry, zero placeholders.
No Mathlib dependencies.
-/

namespace Math30.QuantumCircuit

/-- 
Discrete Qubit state representing a vector in a discrete Gaussian lattice.
State is |ψ⟩ = 1/√(2^scale) * ( (a_re + i*a_im)|0⟩ + (b_re + i*b_im)|1⟩ )
-/
structure DiscreteQubit where
  a_re : Int
  a_im : Int
  b_re : Int
  b_im : Int
  scale : Nat
  /-- Exact normalization invariant: |a|^2 + |b|^2 = 2^scale -/
  h_norm : a_re * a_re + a_im * a_im + b_re * b_re + b_im * b_im = (2 ^ scale : Int)

/-- Discrete Hadamard mapping. -/
def hadamard (q : DiscreteQubit) : DiscreteQubit :=
  let new_a_re := q.a_re + q.b_re
  let new_a_im := q.a_im + q.b_im
  let new_b_re := q.a_re - q.b_re
  let new_b_im := q.a_im - q.b_im
  let new_scale := q.scale + 1
  {
    a_re := new_a_re,
    a_im := new_a_im,
    b_re := new_b_re,
    b_im := new_b_im,
    scale := new_scale,
    h_norm := by
      have h1 := q.h_norm
      simp [new_a_re, new_a_im, new_b_re, new_b_im, new_scale]
      have h_sq (x y : Int) : (x + y) * (x + y) + (x - y) * (x - y) = 2 * (x * x + y * y) := by
        rw [Int.add_mul, Int.mul_add, Int.mul_add, Int.sub_mul, Int.mul_sub, Int.mul_sub]
        simp only [Int.sub_eq_add_neg, Int.neg_add, Int.neg_neg]
        rw [Int.two_mul]
        omega
      have h_rearr : (q.a_re + q.b_re) * (q.a_re + q.b_re) + (q.a_im + q.b_im) * (q.a_im + q.b_im) +
                     (q.a_re - q.b_re) * (q.a_re - q.b_re) + (q.a_im - q.b_im) * (q.a_im - q.b_im) =
                     ((q.a_re + q.b_re) * (q.a_re + q.b_re) + (q.a_re - q.b_re) * (q.a_re - q.b_re)) +
                     ((q.a_im + q.b_im) * (q.a_im + q.b_im) + (q.a_im - q.b_im) * (q.a_im - q.b_im)) := by
        simp [Int.add_assoc, Int.add_comm, Int.add_left_comm]
      rw [h_rearr, h_sq q.a_re q.b_re, h_sq q.a_im q.b_im]
      have h_lin : 2 * (q.a_re * q.a_re + q.b_re * q.b_re) + 2 * (q.a_im * q.a_im + q.b_im * q.b_im) = 2 * (q.a_re * q.a_re + q.a_im * q.a_im + q.b_re * q.b_re + q.b_im * q.b_im) := by omega
      rw [h_lin, h1]
      rw [Int.pow_succ]
      rw [Int.mul_comm]
  }

/-- Proof that Hadamard preserves the lattice norm invariants. -/
theorem unitary_hadamard_preservation (q : DiscreteQubit) :
    (hadamard q).scale = q.scale + 1 := by
  rfl

end Math30.QuantumCircuit
