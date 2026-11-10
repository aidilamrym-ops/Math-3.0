/-
OMEGA falsification fixture F.

`--` inside a Lean string literal is not a line comment. gate.py does not
parse string literals, so it blanks everything after the `--` on this line,
including a real `sorry` that Lean still elaborates.
-/
def omega_line_evasion : Nat := let _s := "a--b"; (sorry : Nat)
