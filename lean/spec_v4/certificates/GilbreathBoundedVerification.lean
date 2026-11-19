import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic

/-!
  GilbreathBoundedVerification.lean
  Math 3.0 Batch 16: Conjecture #6 — Gilbreath's Conjecture
  (bounded verification on the first 20 primes + parity invariant).

  Scope: `gilbreath_first_20_primes` is a FORMAL_FINITE_THEOREM verifying
  all 19 iterated absolute-difference rows of the first 20 primes have
  leading entry 1. `gilbreath_parity_preservation_general` is a structural
  FORMAL_GENERAL_THEOREM: a leading 2 followed by odd entries yields an odd
  leading entry and even trailing entries after one step.

  The full Gilbreath Conjecture — every iterated difference row of the
  sequence of primes begins with 1 — remains OPEN. The parity invariant
  alone does not prove that the leading entry stays 1.
-/

namespace Math30.Certificates

/-- One Gilbreath step: replace each adjacent pair `(a, b)` by `|a - b|`,
    computed without subtraction on integers by cases on `a ≤ b`. -/
def gilbreathStep : List ℕ → List ℕ
  | a :: b :: rest => (if a ≤ b then b - a else a - b) :: gilbreathStep (b :: rest)
  | _ => []

/-- Iterate the Gilbreath difference operator `k` times. -/
def gilbreathIter : ℕ → List ℕ → List ℕ
  | 0, xs => xs
  | k + 1, xs => gilbreathIter k (gilbreathStep xs)

/-- `SatisfiesGilbreathHead xs` states that every nonempty iterated
    difference row `gilbreathIter k xs` (for `1 ≤ k < xs.length`) has
    leading entry `1`. -/
def SatisfiesGilbreathHead (xs : List ℕ) : Prop :=
  ∀ k : ℕ, 1 ≤ k → k < xs.length → (gilbreathIter k xs).head? = some 1

/-- Bounded deterministic verification: the first 20 primes satisfy
    Gilbreath's head condition across all 19 iterated rows. -/
theorem gilbreath_first_20_primes (ps : List ℕ)
    (hps : ps = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]) :
    SatisfiesGilbreathHead ps := by
  rw [hps]
  intro k h1 hk
  have hk20 : k < 20 := by simpa using hk
  interval_cases k <;> decide

/-- Structural parity lock: if `xs = 2 :: x :: rest` with `x` odd and every
    element of `rest` odd, then one Gilbreath step has an odd leading entry
    and all trailing entries even. -/
theorem gilbreath_parity_preservation_general (xs : List ℕ)
    (hhead : ∃ x rest, xs = 2 :: x :: rest ∧ x % 2 = 1)
    (hodd_tail : ∀ y ∈ xs.drop 2, y % 2 = 1) :
    ∃ h t, gilbreathStep xs = h :: t ∧ h % 2 = 1 ∧
      ∀ z ∈ t, z % 2 = 0 := by
  obtain ⟨x, rest, rfl, hx⟩ := hhead
  have htail : ∀ y ∈ rest, y % 2 = 1 := by
    simpa using hodd_tail
  have hstep_even : ∀ ys : List ℕ, (∀ y ∈ ys, y % 2 = 1) →
      ∀ z ∈ gilbreathStep ys, z % 2 = 0 := by
    intro ys
    induction ys with
    | nil => simp [gilbreathStep]
    | cons a rest ih =>
      cases rest with
      | nil => simp [gilbreathStep]
      | cons b rest =>
        intro hall z hz
        simp only [gilbreathStep, List.mem_cons] at hz
        rcases hz with rfl | hz
        · have ha : a % 2 = 1 := hall a (by simp)
          have hb : b % 2 = 1 := hall b (by simp)
          split <;> omega
        · exact ih (fun y hy => hall y (by simp [hy])) z hz
  refine ⟨(if 2 ≤ x then x - 2 else 2 - x), gilbreathStep (x :: rest), ?_, ?_, ?_⟩
  · simp [gilbreathStep]
  · split <;> omega
  · apply hstep_even
    intro y hy
    rcases List.mem_cons.mp hy with rfl | hy
    · exact hx
    · exact htail y hy

#eval "GilbreathBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
