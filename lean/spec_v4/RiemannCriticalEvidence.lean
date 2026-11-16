-- RiemannCriticalEvidence.lean
-- Math 3.0: rational interval records (finite arithmetic only).
--
-- Scope:
--   * a structure bundling two nonnegative rational endpoints and the proof
--     `loNum * hiDen ≤ hiNum * loDen`;
--   * two decimal interval records retained for the legacy Phase 7 harness.
--
-- Claim limits:
--   * this file does NOT evaluate the Riemann zeta function;
--   * it does NOT prove that any recorded `t` is a zero of zeta, nor that any
--     zero lies on the critical line Re(s) = 1/2;
--   * the records are numeric data only. The earlier header that advertised
--     "Riemann critical evidence" was an overclaim and has been removed.

import Mathlib.Data.Nat.Basic
import Mathlib.Tactic

namespace Math30.Riemann.CriticalEvidence

/-- A rational interval record `loNum/loDen ≤ hiNum/hiDen` with equal
    denominators. Historical name: the structure does not encode a zeta zero. -/
structure RationalIntervalRecord where
  loNum : ℕ
  loDen : ℕ
  hiNum : ℕ
  hiDen : ℕ
  h_valid : loNum * hiDen ≤ hiNum * loDen
  h_pos : loDen > 0
  h_eq_den : loDen = hiDen

/-- Decimal interval record near 14.13472514 (numeric data only). -/
def intervalRecord1 : RationalIntervalRecord := {
  loNum := 1413472514
  loDen := 100000000
  hiNum := 1413472518
  hiDen := 100000000
  h_valid := by decide
  h_pos := by decide
  h_eq_den := by decide
}

/-- Decimal interval record near 21.02203964 (numeric data only). -/
def intervalRecord2 : RationalIntervalRecord := {
  loNum := 2102203964
  loDen := 100000000
  hiNum := 2102203968
  hiDen := 100000000
  h_valid := by decide
  h_pos := by decide
  h_eq_den := by decide
}

/-- Every rational interval record has ordered endpoints. This is a projection
    of the structure field `h_valid`, not a statement about zeta zeros. -/
theorem rational_interval_ordered (z : RationalIntervalRecord) :
    z.loNum ≤ z.hiNum := by
  have hv := z.h_valid
  have hd := z.h_eq_den
  rw [hd] at hv
  have h_hi_pos : z.hiDen > 0 := by rw [← hd]; exact z.h_pos
  exact Nat.le_of_mul_le_mul_right hv h_hi_pos

end Math30.Riemann.CriticalEvidence

#print axioms Math30.Riemann.CriticalEvidence.rational_interval_ordered
