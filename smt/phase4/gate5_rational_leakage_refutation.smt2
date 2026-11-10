; Gate 5 Rational Leakage Refutation SMT-LIB2 Bounded Model
; QF_NRA check for floating-point approximation error boundary violation.
(set-logic QF_NRA)
(declare-const num Real)
(declare-const den Real)
(assert (> den 0.0))
(assert (>= (abs (/ num den)) 0.5))
(check-sat)
