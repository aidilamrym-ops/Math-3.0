; Phase 4 / Gate 3: Newton-box lower endpoints are strictly positive
; on the closed integer lattice [0, floor(lower*10^18)].
(set-logic QF_LIA)
(set-option :produce-models true)
(declare-const q0 Int)
(assert (and (<= 0 q0) (<= q0 248851580993501700)))
(declare-const q1 Int)
(assert (and (<= 0 q1) (<= q1 273647560508655000)))
(declare-const q2 Int)
(assert (and (<= 0 q2) (<= q2 266648880253153250)))
(assert (or (<= q0 0) (<= q1 0) (<= q2 0)))
(check-sat)
