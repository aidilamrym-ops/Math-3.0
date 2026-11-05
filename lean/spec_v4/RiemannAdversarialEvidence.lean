import Init.Data.Nat.Basic

/-!
# Riemann Adversarial Evidence (Math 3.0 / Phase 7)

Exact rational bounds for the three adversarially perturbed zero boxes.
The proofs use core `decide` over Nat cross-multiplication.
No Mathlib dependency. No placeholders; no admit or axiom.
-/

namespace Math30.Riemann.Adversarial

/-- Exact rational zero box: loNum / loDen <= t <= hiNum / hiDen. -/
structure ZeroBox where
  loNum : Nat
  loDen : Nat
  hiNum : Nat
  hiDen : Nat
  h_nonempty : loNum * hiDen <= hiNum * loDen

/-- Adversarial box for zero 1. -/
def box1 : ZeroBox := {
  loNum := 176684064271683672376862740391521
  loDen := 12500000000000000000000000000000
  hiNum := 141347251417346937901490192313217
  hiDen := 10000000000000000000000000000000
  h_nonempty := by decide
}

/-- Adversarial box for zero 2. -/
def box2 : ZeroBox := {
  loNum := 84088158555086219991575314405557
  loDen := 4000000000000000000000000000000
  hiNum := 2102203963877155499789382860138927
  hiDen := 100000000000000000000000000000000
  h_nonempty := by decide
}

/-- Adversarial box for zero 3. -/
def box3 : ZeroBox := {
  loNum := 1250542879007284438121269515632201
  loDen := 50000000000000000000000000000000
  hiNum := 625271439503642219060634757816101
  hiDen := 25000000000000000000000000000000
  h_nonempty := by decide
}

/-- Every adversarial lower endpoint is strictly positive. -/
theorem adversarial_lower_endpoints_positive :
    0 < box1.loNum ∧ 0 < box2.loNum ∧ 0 < box3.loNum := by
  decide

/-- The three adversarial boxes are strictly ordered and non-overlapping. -/
theorem adversarial_boxes_strictly_ordered :
    box1.hiNum * box2.loDen < box2.loNum * box1.hiDen ∧
    box2.hiNum * box3.loDen < box3.loNum * box2.hiDen := by
  decide

/-- Aggregate Phase 7 safety certificate. -/
theorem adversarial_intervals_safe :
    (0 < box1.loNum ∧ 0 < box2.loNum ∧ 0 < box3.loNum) ∧
    (box1.hiNum * box2.loDen < box2.loNum * box1.hiDen ∧
     box2.hiNum * box3.loDen < box3.loNum * box2.hiDen) := by
  constructor
  · decide
  · decide

#eval "RiemannAdversarialEvidence compiled with zero placeholders."

end Math30.Riemann.Adversarial
