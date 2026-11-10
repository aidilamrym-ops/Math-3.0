/-
Gate 5: Exact Rational Extraction Bridge (interval -> ℚ).

Every numeric endpoint produced by the python-flint layer is transported into
Lean as an exact pair `(num, den)` with `den > 0`.  This module proves the
generic facts that make that transport sound, independently of any concrete
numeric receipt:

* `RatInterval` / `Contains`: closed rational intervals and membership.
* `contains_midpoint`: the exact midpoint of a nonnegative-radius ball lies in
  its own enclosure.
* `sign_positive`, `sign_negative`: a strict endpoint sign propagates to every
  contained rational, so no decimal truncation can flip a sign.
* `exactRat_mul_den`: scaling a transported rational by its denominator
  recovers the integer numerator exactly.
* `exactRat_cross_eq`: equality of two transported rationals is equivalent to
  integer cross-multiplication, i.e. the conversion loses no information.
* `exactRat_injective`: that equivalence in the forward direction.
* `exactRat_pos`: positivity of a transported rational is positivity of its
  integer numerator.

These are generic lemmas.  The generated companion file
`Gate5RationalExtractionValidation.lean` instantiates them with the concrete
endpoints extracted from the Gate 4 receipts.
-/
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic

namespace Math30.Gate5

/-- A closed rational interval with exact `ℚ` endpoints. -/
structure RatInterval where
  lo : ℚ
  hi : ℚ
deriving Repr, DecidableEq

/-- Membership in a closed rational interval. -/
def Contains (I : RatInterval) (q : ℚ) : Prop := I.lo ≤ q ∧ q ≤ I.hi

theorem contains_of_bounds {I : RatInterval} {q : ℚ}
    (hlo : I.lo ≤ q) (hhi : q ≤ I.hi) : Contains I q :=
  ⟨hlo, hhi⟩

theorem contains_lower {I : RatInterval} {q : ℚ} (h : Contains I q) : I.lo ≤ q :=
  h.1

theorem contains_upper {I : RatInterval} {q : ℚ} (h : Contains I q) : q ≤ I.hi :=
  h.2

/-- The exact midpoint of a ball with nonnegative radius lies in the ball. -/
theorem contains_midpoint (m r : ℚ) (hr : 0 ≤ r) :
    Contains ⟨m - r, m + r⟩ m := by
  constructor <;> linarith

/-- A strictly positive lower endpoint forces every contained rational to be
positive.  This is the sign-soundness lemma for interval transport. -/
theorem sign_positive {I : RatInterval} {q : ℚ}
    (h : Contains I q) (hlo : 0 < I.lo) : 0 < q :=
  lt_of_lt_of_le hlo h.1

/-- A strictly negative upper endpoint forces every contained rational to be
negative. -/
theorem sign_negative {I : RatInterval} {q : ℚ}
    (h : Contains I q) (hhi : I.hi < 0) : q < 0 :=
  lt_of_le_of_lt h.2 hhi

/-- A positive interval has no sign ambiguity at all. -/
theorem contains_positive {I : RatInterval} {q : ℚ}
    (h : Contains I q) (hlo : 0 < I.lo) : 0 < q :=
  sign_positive h hlo

/-- A negative interval has no sign ambiguity at all. -/
theorem contains_negative {I : RatInterval} {q : ℚ}
    (h : Contains I q) (hhi : I.hi < 0) : q < 0 :=
  sign_negative h hhi

/-- Exact rational constructed from an integer numerator and a natural
denominator.  This is the only conversion constructor used by the generated
certificate; no decimal or floating-point literal is involved. -/
def exactRat (n : ℤ) (d : ℕ) : ℚ :=
  (n : ℚ) / (d : ℚ)

@[simp] theorem exactRat_zero (n : ℤ) : exactRat n 0 = 0 := by
  simp [exactRat]

/-- Scaling a transported rational by its denominator recovers the integer
numerator exactly: the conversion is lossless. -/
theorem exactRat_mul_den {n : ℤ} {d : ℕ} (hd : d ≠ 0) :
    exactRat n d * (d : ℚ) = (n : ℚ) := by
  unfold exactRat
  have hd' : (d : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr hd
  field_simp

/-- Equality of two transported rationals is decided exactly by integer
cross-multiplication. -/
theorem exactRat_cross_eq {n1 n2 : ℤ} {d1 d2 : ℕ} (h1 : d1 ≠ 0) (h2 : d2 ≠ 0) :
    exactRat n1 d1 = exactRat n2 d2 ↔
      (n1 : ℚ) * (d2 : ℚ) = (n2 : ℚ) * (d1 : ℚ) := by
  unfold exactRat
  exact div_eq_div_iff (Nat.cast_ne_zero.mpr h1) (Nat.cast_ne_zero.mpr h2)

/-- Forward direction of the lossless-equality property, stated over `ℤ`:
equal transported rationals imply equal integer cross-products. -/
theorem exactRat_injective {n1 n2 : ℤ} {d1 d2 : ℕ}
    (h1 : 0 < d1) (h2 : 0 < d2) (h : exactRat n1 d1 = exactRat n2 d2) :
    n1 * (d2 : ℤ) = n2 * (d1 : ℤ) := by
  have hq := (exactRat_cross_eq (ne_of_gt h1) (ne_of_gt h2)).mp h
  exact_mod_cast hq

/-- A transported rational is zero exactly when its integer numerator is zero. -/
theorem exactRat_eq_zero {n : ℤ} {d : ℕ} (hd : d ≠ 0) :
    exactRat n d = 0 ↔ n = 0 := by
  unfold exactRat
  have hd' : (d : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr hd
  rw [div_eq_zero_iff]
  constructor
  · rintro (h | h)
    · exact_mod_cast h
    · exact absurd h hd'
  · intro h
    left
    exact_mod_cast h

/-- Positivity of a transported rational is exactly positivity of its integer
numerator. -/
theorem exactRat_pos {n : ℤ} {d : ℕ} (hd : 0 < d) :
    0 < exactRat n d ↔ 0 < n := by
  unfold exactRat
  have hd' : (0 : ℚ) < (d : ℚ) := by exact_mod_cast hd
  constructor
  · intro h
    by_contra hn
    have hn' : n ≤ 0 := by omega
    have hle : (n : ℚ) ≤ 0 := by exact_mod_cast hn'
    have hnonpos : (n : ℚ) / (d : ℚ) ≤ 0 :=
      div_nonpos_of_nonpos_of_nonneg hle (le_of_lt hd')
    linarith
  · intro h
    exact div_pos (by exact_mod_cast h) hd'

end Math30.Gate5
