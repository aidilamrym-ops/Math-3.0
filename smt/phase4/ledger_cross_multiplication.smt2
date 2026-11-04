; Phase 4 / Gate 3: exact rational ledger cross-multiplication.
; Refutes any contraction >= 1/2 or non-positive box lower endpoint.
(set-logic QF_LIA)
(assert (> 50000000000000000 0))
(assert (> 10000000000000000 0))
(assert (> 10000000000000000 0))
(assert (> 200000000000000 0))
(assert (> 50000000000000000 0))
(assert (> 4000000000000000 0))
(assert (or (>= (* 2 7111820700942209) 50000000000000000) (<= 2488515809935017 0) (>= (* 2 1836129694132613) 10000000000000000) (<= 54729512101731 0) (>= (* 2 8833926622287651) 50000000000000000) (<= 1066595521012613 0)))
(check-sat)
