/-
OMEGA falsification fixture E.

`sorryAx` is the trusted axiom that `sorry` elaborates to. gate.py's
placeholder table contains `sorry` but not `sorryAx`; `\bsorry\b` does not
match inside `sorryAx` because the next character is a word character.
-/
theorem omega_sorryax_evasion : False := @sorryAx False true
