-- ErdosSzekeresRamsey.lean
-- Math 3.0 / Phase 49: Finite pigeonhole, the length-2 Erdos-Szekeres instance,
-- and the parameterized Ramsey bound R(3,3) ≤ 6.
-- Scope:
--   * the finite pigeonhole principle (via Mathlib);
--   * the smallest Erdos-Szekeres case k = l = 2;
--   * R(3,3) ≤ 6 in parameterized form: for an arbitrary Bool-coloring
--     `c : Fin 6 → Fin 6 → Bool` of the ordered vertex pairs of `Fin 6`, there
--     are three distinct vertices `a b d` with `c a b = c a d = c b d`. For a
--     symmetric coloring this is exactly the edge-coloring statement of
--     R(3,3) ≤ 6; the proof does not use symmetry, so it holds for arbitrary
--     colorings.
-- Claim limits:
--   * this file does NOT prove the full Erdos-Szekeres or Ramsey theorems;
--   * no fixed coloring instance is certified here; the theorem ranges over
--     all colorings of `Fin 6`.

import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Data.Finset.Card
import Mathlib.Tactic

namespace Math30.Combinatorics.Finite

/-- Finite pigeonhole principle: more pigeons than holes forces a collision. -/
theorem pigeonhole_finite {α β : Type*} [Fintype α] [Fintype β]
    (f : α → β) (h : Fintype.card β < Fintype.card α) :
    ∃ x y, x ≠ y ∧ f x = f y :=
  Fintype.exists_ne_map_eq_of_card_lt f h

/-- Erdos-Szekeres smallest case: any two distinct naturals are comparable, hence
admit a monotone subsequence of length two. -/
theorem erdos_szekeres_pair (a b : ℕ) (hne : a ≠ b) :
    a < b ∨ b < a :=
  lt_or_gt_of_ne hne

/-- A two-coloring of a single edge always has a monochromatic representative. -/
theorem ramsey_one_edge (c : Fin 1 → Fin 2) :
    ∃ e : Fin 1, c e = 0 ∨ c e = 1 := by
  refine ⟨0, ?_⟩
  have hval : (c 0).val = 0 ∨ (c 0).val = 1 := by
    have hlt : (c 0).val < 2 := (c 0).isLt
    omega
  rcases hval with h0 | h1
  · left
    exact Fin.eq_of_val_eq (by simpa using h0)
  · right
    exact Fin.eq_of_val_eq (by simpa using h1)

/-- Every 3-element Finset contains three pairwise distinct elements. -/
private lemma exists_three_distinct {α : Type*} [DecidableEq α] {s : Finset α}
    (hs : s.card = 3) :
    ∃ a ∈ s, ∃ b ∈ s, ∃ d ∈ s, a ≠ b ∧ a ≠ d ∧ b ≠ d := by
  have hne : s ≠ ∅ := by
    intro h
    simp [h] at hs
  obtain ⟨a, ha⟩ := Finset.nonempty_iff_ne_empty.mpr hne
  have h2 : (s.erase a).card = 2 := by
    have hce := Finset.card_erase_of_mem ha
    omega
  have hne2 : s.erase a ≠ ∅ := by
    intro h
    simp [h] at h2
  obtain ⟨b, hb⟩ := Finset.nonempty_iff_ne_empty.mpr hne2
  have h3 : ((s.erase a).erase b).card = 1 := by
    have hce := Finset.card_erase_of_mem hb
    omega
  have hne3 : (s.erase a).erase b ≠ ∅ := by
    intro h
    simp [h] at h3
  obtain ⟨d, hd⟩ := Finset.nonempty_iff_ne_empty.mpr hne3
  have hbs : b ∈ s := (Finset.mem_erase.mp hb).2
  have hds : d ∈ s.erase a := (Finset.mem_erase.mp hd).2
  have hds' : d ∈ s := (Finset.mem_erase.mp hds).2
  refine ⟨a, ha, b, hbs, d, hds', ?_, ?_, ?_⟩
  · exact (Finset.mem_erase.mp hb).1.symm
  · exact (Finset.mem_erase.mp hds).1.symm
  · exact (Finset.mem_erase.mp hd).1.symm

/-- A Bool value is either `k` or its complement `!k`. -/
private lemma bool_dichotomy (v k : Bool) : v = k ∨ v = !k := by
  cases v <;> cases k <;> simp

