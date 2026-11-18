/-
OMEGA falsification fixture I.

An unterminated ordinary string literal is invalid Lean. A fail-closed gate
must report the lexical defect instead of blanking the remainder of the file
and hiding a trust token that follows.
-/
def omega_unterminated_note : String := "unterminated
theorem omega_hidden_sorry : False := sorry
