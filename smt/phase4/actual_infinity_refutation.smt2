; SMT-LIB2 witness: finite-capacity actual-infinity obstruction.
; Logic: QF_LIA
;
; Concrete four-step instance of `actual_infinity_violates_conservation`
; (lean/spec_v4/ActualInfinityRefutation.lean).  A traversal starts at state 0
; and strictly increases by at least one unit per step.  With lattice capacity
; 3, the fourth state must be at least 4, so the traversal cannot remain inside
; the lattice.  The general parametric theorem is proved in Lean; this script
; is an executable finite instance, not a proof of the general theorem.

(set-logic QF_LIA)

(declare-const capacity Int)
(declare-const s0 Int)
(declare-const s1 Int)
(declare-const s2 Int)
(declare-const s3 Int)
(declare-const s4 Int)

; The finite lattice has capacity 3 and the traversal starts at state 0.
(assert (= capacity 3))
(assert (= s0 0))

; Each step must strictly increase the state index by at least one unit.
(assert (>= s1 (+ s0 1)))
(assert (>= s2 (+ s1 1)))
(assert (>= s3 (+ s2 1)))
(assert (>= s4 (+ s3 1)))

; Claim: every visited state stays inside the finite capacity.
(assert (<= s4 capacity))

(check-sat)
(exit)
