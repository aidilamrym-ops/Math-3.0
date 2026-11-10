/-
OMEGA control fixture: a plain `axiom` at the start of a line. The strict
gate must return FAIL.
-/
axiom omega_plain_axiom : False

theorem omega_plain_axiom_thm : False := omega_plain_axiom
