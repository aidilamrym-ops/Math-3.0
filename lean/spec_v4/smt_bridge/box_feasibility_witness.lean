import Init.Data.Rat.Basic
import Mathlib.Tactic

namespace Math30.SMTBridge

theorem box_feasibility_witness_sat_witness :
  ((((13.325072930817287 : Rat) ≤ (14.686140661634507 : Rat)) ∧ ((14.686140661634507 : Rat) ≤ (16.04720839245173 : Rat)))) ∧
  (((14.686140661634507 : Rat) = (14.686140661634507 : Rat))) ∧
  ((((10.409477555590692 : Rat) ≤ (11.813859338365493 : Rat)) ∧ ((11.813859338365493 : Rat) ≤ (13.218241121140293 : Rat)))) ∧
  (((11.813859338365493 : Rat) = (11.813859338365493 : Rat))) ∧
  ((((11.068653927850544 : Rat) ≤ (12.5 : Rat)) ∧ ((12.5 : Rat) ≤ (13.931346072149456 : Rat)))) ∧
  (((12.5 : Rat) = (12.5 : Rat))) ∧
  (((0.14223641401884418 : Rat) = (0.14223641401884418 : Rat))) ∧
  (((2 : Rat) * (0.14223641401884418 : Rat) < (1 : Rat))) ∧
  (((0.1836129694132613 : Rat) = (0.1836129694132613 : Rat))) ∧
  (((2 : Rat) * (0.1836129694132613 : Rat) < (1 : Rat))) ∧
  (((0.17667853244575302 : Rat) = (0.17667853244575302 : Rat))) ∧
  (((2 : Rat) * (0.17667853244575302 : Rat) < (1 : Rat))) := by
  constructor
  · constructor <;> norm_num
  · constructor
    · rfl
    · constructor
      · constructor <;> norm_num
      · constructor
        · rfl
        · constructor
          · constructor <;> norm_num
          · constructor
            · rfl
            · constructor
              · rfl
              · constructor
                · norm_num
                · constructor
                  · rfl
                  · constructor
                    · norm_num
                    · constructor
                      · rfl
                      · norm_num

#print axioms box_feasibility_witness_sat_witness

end Math30.SMTBridge
