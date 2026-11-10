/-
OMEGA falsification fixture C.

`private axiom` is still an axiom declaration. gate.py anchors the axiom
pattern to the line start (`^[ \t]*axiom`), so a modifier before `axiom`
evades the scan.
-/
private axiom omega_private_cheat : False

theorem omega_private_thm : False := omega_private_cheat
