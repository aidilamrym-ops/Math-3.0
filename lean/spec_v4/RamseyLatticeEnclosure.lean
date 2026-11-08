-- RamseyLatticeEnclosure.lean
-- Math 3.0 Finite Graph Ramsey Enclosure
-- Exact decidable adjacency matrices and probabilistic existence invariant bounds.

import Mathlib.Data.Fin.Basic
import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Interval
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Fintype.Card
import Mathlib.Combinatorics.Enumerative.DoubleCounting
import Mathlib.Tactic

namespace Math30.Ramsey

open SimpleGraph Fintype Finset

/-- Edge in a graph on n vertices represented as a 2-element Finset. -/
abbrev Edge (n : ℕ) := {S : Finset (Fin n) // S.card = 2}

/-- Finite graph as a Finset of edges. -/
abbrev FiniteGraph (n : ℕ) := Finset (Edge n)

/-- Inside edges of vertex subset S. -/
def inside (n : ℕ) (S : Finset (Fin n)) : Finset (Edge n) :=
  (S.powersetCard 2).attach.map
    ⟨fun T => ⟨T.1, (Finset.mem_powersetCard.mp T.2).2⟩, by
      intro a b h
      apply Subtype.ext
      have := congrArg (fun e : Edge n => e.val) h
      simpa using this⟩

lemma card_inside (n : ℕ) (S : Finset (Fin n)) :
    (inside n S).card = Nat.choose S.card 2 := by
  unfold inside
  rw [Finset.card_map, Finset.card_attach, Finset.card_powersetCard]

/-- Clique of size k exists. -/
def hasClique {n : ℕ} (g : FiniteGraph n) (k : ℕ) : Prop :=
  ∃ S : Finset (Fin n), S.card = k ∧ inside n S ⊆ g

/-- Independent set of size k exists. -/
def hasIndependentSet {n : ℕ} (g : FiniteGraph n) (k : ℕ) : Prop :=
  ∃ S : Finset (Fin n), S.card = k ∧ Disjoint (inside n S) g

/-- R(3,3) ≤ 6 constructive proof via degree pigeonhole on simple graphs. -/
theorem ramsey_R33 (G : SimpleGraph (Fin 6)) :
    (∃ s : Finset (Fin 6), G.IsNClique 3 s) ∨
    (∃ s : Finset (Fin 6), Gᶜ.IsNClique 3 s) := by
  classical
  let v : Fin 6 := 0
  let t := Finset.univ.erase v
  have ht_card : t.card = 5 := by simp [t]
  let A := t.filter (fun w => G.Adj v w)
  let B := t.filter (fun w => ¬ G.Adj v w)
  have hsum : A.card + B.card = 5 := by
    have h := Finset.card_filter_add_card_filter_not (s := t) (p := fun w => G.Adj v w)
    simpa [A, B, ht_card] using h
  have hsplit : 3 ≤ A.card ∨ 3 ≤ B.card := by omega
  rcases hsplit with hA | hB
  · obtain ⟨S, hSsub, hScard⟩ := Finset.exists_subset_card_eq (s := A) (n := 3) hA
    have hS : ∀ a ∈ S, a ∈ t ∧ G.Adj v a := by
      intro a ha
      have h := hSsub ha
      simpa [A] using h
    by_cases hedge : ∃ a ∈ S, ∃ b ∈ S, a ≠ b ∧ G.Adj a b
    · obtain ⟨a, ha, b, hb, hne, hadj⟩ := hedge
      exact Or.inl ⟨{v, a, b}, is3Clique_triple_iff.2 ⟨(hS a ha).2, (hS b hb).2, hadj⟩⟩
    · refine Or.inr ⟨S, (isNClique_iff (G := Gᶜ)).2 ⟨?_, hScard⟩⟩
      rw [isClique_iff]
      intro a ha b hb hne
      rw [compl_adj]
      have ha' : a ∈ S := by simpa using ha
      have hb' : b ∈ S := by simpa using hb
      exact ⟨hne, fun hadj => hedge ⟨a, ha', b, hb', hne, hadj⟩⟩
  · obtain ⟨S, hSsub, hScard⟩ := Finset.exists_subset_card_eq (s := B) (n := 3) hB
    have hS : ∀ a ∈ S, a ∈ t ∧ ¬ G.Adj v a := by
      intro a ha
      have h := hSsub ha
      simpa [B] using h
    by_cases hnon : ∃ a ∈ S, ∃ b ∈ S, a ≠ b ∧ ¬ G.Adj a b
    · obtain ⟨a, ha, b, hb, hne, hnab⟩ := hnon
      have hva : v ≠ a := by
        have := (hS a ha).1
        simp [t] at this
        exact Ne.symm this
      have hvb : v ≠ b := by
        have := (hS b hb).1
        simp [t] at this
        exact Ne.symm this
      exact Or.inr ⟨{v, a, b}, is3Clique_triple_iff.2
        ⟨by rw [compl_adj]; exact ⟨hva, (hS a ha).2⟩,
         by rw [compl_adj]; exact ⟨hvb, (hS b hb).2⟩,
         by rw [compl_adj]; exact ⟨hne, hnab⟩⟩⟩
    · refine Or.inl ⟨S, (isNClique_iff (G := G)).2 ⟨?_, hScard⟩⟩
      rw [isClique_iff]
      intro a ha b hb hne
      have ha' : a ∈ S := by simpa using ha
      have hb' : b ∈ S := by simpa using hb
      by_contra hnab
      exact hnon ⟨a, ha', b, hb', hne, hnab⟩

lemma card_edge (n : ℕ) : Fintype.card (Edge n) = Nat.choose n 2 := by
  rw [Fintype.card_subtype]
  have h : (Finset.filter (fun S : Finset (Fin n) => S.card = 2) Finset.univ)
      = Finset.powersetCard 2 (Finset.univ) := by
    rw [Finset.powersetCard_eq_filter, Finset.powerset_univ]
  rw [h, Finset.card_powersetCard, Finset.card_univ, Fintype.card_fin]

lemma card_supersets (n : ℕ) (I : Finset (Edge n)) :
    (Finset.univ.filter (fun g : FiniteGraph n => I ⊆ g)).card
      = 2 ^ (Fintype.card (Edge n) - I.card) := by
  classical
  have h : I ⊆ (Finset.univ : Finset (Edge n)) := Finset.subset_univ I
  have hfilter : Finset.univ.filter (fun g : FiniteGraph n => I ⊆ g)
      = Finset.Icc I (Finset.univ : Finset (Edge n)) := by
    ext g
    simp [Finset.mem_Icc]
  rw [hfilter, Finset.card_Icc_finset h]
  simp

lemma card_disjoint (n : ℕ) (I : Finset (Edge n)) :
    (Finset.univ.filter (fun g : FiniteGraph n => Disjoint I g)).card
      = 2 ^ (Fintype.card (Edge n) - I.card) := by
  classical
  have h : I ⊆ (Finset.univ : Finset (Edge n)) := Finset.subset_univ I
  have hfilter : Finset.univ.filter (fun g : FiniteGraph n => Disjoint I g)
      = (Finset.univ \ I).powerset := by
    ext g
    simp [Finset.mem_powerset, Finset.subset_sdiff, disjoint_comm]
  rw [hfilter, Finset.card_powerset, Finset.card_sdiff_of_subset h]
  simp

lemma card_mono_le (n : ℕ) (S : Finset (Fin n)) :
    (Finset.univ.filter (fun g : FiniteGraph n =>
        inside n S ⊆ g ∨ Disjoint (inside n S) g)).card
      ≤ 2 * 2 ^ (Fintype.card (Edge n) - (inside n S).card) := by
  classical
  let P : FiniteGraph n → Prop := fun g => inside n S ⊆ g
  let Q : FiniteGraph n → Prop := fun g => Disjoint (inside n S) g
  have hsub : Finset.univ.filter (fun g : FiniteGraph n => P g ∨ Q g)
      ⊆ (Finset.univ.filter P) ∪ (Finset.univ.filter Q) := by
    intro g hg
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hg ⊢
    rcases hg with h | h
    · exact Finset.mem_union_left _ (by simp [h])
    · exact Finset.mem_union_right _ (by simp [h])
  calc
    (Finset.univ.filter (fun g : FiniteGraph n =>
        inside n S ⊆ g ∨ Disjoint (inside n S) g)).card
        = (Finset.univ.filter (fun g : FiniteGraph n => P g ∨ Q g)).card := rfl
    _ ≤ ((Finset.univ.filter P) ∪ (Finset.univ.filter Q)).card := Finset.card_le_card hsub
    _ ≤ (Finset.univ.filter P).card + (Finset.univ.filter Q).card := Finset.card_union_le _ _
    _ = 2 ^ (Fintype.card (Edge n) - (inside n S).card)
          + 2 ^ (Fintype.card (Edge n) - (inside n S).card) := by
        rw [card_supersets, card_disjoint]
    _ = 2 * 2 ^ (Fintype.card (Edge n) - (inside n S).card) := by ring

lemma card_le_of_forall_mono (n k : ℕ) (_hk : 2 ≤ k) (_hkn : k ≤ n)
    (hmono : ∀ g : FiniteGraph n, hasClique g k ∨ hasIndependentSet g k) :
    Fintype.card (FiniteGraph n)
      ≤ Nat.choose n k * (2 * 2 ^ (Fintype.card (Edge n) - Nat.choose k 2)) := by
  classical
  let t : Finset (Finset (Fin n)) := Finset.powersetCard k (Finset.univ : Finset (Fin n))
  let r : FiniteGraph n → Finset (Fin n) → Prop :=
    fun g S => inside n S ⊆ g ∨ Disjoint (inside n S) g
  have hcard_s : (Finset.univ : Finset (FiniteGraph n)).card = Fintype.card (FiniteGraph n) :=
    Finset.card_univ
  have hcard_t : t.card = Nat.choose n k := by
    simp [t, Finset.card_powersetCard, Fintype.card_fin]
  have hm : ∀ g ∈ (Finset.univ : Finset (FiniteGraph n)), 1 ≤ (t.bipartiteAbove r g).card := by
    intro g _
    rcases hmono g with ⟨S, hS, hcl⟩ | ⟨S, hS, hind⟩
    · have hSt : S ∈ t := by
        simp only [t, Finset.mem_powersetCard]
        exact ⟨Finset.subset_univ S, hS⟩
      have hmem : S ∈ t.bipartiteAbove r g := by
        simp only [Finset.mem_bipartiteAbove, hSt, true_and, r]
        exact Or.inl hcl
      exact Finset.card_pos.mpr ⟨S, hmem⟩
    · have hSt : S ∈ t := by
        simp only [t, Finset.mem_powersetCard]
        exact ⟨Finset.subset_univ S, hS⟩
      have hmem : S ∈ t.bipartiteAbove r g := by
        simp only [Finset.mem_bipartiteAbove, hSt, true_and, r]
        exact Or.inr hind
      exact Finset.card_pos.mpr ⟨S, hmem⟩
  have hn : ∀ S ∈ t, ((Finset.univ : Finset (FiniteGraph n)).bipartiteBelow r S).card
      ≤ 2 * 2 ^ (Fintype.card (Edge n) - Nat.choose k 2) := by
    intro S hS
    have hScard : S.card = k := (Finset.mem_powersetCard.mp hS).2
    have hbelow : (Finset.univ : Finset (FiniteGraph n)).bipartiteBelow r S
        = Finset.univ.filter (fun g : FiniteGraph n =>
            inside n S ⊆ g ∨ Disjoint (inside n S) g) := by
      ext g
      simp [Finset.mem_bipartiteBelow, r]
    rw [hbelow]
    have hle := card_mono_le n S
    rwa [card_inside, hScard] at hle
  have hmain := Finset.card_mul_le_card_mul (s := (Finset.univ : Finset (FiniteGraph n)))
    (t := t) (r := r) (m := 1)
    (n := 2 * 2 ^ (Fintype.card (Edge n) - Nat.choose k 2)) hm hn
  rw [hcard_s, hcard_t] at hmain
  simpa using hmain

/-- Erdős probabilistic existence invariant (counting bound bridge). -/
theorem ramsey_probabilistic_existence_invariant
    (n k : ℕ) (hk : 2 ≤ k) (hkn : k ≤ n)
    (h_avg : (Nat.choose n k : ℝ) * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) < 1/2) :
    ∃ (g : FiniteGraph n), ¬ hasClique g k ∧ ¬ hasIndependentSet g k := by
  classical
  by_contra h_all
  have h_mono : ∀ g : FiniteGraph n, hasClique g k ∨ hasIndependentSet g k := by
    intro g
    by_contra h_not
    push Not at h_not
    exact h_all ⟨g, h_not.1, h_not.2⟩
  have h_bound := card_le_of_forall_mono n k hk hkn h_mono
  have h_fintype : Fintype.card (FiniteGraph n) = 2 ^ Fintype.card (Edge n) := by
    simp [FiniteGraph]
  have h_card_edge := card_edge n
  rw [h_fintype, h_card_edge] at h_bound
  have h_choose_le : Nat.choose k 2 ≤ Nat.choose n 2 := by
    exact Nat.choose_mono 2 hkn
  have h_sub : 2 ^ (Nat.choose n 2) = 2 ^ (Nat.choose n 2 - Nat.choose k 2) * 2 ^ (Nat.choose k 2) := by
    rw [← pow_add, Nat.sub_add_cancel h_choose_le]
  rw [h_sub] at h_bound
  have h_bound_real : (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) * (2 : ℝ) ^ (Nat.choose k 2) ≤
      (Nat.choose n k : ℝ) * (2 * (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2)) := by
    exact_mod_cast h_bound
  have h_pow_pos : (0 : ℝ) < (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) := by positivity
  have h_div : (2 : ℝ) ^ (Nat.choose k 2) ≤ (Nat.choose n k : ℝ) * 2 := by
    rcases le_or_gt ((2 : ℝ) ^ (Nat.choose k 2)) ((Nat.choose n k : ℝ) * 2) with h_goal | h_wrong
    · exact h_goal
    · have h_m1 : (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) * (2 : ℝ) ^ (Nat.choose k 2) >
        (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) * ((Nat.choose n k : ℝ) * 2) := by
        gcongr
      have h_m2 : (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) * ((Nat.choose n k : ℝ) * 2) =
        (Nat.choose n k : ℝ) * (2 * (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2)) := by ring
      have h_m3 : (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2) * (2 : ℝ) ^ (Nat.choose k 2) >
        (Nat.choose n k : ℝ) * (2 * (2 : ℝ) ^ (Nat.choose n 2 - Nat.choose k 2)) := by
        linarith [h_m1, h_m2]
      linarith [h_bound_real, h_m3]
  have h_final : (1 : ℝ) ≤ (Nat.choose n k : ℝ) * 2 * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) := by
    calc
      (1 : ℝ) = (2 : ℝ) ^ (Nat.choose k 2) * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) := by
        have : (2 : ℝ) ^ (Nat.choose k 2) * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) = ((2 : ℝ) * (2 : ℝ)⁻¹) ^ (Nat.choose k 2) := by
          exact (mul_pow 2 (2 : ℝ)⁻¹ (Nat.choose k 2)).symm
        rw [this, mul_inv_cancel₀ (by norm_num), one_pow]
      _ ≤ ((Nat.choose n k : ℝ) * 2) * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) := by
        have h_inv_pos : (0 : ℝ) ≤ (2 : ℝ)⁻¹ ^ (Nat.choose k 2) := by positivity
        exact mul_le_mul_of_nonneg_right h_div h_inv_pos
      _ = (Nat.choose n k : ℝ) * 2 * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) := by ring
  have h_absurd : (Nat.choose n k : ℝ) * 2 * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) < 1 := by
    have h_rew : (Nat.choose n k : ℝ) * 2 * (2 : ℝ)⁻¹ ^ (Nat.choose k 2) = 2 * ((Nat.choose n k : ℝ) * (2 : ℝ)⁻¹ ^ (Nat.choose k 2)) := by ring
    rw [h_rew]
    linarith [h_avg]
  linarith [h_final, h_absurd]

#print axioms ramsey_R33
#print axioms ramsey_probabilistic_existence_invariant

end Math30.Ramsey
