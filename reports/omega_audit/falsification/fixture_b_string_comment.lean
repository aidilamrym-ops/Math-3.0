/-
OMEGA falsification fixture B.

A Lean string literal containing the comment opener `/-` is not a comment.
gate.py does not parse string literals; it enters comment depth 1 here and
blanks the remainder of the file. A real `sorry` after this line must then
be invisible to the gate.
-/
def omega_note : String := "/-"

theorem omega_string_evasion : False := sorry
