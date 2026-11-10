; Twistor Googly Refutation SMT-LIB2 Bounded Model
; QF_NRA check for helicity bound breakdown under sign-mixed conditions.
(set-logic QF_NRA)
(declare-const s Real)
(declare-const d Real)
(assert (>= s 0.0))
(assert (>= d 0.0))
(assert (not (< (* 2.0 s (+ d 1.0)) (* 3.0 (+ s 1.0) (+ d 2.0)))))
(check-sat)
