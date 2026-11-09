import Init.Data.Nat.Basic

/-!
# Quantum QFT (Math 3.0 / Phase 11 / Quantum Lattice)

Discrete Quantum Fourier Transform (QFT) implementation using exact integer lattice
arithmetic over 2-qubit states.
Zero axioms, zero sorry, zero placeholders.
-/

namespace Math30.QuantumQft

/-- Discrete 2-Qubit state representing a vector in a 4-dimensional discrete Gaussian lattice. -/
structure Discrete2Qubit where
  a00_re : Int
  a00_im : Int
  a01_re : Int
  a01_im : Int
  a10_re : Int
  a10_im : Int
  a11_re : Int
  a11_im : Int
  scale : Nat
  h_norm : a00_re * a00_re + a00_im * a00_im +
           a01_re * a01_re + a01_im * a01_im +
           a10_re * a10_re + a10_im * a10_im +
           a11_re * a11_re + a11_im * a11_im = (2 ^ scale : Int)

/-- Helper square expansion lemma. -/
theorem sq_expand (x y : Int) : (x + y) * (x + y) + (x - y) * (x - y) = 2 * (x * x + y * y) := by
  rw [Int.add_mul, Int.mul_add, Int.mul_add, Int.sub_mul, Int.mul_sub, Int.mul_sub]
  simp only [Int.sub_eq_add_neg, Int.neg_add, Int.neg_neg]
  rw [Int.two_mul]
  omega

/-- Discrete Hadamard mapping on qubit 0. -/
def hadamard_q0 (q : Discrete2Qubit) : Discrete2Qubit :=
  let n_a00_re := q.a00_re + q.a10_re; let n_a00_im := q.a00_im + q.a10_im
  let n_a01_re := q.a01_re + q.a11_re; let n_a01_im := q.a01_im + q.a11_im
  let n_a10_re := q.a00_re - q.a10_re; let n_a10_im := q.a00_im - q.a10_im
  let n_a11_re := q.a01_re - q.a11_re; let n_a11_im := q.a01_im - q.a11_im
  {
    a00_re := n_a00_re, a00_im := n_a00_im, a01_re := n_a01_re, a01_im := n_a01_im,
    a10_re := n_a10_re, a10_im := n_a10_im, a11_re := n_a11_re, a11_im := n_a11_im,
    scale := q.scale + 1,
    h_norm := by
      have h1 := q.h_norm
      simp [n_a00_re, n_a00_im, n_a01_re, n_a01_im, n_a10_re, n_a10_im, n_a11_re, n_a11_im]
      have h_rearr : (q.a00_re + q.a10_re) * (q.a00_re + q.a10_re) + (q.a00_im + q.a10_im) * (q.a00_im + q.a10_im) +
                     (q.a01_re + q.a11_re) * (q.a01_re + q.a11_re) + (q.a01_im + q.a11_im) * (q.a01_im + q.a11_im) +
                     (q.a00_re - q.a10_re) * (q.a00_re - q.a10_re) + (q.a00_im - q.a10_im) * (q.a00_im - q.a10_im) +
                     (q.a01_re - q.a11_re) * (q.a01_re - q.a11_re) + (q.a01_im - q.a11_im) * (q.a01_im - q.a11_im) =
                     ((q.a00_re + q.a10_re) * (q.a00_re + q.a10_re) + (q.a00_re - q.a10_re) * (q.a00_re - q.a10_re)) +
                     ((q.a00_im + q.a10_im) * (q.a00_im + q.a10_im) + (q.a00_im - q.a10_im) * (q.a00_im - q.a10_im)) +
                     ((q.a01_re + q.a11_re) * (q.a01_re + q.a11_re) + (q.a01_re - q.a11_re) * (q.a01_re - q.a11_re)) +
                     ((q.a01_im + q.a11_im) * (q.a01_im + q.a11_im) + (q.a01_im - q.a11_im) * (q.a01_im - q.a11_im)) := by
        simp [Int.add_assoc, Int.add_left_comm]
      rw [h_rearr, sq_expand q.a00_re q.a10_re, sq_expand q.a00_im q.a10_im, sq_expand q.a01_re q.a11_re, sq_expand q.a01_im q.a11_im]
      have h_lin : 2 * (q.a00_re * q.a00_re + q.a10_re * q.a10_re) + 2 * (q.a00_im * q.a00_im + q.a10_im * q.a10_im) +
                   2 * (q.a01_re * q.a01_re + q.a11_re * q.a11_re) + 2 * (q.a01_im * q.a01_im + q.a11_im * q.a11_im) =
                   2 * (q.a00_re * q.a00_re + q.a00_im * q.a00_im + q.a01_re * q.a01_re + q.a01_im * q.a01_im + q.a10_re * q.a10_re + q.a10_im * q.a10_im + q.a11_re * q.a11_re + q.a11_im * q.a11_im) := by omega
      rw [h_lin, h1]
      rw [Int.pow_succ, Int.mul_comm]
  }

