; Phase 4 / Gate 3: no sign flip inside the three certified eigenvalue boxes.
; Variables are eigenvalue numerators on the closed lattice e/10^18.
(set-logic QF_LIA)
(set-option :produce-models true)
(declare-const e0 Int)
(assert (and (<= 13325072930817286000 e0) (<= e0 16047208392451728000)))
(declare-const e1 Int)
(assert (and (<= 10409477555590692000 e1) (<= e1 13218241121140294000)))
(declare-const e2 Int)
(assert (and (<= 11068653927850545000 e2) (<= e2 13931346072149455000)))
(assert (or (<= e0 0) (<= e1 0) (<= e2 0)))
(check-sat)
