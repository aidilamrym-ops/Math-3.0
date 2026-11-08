; Phase 4 / Gate 4: Ramsey R(3,3) degree-cap pigeonhole.
;
; Six vertices of K6.  Each carries at most 2 red edges, so the red degrees
; r1..r6 are capped at 2.  A total red degree of 13 would need at least 7 red
; edges (handshake: total red degree = 2 * #red edges), which six vertices of
; capacity 2 cannot supply.
;
; The claim refuted is the last assertion.  Its refutation needs ALL SIX caps:
; no single cap, and no pair of caps, contradicts a total of 13.  That is what
; makes this a pigeonhole and not a restatement.
(set-logic QF_LIA)
(set-option :produce-models true)
(declare-const r1 Int)
(declare-const r2 Int)
(declare-const r3 Int)
(declare-const r4 Int)
(declare-const r5 Int)
(declare-const r6 Int)
(assert (<= 0 r1))
(assert (<= 0 r2))
(assert (<= 0 r3))
(assert (<= 0 r4))
(assert (<= 0 r5))
(assert (<= 0 r6))
(assert (<= r1 2))
(assert (<= r2 2))
(assert (<= r3 2))
(assert (<= r4 2))
(assert (<= r5 2))
(assert (<= r6 2))
(assert (>= (+ r1 r2 r3 r4 r5 r6) 13))
(check-sat)
