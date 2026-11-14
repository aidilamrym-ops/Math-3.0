; SMT-LIB2 Verification Script: Continuity Refutation in a Finite Lattice
; Logic: QF_LIA
;
; A continuous path that remains inside a finite lattice of size N can move at
; most one lattice unit per discrete step. It therefore cannot traverse N+1
; distinct states in at most N steps. The constraints below encode that
; discrete intermediate-value obstruction and are jointly unsatisfiable.

(set-logic QF_LIA)

(declare-const lattice_size Int)
(declare-const path_steps Int)
(declare-const path_span Int)

; A nonempty finite lattice.
(assert (> lattice_size 0))

; The discrete path is contained in the lattice: at most N unit transitions.
(assert (>= path_steps 0))
(assert (<= path_steps lattice_size))

; A continuous traversal that leaves the initial state must span at least N+1
; distinct lattice positions.
(assert (>= path_span (+ lattice_size 1)))

; Each unit step can increase the span by at most one lattice unit.
(assert (<= path_span path_steps))

(check-sat)
(exit)
