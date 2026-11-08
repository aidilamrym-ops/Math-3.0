import Init.Data.Nat.Basic
import Mathlib.Tactic

namespace Math30.Evolution.UniversalContraction

def contractStep (x : Nat) : Nat := if x > 0 then x / 2 else 0

theorem convergence_bounded (x : Nat) (hx : x ≤ 10) :
    contractStep (contractStep (contractStep (contractStep (contractStep (contractStep (contractStep (contractStep (contractStep (contractStep x))))))))) = 0 := by
  interval_cases x <;> rfl

end Math30.Evolution.UniversalContraction
