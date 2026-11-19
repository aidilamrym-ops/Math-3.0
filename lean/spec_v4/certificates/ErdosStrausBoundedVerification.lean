import Mathlib.Tactic

/-!
  ErdosStrausBoundedVerification.lean
  Math 3.0 Batch 15: Conjecture #5 — the Erdős–Straus Conjecture
  (two parametric families + bounded verification).

  Scope: `erdos_straus_even_general` and `erdos_straus_mod4_eq3_general` are
  FORMAL_GENERAL_THEOREMs covering 75% of all integers: every even `n = 2k`
  with `k ≥ 1`, and every `n = 4k + 3`, is decomposable.
  `erdos_straus_bounded_up_to_50` and `erdos_straus_bounded_up_to_200` are
  FORMAL_FINITE_THEOREMs verifying every case in their range by explicit
  division-free witnesses.

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

/-- Bounded deterministic verification: every `2 ≤ n ≤ 200` is Erdős–Straus
    decomposable, sealed by explicit division-free witnesses. -/
theorem erdos_straus_bounded_up_to_200 (n : ℕ) (hn : 2 ≤ n ∧ n ≤ 200) :
    IsErdosStrausDecomposable n := by
  obtain ⟨h2, h200⟩ := hn
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
  · exact ⟨13, 664, 440232, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨14, 183, 33306, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨14, 248, 92008, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨14, 379, 143262, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨14, 771, 593670, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨15, 211, 44310, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨15, 286, 81510, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨15, 436, 189660, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨15, 886, 784110, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨16, 241, 57840, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨16, 326, 159088, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨16, 497, 246512, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨16, 1009, 1017072, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨17, 273, 74256, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨17, 370, 81770, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨17, 562, 315282, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨17, 1140, 1298460, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨18, 307, 93942, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨18, 415, 171810, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨18, 631, 397530, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨18, 1279, 1634562, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨19, 343, 117306, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨20, 210, 30660, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨19, 704, 494912, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨19, 1426, 2032050, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨20, 381, 144780, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨20, 514, 395780, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨20, 781, 609180, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨20, 1581, 2497980, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨21, 421, 176820, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨21, 568, 322056, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨21, 862, 742182, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨21, 1744, 3039792, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨22, 463, 213906, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨22, 624, 583440, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨22, 947, 895862, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨22, 1915, 3665310, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨23, 507, 256542, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨23, 690, 61410, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨23, 1036, 1072260, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨23, 2094, 4382742, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨24, 553, 305256, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨24, 745, 554280, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨24, 1129, 1273512, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨24, 2281, 5200680, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨25, 601, 360600, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨25, 810, 392850, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨25, 1226, 1501850, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨25, 2476, 6128100, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨26, 651, 423150, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨26, 876, 1150188, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨26, 1327, 1759602, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨26, 2679, 7174362, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨27, 703, 493506, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨27, 946, 893970, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨27, 1432, 2049192, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨27, 2890, 8349210, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨28, 757, 572292, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨28, 1018, 1553468, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨28, 1541, 2373140, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨28, 3109, 9662772, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨29, 813, 660156, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨29, 1102, 124526, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨29, 1654, 2734062, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨29, 3336, 11125560, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨30, 871, 757770, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨30, 1171, 1370070, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨30, 1771, 3134670, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨30, 3571, 12748470, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨31, 931, 865830, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨31, 1254, 427614, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨31, 1892, 3577772, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨31, 3814, 14542782, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨32, 993, 985056, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨32, 1334, 2668000, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨32, 2017, 4066272, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨32, 4065, 16520160, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨33, 1057, 1116192, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨33, 1420, 2014980, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨33, 2146, 4603170, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨33, 4324, 18692652, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨34, 1123, 1260006, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨34, 1508, 3409588, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨34, 2279, 5191562, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨34, 4591, 21072690, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨35, 1191, 1417290, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨35, 1600, 1534400, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨35, 2416, 5834640, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨35, 4866, 23673090, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨36, 1261, 1588860, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨36, 1693, 2864556, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨36, 2557, 6535692, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨36, 5149, 26507052, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨37, 1333, 1775556, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨37, 1790, 1920670, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨37, 2702, 7298102, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨37, 5440, 29588160, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨38, 1407, 1978242, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨38, 1888, 5344928, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨38, 2851, 8125350, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨38, 5739, 32930382, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨39, 1483, 2197806, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨39, 1990, 3958110, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨39, 3004, 9021012, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨39, 6046, 36548070, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨40, 1561, 2435160, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨40, 2094, 6575160, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨40, 3161, 9988760, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨40, 6361, 40455960, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨41, 1641, 2691240, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨41, 2208, 633696, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨41, 3322, 11032362, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨41, 6684, 44669172, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨42, 1723, 2967006, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨42, 2311, 5338410, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨42, 3487, 12155682, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨42, 7015, 49203210, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨43, 1807, 3263442, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨44, 1066, 304876, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨43, 3656, 13362680, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨43, 7354, 54073962, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨44, 1893, 3581556, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨44, 2538, 9659628, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨44, 3829, 14657412, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨44, 7701, 59297700, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨45, 1981, 3922380, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨45, 2656, 7051680, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨45, 4006, 16044030, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨45, 8056, 64891080, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨46, 2071, 4286970, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨46, 2776, 11556488, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨46, 4187, 17526782, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨46, 8419, 70871142, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨47, 2163, 4676406, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨47, 2900, 5043100, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨47, 4372, 19110012, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨47, 8790, 77255310, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨48, 2257, 5091792, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨48, 3025, 9147600, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨48, 4561, 20798160, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨48, 9169, 84061392, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨49, 2353, 5534256, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨50, 1380, 1331700, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨49, 4754, 22595762, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨49, 9556, 91307580, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨50, 2451, 6004950, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨50, 3284, 16173700, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨50, 4951, 24507450, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨50, 9951, 99012450, by norm_num, by norm_num, by norm_num, by norm_num⟩
  · exact ⟨51, 2551, 6505050, by norm_num, by norm_num, by norm_num, by norm_num⟩

#eval "ErdosStrausBoundedVerification certificate compiled with zero placeholders."

end Math30.Certificates