/-- Pigeonhole at vertex `0`: among the five other vertices of `Fin 6`, three
are joined to `0` by pairs of one common color. -/
private lemma exists_three_same_neighbors (c : Fin 6 → Fin 6 → Bool) :
    ∃ k : Bool, ∃ a b d : Fin 6, a ≠ 0 ∧ b ≠ 0 ∧ d ≠ 0 ∧ a ≠ b ∧ a ≠ d ∧ b ≠ d ∧
      c 0 a = k ∧ c 0 b = k ∧ c 0 d = k := by
  classical
  set N : Finset (Fin 6) := Finset.univ.erase 0 with hN
  have hNcard : N.card = 5 := by simp [hN]
  set R : Finset (Fin 6) := N.filter (fun x => c 0 x = true) with hR
  set B : Finset (Fin 6) := N.filter (fun x => c 0 x = false) with hB
  have hRmem : ∀ v ∈ R, v ∈ N ∧ c 0 v = true := fun v hv => Finset.mem_filter.mp hv
  have hBmem : ∀ v ∈ B, v ∈ N ∧ c 0 v = false := fun v hv => Finset.mem_filter.mp hv
  have hunion : R ∪ B = N := by
    ext x
    simp only [Finset.mem_union, Finset.mem_filter, hR, hB, hN, Finset.mem_erase]
    cases h : c 0 x <;> simp
  have hdisj : Disjoint R B := by
    refine Finset.disjoint_left.mpr fun x hxR hxB => ?_
    have hxR' := Finset.mem_filter.mp hxR
    have hxB' := Finset.mem_filter.mp hxB
    cases h : c 0 x
    · exact absurd hxR'.2 (by rw [h]; simp)
    · exact absurd hxB'.2 (by rw [h]; simp)
  have hcount : R.card + B.card = N.card := by
    rw [← Finset.card_union_of_disjoint hdisj, hunion]
  have h3 : 3 ≤ R.card ∨ 3 ≤ B.card := by omega
  have hnonzero : ∀ v : Fin 6, v ∈ N → v ≠ 0 := fun v hv =>
    (Finset.mem_erase.mp hv).1
  have main : ∀ (S : Finset (Fin 6)) (k : Bool),
      (∀ v, v ∈ S → v ∈ N ∧ c 0 v = k) → 3 ≤ S.card →
      ∃ a b d : Fin 6, a ≠ 0 ∧ b ≠ 0 ∧ d ≠ 0 ∧ a ≠ b ∧ a ≠ d ∧ b ≠ d ∧
        c 0 a = k ∧ c 0 b = k ∧ c 0 d = k := by
    intro S k hS hS3
    obtain ⟨s, hsS, hsc⟩ := Finset.exists_subset_card_eq hS3
    obtain ⟨a, ha, b, hb, d, hd, hab, had, hbd⟩ := exists_three_distinct hsc
    refine ⟨a, b, d, hnonzero a (hS a (hsS ha)).1, hnonzero b (hS b (hsS hb)).1,
      hnonzero d (hS d (hsS hd)).1, hab, had, hbd, (hS a (hsS ha)).2,
      (hS b (hsS hb)).2, (hS d (hsS hd)).2⟩
  rcases h3 with hR3 | hB3
  · exact ⟨true, main R true hRmem hR3⟩
  · exact ⟨false, main B false hBmem hB3⟩

/-- **R(3,3) ≤ 6**, parameterized: every Bool-coloring `c` of the ordered pairs
of `Fin 6` contains a monochromatic triangle — three distinct vertices `a b d`
with `c a b = c a d = c b d`. For a symmetric coloring this is the classical
edge-coloring statement. -/
theorem ramsey_K6_mono_triangle (c : Fin 6 → Fin 6 → Bool) :
    ∃ a b d : Fin 6, a ≠ b ∧ a ≠ d ∧ b ≠ d ∧ c a b = c a d ∧ c a d = c b d := by
  obtain ⟨k, x, y, z, hx0, hy0, hz0, hxy, hxz, hyz, hxk, hyk, hzk⟩ :=
    exists_three_same_neighbors c
  by_cases hmut : c x y = k ∨ c x z = k ∨ c y z = k
  · rcases hmut with h | h | h
    · exact ⟨0, x, y, Ne.symm hx0, Ne.symm hy0, hxy, hxk.trans hyk.symm,
        hyk.trans h.symm⟩
    · exact ⟨0, x, z, Ne.symm hx0, Ne.symm hz0, hxz, hxk.trans hzk.symm,
        hzk.trans h.symm⟩
    · exact ⟨0, y, z, Ne.symm hy0, Ne.symm hz0, hyz, hyk.trans hzk.symm,
        hzk.trans h.symm⟩
  · have fy : c x y = !k := by
      rcases bool_dichotomy (c x y) k with e | e
      · exact absurd e (fun hc => hmut (Or.inl hc))
      · exact e
    have fz : c x z = !k := by
      rcases bool_dichotomy (c x z) k with e | e
      · exact absurd e (fun hc => hmut (Or.inr (Or.inl hc)))
      · exact e
    have fw : c y z = !k := by
      rcases bool_dichotomy (c y z) k with e | e
      · exact absurd e (fun hc => hmut (Or.inr (Or.inr hc)))
      · exact e
    exact ⟨x, y, z, hxy, hxz, hyz, by rw [fy, fz], by rw [fz, fw]⟩

#print axioms pigeonhole_finite
#print axioms ramsey_K6_mono_triangle

end Math30.Combinatorics.Finite
