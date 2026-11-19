import Mathlib.Tactic

/-!
  ErdosStrausBoundedVerification.lean
  Math 3.0 Batch 15: Conjecture #5 — the Erdős–Straus Conjecture
  (two parametric families + bounded verification).

  Scope: `erdos_straus_even_general` and `erdos_straus_mod4_eq3_general` are
  FORMAL_GENERAL_THEOREMs covering 75% of all integers: every even `n = 2k`
  with `k ≥ 1`, and every `n = 4k + 3`, is decomposable.
  `erdos_straus_bounded_up_to_50` is a FORMAL_FINITE_THEOREM verifying every
  `2 ≤ n ≤ 50` by explicit division-free witnesses.

  All decompositions are stated without division as
  `4 * x * y * z = n * (y * z + x * z + x * y)`.

  The full Erdős–Straus Conjecture — `∀ n ≥ 2, IsErdosStrausDecomposable n` —
  remains OPEN. In particular, the remaining class `n ≡ 1 (mod 4)` is not
  covered by the general theorems in this module.
-/

namespace Math30.Certificates

/-- `IsErdosStrausDecomposable n` states that `4 / n` is a sum of three unit
    fractions, expressed without division by cross-multiplication:
    `4 * x * y * z = n * (y * z + x * z + x * y)`. -/
def IsErdosStrausDecomposable (n : ℕ) : Prop :=
  ∃ x y z : ℕ,
    0 < x ∧ 0 < y ∧ 0 < z ∧
      4 * x * y * z = n * (y * z + x * z + x * y)

/-- Every even `n = 2k` with `k ≥ 1` is Erdős–Straus decomposable via
    `x = k`, `y = z = 2k`, since `4/(2k) = 1/k + 1/(2k) + 1/(2k)`. -/
theorem erdos_straus_even_general (n : ℕ)
    (heven : ∃ k : ℕ, 1 ≤ k ∧ n = 2 * k) :
    IsErdosStrausDecomposable n := by
  obtain ⟨k, hk, rfl⟩ := heven
  refine ⟨k, 2 * k, 2 * k, by omega, by omega, by omega, by ring⟩

/-- Every `n = 4k + 3` is Erdős–Straus decomposable via
    `x = k + 1`, `y = z = 2 * (k + 1) * (4k + 3)`. -/
theorem erdos_straus_mod4_eq3_general (n : ℕ)
    (hmod : ∃ k : ℕ, n = 4 * k + 3) :
    IsErdosStrausDecomposable n := by
  obtain ⟨k, rfl⟩ := hmod
  refine ⟨k + 1, 2 * (k + 1) * (4 * k + 3), 2 * (k + 1) * (4 * k + 3),
    by omega, by positivity, by positivity, by ring⟩

/-- Bounded deterministic verification: every `2 ≤ n ≤ 50` is Erdős–Straus
    decomposable, sealed by explicit division-free witnesses. -/
theorem erdos_straus_bounded_up_to_50 (n : ℕ) (hn : 2 ≤ n ∧ n ≤ 50) :
    IsErdosStrausDecomposable n := by
  obtain ⟨h2, h50⟩ := hn
  interval_cases n
  · exact ⟨1, 2, 2, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨1, 4, 12, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨2, 3, 6, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨2, 4, 20, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨2, 7, 42, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨2, 15, 210, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨3, 7, 42, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨3, 10, 90, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨3, 16, 240, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨3, 34, 1122, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨4, 13, 156, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨4, 18, 468, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨4, 29, 812, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨4, 61, 3660, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨5, 21, 420, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨5, 30, 510, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨5, 46, 2070, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨5, 96, 9120, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨6, 31, 930, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨6, 43, 1806, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨6, 67, 4422, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨6, 139, 19182, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨7, 43, 1806, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨7, 60, 2100, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨7, 92, 8372, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨7, 190, 35910, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨8, 57, 3192, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨8, 78, 9048, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨8, 121, 14520, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨8, 249, 61752, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨9, 73, 5256, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨9, 100, 9900, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨9, 154, 23562, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨9, 316, 99540, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨10, 91, 8190, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨10, 124, 22940, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨10, 191, 36290, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨10, 391, 152490, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨11, 111, 12210, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨11, 154, 6314, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨11, 232, 53592, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨11, 474, 224202, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨12, 133, 17556, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨12, 181, 32580, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨12, 277, 76452, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨12, 565, 318660, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨13, 157, 24492, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨14, 99, 9702, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨13, 326, 105950, by norm_num, by norm_num, by norm_num, by norm_num⟩

#eval "ErdosStrausBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
