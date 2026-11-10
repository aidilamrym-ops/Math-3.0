/-
OMEGA falsification fixture D.

An attribute before `axiom` also moves `axiom` off the line start, so the
`^[ \t]*axiom` pattern must miss it while Lean still accepts the axiom.
-/
@[simp] axiom omega_attributed_cheat : False

theorem omega_attributed_thm : False := omega_attributed_cheat
