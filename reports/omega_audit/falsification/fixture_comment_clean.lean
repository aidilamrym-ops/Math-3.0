/-
OMEGA control fixture: the words sorry, admit, and axiom appear only inside
comments. The strict gate must return PASS because comments are blanked
before the scan.
-/
-- A comment may discuss sorry, admit, and axiom without using them.
theorem omega_comment_clean : 2 + 2 = 4 := by decide
