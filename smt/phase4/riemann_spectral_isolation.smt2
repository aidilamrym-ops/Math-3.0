; Phase 4 / Riemann Spectral Isolation
(set-logic QF_NRA)
(declare-const t Real)
(assert (>= t 0))
(assert (not (>= (* t t) 0)))
(check-sat)
