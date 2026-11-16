-- SturmTarskiIsolation.lean
-- Math 3.0: finite sign-variation arithmetic.
--
-- Scope:
--   * polynomial evaluation at rational points;
--   * sign of a rational number and sign-change counting with zeros ignored;
--   * the algebraic one-step remainder relation for a linear combination of
--     polynomial evaluations.
--
-- Claim limits:
--   * this file does NOT implement a Sturm chain, a Sturm theorem, or a real
--     root-isolation algorithm; the former `sturmChain` generator repeated its
--     second argument instead of computing a remainder and has been removed;
--   * no theorem here counts or isolates roots of a real polynomial;
--   * only finite sign-variation arithmetic and concrete list computations
--     are proved.

import Mathlib.Data.Int.Basic
import Mathlib.Data.List.Basic
import Mathlib.Tactic

namespace Math30.SturmTarski

/-- Polynomial representation as coefficient list (descending degree). -/
abbrev Poly := List ℤ

/-- Polynomial evaluation at rational point `x`. -/
def eval (p : Poly) (x : ℚ) : ℚ :=
  match p with
  | [] => 0
  | c :: cs => cs.foldl (fun acc coeff => acc * x + (coeff : ℚ)) (c : ℚ)

/-- Evaluation of a linear polynomial `[a, b]`. -/
theorem eval_two (a b : ℤ) (x : ℚ) : eval [a, b] x = (a : ℚ) * x + (b : ℚ) := by
  rfl

/-- Sign of a rational number (-1, 0, or 1). -/
def sign (q : ℚ) : ℤ :=
  if q > 0 then 1 else if q < 0 then -1 else 0

/-- Count sign changes in a list of rational evaluations (ignoring zeros). -/
def signChanges (values : List ℚ) : ℕ :=
  let nonZeroSigns := values.map sign |>.filter (fun s => s ≠ 0)
  (nonZeroSigns.zip (nonZeroSigns.tail)).foldl (fun count ⟨s1, s2⟩ =>
    if s1 ≠ s2 then count + 1 else count) 0

/-- Evaluate a list of polynomials (a candidate chain) at `x`. -/
def evalChain (chain : List Poly) (x : ℚ) : List ℚ :=
  chain.map (fun p => eval p x)

/-- Algebraic remainder step: if `p0(q) = p1(q) * q - p2(q)`, then `p0` and
    `p1` vanish together at `q` exactly when `p1` and `p2` do. This is a
    linear-combination identity, not a Sturm root-counting theorem. -/
theorem sturm_remainder_invariant (p0 p1 p2 : Poly) (q : ℚ)
    (h_rel : eval p0 q = eval p1 q * q - eval p2 q) :
    eval p0 q = 0 ∧ eval p1 q = 0 ↔ eval p1 q = 0 ∧ eval p2 q = 0 := by
  constructor
  · intro ⟨h0, h1⟩
    have h2 : eval p2 q = 0 := by
      calc eval p2 q = eval p1 q * q - eval p0 q := by linarith [h_rel]
      _ = 0 * q - 0 := by rw [h1, h0]
      _ = 0 := by ring
    exact ⟨h1, h2⟩
  · intro ⟨h1, h2⟩
    have h0 : eval p0 q = 0 := by
      calc eval p0 q = eval p1 q * q - eval p2 q := h_rel
      _ = 0 * q - 0 := by rw [h1, h2]
      _ = 0 := by ring
    exact ⟨h0, h1⟩

/-! ## Concrete finite sign-variation computations -/

theorem signChanges_nil : signChanges [] = 0 := rfl

theorem signChanges_pos_pos : signChanges [1, 2] = 0 := by decide

theorem signChanges_pos_neg : signChanges [1, -1] = 1 := by decide

theorem signChanges_zero_ignored : signChanges [1, 0, -2] = 1 := by decide

theorem evalChain_linear_pair :
    evalChain [[1, 0], [1, -1]] 2 = [2, 1] := by
  simp only [evalChain, List.map_cons, List.map_nil]
  rw [eval_two, eval_two]
  norm_num

#print axioms sturm_remainder_invariant
#print axioms signChanges_pos_neg

end Math30.SturmTarski
