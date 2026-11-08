import Init.Data.Nat.Basic
import Mathlib.Tactic

namespace Math30.Collatz

def collatzStep (n : Nat) : Nat :=
  if n % 2 = 0 then n / 2 else 3 * n + 1

def collatzLoop (curr : Nat) : Nat → Bool
  | 0 => curr == 1
  | fuel + 1 => if curr == 1 then true else collatzLoop (collatzStep curr) fuel

def collatzReachesOne (n : Nat) (max_fuel : Nat) : Bool := collatzLoop n max_fuel

lemma collatzLoop_one (f : Nat) : collatzLoop 1 f = true := by
  induction f with
  | zero => rfl
  | succ f ih => rfl

lemma collatzLoop_mono (curr : Nat) (f1 f2 : Nat) (h : f1 ≤ f2) (eq1 : collatzLoop curr f1 = true) : collatzLoop curr f2 = true := by
  induction f1 generalizing curr f2 with
  | zero =>
    dsimp [collatzLoop] at eq1
    have h_curr : curr = 1 := by
      cases curr with
      | zero => contradiction
      | succ c => cases c with | zero => rfl | succ _ => contradiction
    subst h_curr
    exact collatzLoop_one f2
  | succ f1 ih =>
    match f2 with
    | 0 => cases h
    | f2 + 1 =>
      dsimp [collatzLoop] at eq1 ⊢
      split_ifs at eq1 ⊢ with h_eq
      · exact collatzLoop_one (f2 + 1)
      · exact ih (collatzStep curr) f2 (Nat.le_of_succ_le_succ h) eq1

theorem collatz_horizon_defeat (n : Nat) (hn : n ≥ 1) (hn_max : n ≤ 100) (max_fuel : Nat) (h_fuel : max_fuel ≥ 5000) :
    collatzReachesOne n max_fuel = true := by
  have h_base : collatzLoop n 5000 = true := by
    interval_cases n <;> decide
  exact collatzLoop_mono n 5000 max_fuel h_fuel h_base

#print axioms collatz_horizon_defeat

end Math30.Collatz
