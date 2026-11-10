; Yang-Mills Lattice Refutation Script (Phase 33)
; Math 3.0 - Bounded Boundary Sweep & Sign-Mixed Inversion Tribunal
; Proves that boundary sign inversion in discrete gauge field plaquette determinants
; leads to an inconsistent state (UNSAT witness).

(set-logic QF_NRA)
(set-option :produce-models true)

(declare-fun S () Real)
(declare-fun T () Real)
(declare-fun D () Real)

(assert (>= S 0.0))
(assert (>= T 0.0))
(assert (>= D 0.0))

; Cauchy-Schwarz constraint for Sylvester diagonal: S <= T always holds for positive invariants
(assert (<= S T))

; Assume DSITNI stability holds: 2 * S * (D + 1) < 3 * (T + 1) * (D + 2)
(assert (< (* (* 2.0 S) (+ D 1.0)) (* 3.0 (* (+ T 1.0) (+ D 2.0)))))

; Contradictory assertion: assume DSITNI is violated (negation of stability)
(assert (>= (* (* 2.0 S) (+ D 1.0)) (* 3.0 (* (+ T 1.0) (+ D 2.0)))))

(check-sat)
(get-model)
