; Phase 4 / Gate 3: every contraction numerator on the closed lattice
; [0, ceil(max_ratio*10^18)] stays strictly below 1/2.
(set-logic QF_LIA)
(set-option :produce-models true)
(declare-const c0 Int)
(assert (and (<= 0 c0) (<= c0 142236414018844185)))
(declare-const c1 Int)
(assert (and (<= 0 c1) (<= c1 183612969413261292)))
(declare-const c2 Int)
(assert (and (<= 0 c2) (<= c2 176678532445753015)))
(assert (or (>= (* 2 c0) 1000000000000000000) (>= (* 2 c1) 1000000000000000000) (>= (* 2 c2) 1000000000000000000)))
(check-sat)
