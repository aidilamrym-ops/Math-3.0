-- PolynomialCriticalSieve.lean
-- Math 3.0 Collins-Loos Real Root Isolation via Parametric Differentiation
-- Exact polynomial representation, discrete derivative, linear base case, and Rolle root separation.

import Mathlib.Data.Int.Basic
import Mathlib.Data.List.Basic
import Mathlib.Tactic

namespace Math30.Polynomial

/-- Polynomial represented as a list of integer coefficients in descending degree order:
    `[a_n, a_{n-1}, ..., a_1, a_0]` represents $\sum_{i=0}^n a_i x^i$. -/
abbrev Poly := List ℤ

/-- Evaluate polynomial at rational point `x`. -/
def eval (p : Poly) (x : ℚ) : ℚ :=
  match p with
  | [] => 0
  | c :: cs => cs.foldl (fun acc coeff => acc * x + (coeff : ℚ)) (c : ℚ)

theorem eval_two (a b : ℤ) (x : ℚ) : eval [a, b] x = (a : ℚ) * x + (b : ℚ) := by
  rfl

theorem eval_three (a b c : ℤ) (x : ℚ) :
    eval [a, b, c] x = ((a : ℚ) * x + b) * x + c := by
  rfl

/-- Simplified discrete derivative on `[a_n, ..., a_0]`. -/
def polyDeriv (p : Poly) : Poly :=
  let n := p.length - 1
  (p.zip (List.range p.length)).dropLast.map (fun ⟨coeff, i⟩ =>
    coeff * ((n - i : ℕ) : ℤ))

/-- Base case: degree 1 polynomial `[a, b]` representing $ax + b = 0$ with $a \neq 0$.
    Unique rational root is $-b / a$. -/
theorem linear_root_unique (a b : ℤ) (ha : a ≠ 0) (x : ℚ) :
    eval [a, b] x = 0 ↔ x = - (b : ℚ) / (a : ℚ) := by
  rw [eval_two]
  have ha_q : (a : ℚ) ≠ 0 := by exact_mod_cast ha
  constructor
  · intro h
    have h2 : (a : ℚ) * x = - (b : ℚ) := by linarith [h]
    rw [mul_comm] at h2
    exact (eq_div_iff ha_q).mpr h2
  · intro h
    have h2 : x * (a : ℚ) = - (b : ℚ) := (eq_div_iff ha_q).mp h
    rw [mul_comm] at h2
    linarith [h2]

/-- Rolle's theorem for a quadratic `[A, B, C]`: if the polynomial vanishes at
    two rational points `u < v`, then its derivative vanishes at the midpoint.
    This is a finite algebraic instance of Rolle's theorem, not the general
    theorem for arbitrary polynomials. -/
theorem rolles_separation_bound (A B C : ℤ) (u v : ℚ) (huv : u < v)
    (h_roots : eval [A, B, C] u = 0 ∧ eval [A, B, C] v = 0) :
    ∃ c ∈ Set.Ioo u v, eval (polyDeriv [A, B, C]) c = 0 := by
  refine ⟨(u + v) / 2, ⟨by linarith, by linarith⟩, ?_⟩
  have hfac : eval [A, B, C] u - eval [A, B, C] v =
      (u - v) * ((A : ℚ) * (u + v) + (B : ℚ)) := by
    rw [eval_three A B C u, eval_three A B C v]
    ring
  have hdiff : eval [A, B, C] u - eval [A, B, C] v = 0 := by
    rw [h_roots.1, h_roots.2, sub_self]
  rw [hfac] at hdiff
  have huv' : (u - v : ℚ) ≠ 0 := sub_ne_zero.mpr (ne_of_lt huv)
  have hsum : (A : ℚ) * (u + v) + (B : ℚ) = 0 :=
    (mul_eq_zero.mp hdiff).resolve_left huv'
  have hderiv : eval (polyDeriv [A, B, C]) ((u + v) / 2) =
      2 * (A : ℚ) * ((u + v) / 2) + (B : ℚ) := by
    rw [show polyDeriv [A, B, C] = [A * 2, B * 1] by rfl]
    rw [eval_two (A * 2) (B * 1)]
    push_cast
    ring
  rw [hderiv]
  calc
    2 * (A : ℚ) * ((u + v) / 2) + (B : ℚ) = (A : ℚ) * (u + v) + (B : ℚ) := by ring
    _ = 0 := by rw [hsum]

#print axioms linear_root_unique
#print axioms rolles_separation_bound

end Math30.Polynomial
