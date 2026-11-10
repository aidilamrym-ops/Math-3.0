/-
OMEGA falsification fixture A.

`constant` is Lean 4's synonym for `axiom`. gate.py's placeholder table
only matches the literal token `axiom` as the first token on a line, so it
must miss this trust extension.
-/
constant omega_cheat : False

theorem omega_cheat_thm : False := omega_cheat
