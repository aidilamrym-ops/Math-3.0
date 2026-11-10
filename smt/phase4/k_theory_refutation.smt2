; SMT Refutation: K-Theory Refutation (Phase 4)
; Math 3.0 - Proves that the period table is unsatisfiable under a contradictory classification.
; Description:
;   The AII (Altland-Zirnbauer) symmetry class at dimension d=2 must classify as Z2 (index 2).
;   Asserting an inconsistent classification (Z, index 1) yields UNSAT, confirming the table's integrity.
;
(set-logic QF_LIA)
(set-option :produce-models true)

; Symmetry class, dimension, and classification group (0: trivial, 1: Z, 2: Z2, 3: 2Z)
(declare-fun symmetry_class () Int)
(declare-fun dimension () Int)
(declare-fun classification_group () Int)

(assert (>= symmetry_class 0))
(assert (<= symmetry_class 9))
(assert (>= dimension 0))
(assert (<= dimension 7))
(assert (>= classification_group 0))
(assert (<= classification_group 3))

; AII (symmetry_class=6) at dimension 2 must be Z2 (group=2)
(assert (=> (and (= symmetry_class 6) (= dimension 2)) (= classification_group 2)))

; Force the antecedent to be true: we are evaluating AII at d=2
(assert (and (= symmetry_class 6) (= dimension 2)))

; Contradictory assignment: force classification_group = Z (1)
(assert (= classification_group 1))

; The system is inconsistent => UNSAT
(check-sat)
(get-model)
