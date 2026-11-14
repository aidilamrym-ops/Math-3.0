; Gate 5 Rational Leakage Refutation SMT-LIB2 Bounded Model
; QF_NRA check that an extracted rational cannot simultaneously stay strictly
; inside the half-unit contraction bound and leak at or beyond it.
;
; Safety property (exact extraction):     den > 0  and  2*|num| <  den
; Leakage assumption (its negation):      den > 0  and  2*|num| >= den
; The conjunction is unsatisfiable, so no rational surviving the extraction
; bound can leak past it.
(set-logic QF_NRA)
(declare-const num Real)
(declare-const den Real)
(assert (> den 0.0))
(assert (< (* 2.0 (abs num)) den))
(assert (>= (* 2.0 (abs num)) den))
(check-sat)
