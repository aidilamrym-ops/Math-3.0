import Mathlib.Data.Int.Basic
import Mathlib.Algebra.Group.Equiv.Basic
import Mathlib.Tactic
#synth AddMonoid ℤ
#check (AddEquiv.refl ℤ : ℤ ≃+ ℤ)
def HG (_n : ℕ) (_X : Type) := ℤ
#check (AddEquiv.refl ℤ : HG 1 Unit ≃+ ℤ)