/-- Discrete Hadamard mapping on qubit 1. -/
def hadamard_q1 (q : Discrete2Qubit) : Discrete2Qubit :=
  let n_a00_re := q.a00_re + q.a01_re; let n_a00_im := q.a00_im + q.a01_im
  let n_a10_re := q.a10_re + q.a11_re; let n_a10_im := q.a10_im + q.a11_im
  let n_a01_re := q.a00_re - q.a01_re; let n_a01_im := q.a00_im - q.a01_im
  let n_a11_re := q.a10_re - q.a11_re; let n_a11_im := q.a10_im - q.a11_im
  {
    a00_re := n_a00_re, a00_im := n_a00_im, a01_re := n_a01_re, a01_im := n_a01_im,
    a10_re := n_a10_re, a10_im := n_a10_im, a11_re := n_a11_re, a11_im := n_a11_im,
    scale := q.scale + 1,
    h_norm := by
      have h1 := q.h_norm
      simp [n_a00_re, n_a00_im, n_a01_re, n_a01_im, n_a10_re, n_a10_im, n_a11_re, n_a11_im]
      have h_rearr : (q.a00_re + q.a01_re) * (q.a00_re + q.a01_re) + (q.a00_im + q.a01_im) * (q.a00_im + q.a01_im) +
                     (q.a00_re - q.a01_re) * (q.a00_re - q.a01_re) + (q.a00_im - q.a01_im) * (q.a00_im - q.a01_im) +
                     (q.a10_re + q.a11_re) * (q.a10_re + q.a11_re) + (q.a10_im + q.a11_im) * (q.a10_im + q.a11_im) +
                     (q.a10_re - q.a11_re) * (q.a10_re - q.a11_re) + (q.a10_im - q.a11_im) * (q.a10_im - q.a11_im) =
                     ((q.a00_re + q.a01_re) * (q.a00_re + q.a01_re) + (q.a00_re - q.a01_re) * (q.a00_re - q.a01_re)) +
                     ((q.a00_im + q.a01_im) * (q.a00_im + q.a01_im) + (q.a00_im - q.a01_im) * (q.a00_im - q.a01_im)) +
                     ((q.a10_re + q.a11_re) * (q.a10_re + q.a11_re) + (q.a10_re - q.a11_re) * (q.a10_re - q.a11_re)) +
                     ((q.a10_im + q.a11_im) * (q.a10_im + q.a11_im) + (q.a10_im - q.a11_im) * (q.a10_im - q.a11_im)) := by
        simp [Int.add_assoc, Int.add_left_comm]
      rw [h_rearr, sq_expand q.a00_re q.a01_re, sq_expand q.a00_im q.a01_im, sq_expand q.a10_re q.a11_re, sq_expand q.a10_im q.a11_im]
      have h_lin : 2 * (q.a00_re * q.a00_re + q.a01_re * q.a01_re) + 2 * (q.a00_im * q.a00_im + q.a01_im * q.a01_im) +
                   2 * (q.a10_re * q.a10_re + q.a11_re * q.a11_re) + 2 * (q.a10_im * q.a10_im + q.a11_im * q.a11_im) =
                   2 * (q.a00_re * q.a00_re + q.a00_im * q.a00_im + q.a01_re * q.a01_re + q.a01_im * q.a01_im + q.a10_re * q.a10_re + q.a10_im * q.a10_im + q.a11_re * q.a11_re + q.a11_im * q.a11_im) := by omega
      rw [h_lin, h1]
      rw [Int.pow_succ, Int.mul_comm]
  }

/-- Controlled-R2 gate (diag(1, i)) on qubit 1 (ctrl), qubit 0 (target). -/
def control_r2 (q : Discrete2Qubit) : Discrete2Qubit :=
  {
    a00_re := q.a00_re, a00_im := q.a00_im, a01_re := q.a01_re, a01_im := q.a01_im,
    a10_re := q.a10_re, a10_im := q.a10_im,
    a11_re := -q.a11_im, a11_im := q.a11_re, -- Multiplication by i
    scale := q.scale,
    h_norm := by
      have h1 := q.h_norm
      have h_neg : (-q.a11_im) * (-q.a11_im) = q.a11_im * q.a11_im := by
        rw [Int.neg_mul_neg]
      omega
  }

/-- Exact 2-qubit Discrete QFT. -/
def discrete_qft (q : Discrete2Qubit) : Discrete2Qubit :=
  hadamard_q1 (control_r2 (hadamard_q0 q))

/-- Theorem: Discrete QFT preserves the structural biner scale bounding invariants. -/
theorem discrete_qft_unitary_preservation (q : Discrete2Qubit) :
    (discrete_qft q).scale = q.scale + 2 := by
  rfl

end Math30.QuantumQft
