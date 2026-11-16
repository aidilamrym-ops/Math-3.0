-- HorizonFrontierTests.lean
-- Math 3.0 regression fixtures for finite models.
--
-- Scope:
--   * the quotient pushout construction of S¹ as the identification of two
--     points of `Bool`, together with its path constructor;
--   * the degree-map algebra on ℤ for affine maps;
--   * the finite Freudenthal stable-range inequality `n + 1 < k → n + k < 2k`;
--   * one finite bulk-edge arithmetic model.
--
-- Claim limits:
--   * this is NOT a computation of π_n(S^k), not a synthetic homotopy type
--     theory development, and not a sheaf/topos formalization;
--   * `HomotopyGroup n Unit` is definitionally ℤ; the equivalence results in
--     `DecidableHomotopySphere.lean` are model-level identities, not the
--     topological Hurewicz isomorphism;
--   * physics labels name finite arithmetic models only.

import Mathlib.Data.Int.Basic
import Mathlib.Tactic

-- Test 1: Quotient pushout and the circle S¹ as a point-type scaffold.
namespace TestHigherInductive

/-- Homotopy pushout of f : A → B and g : A → C. -/
inductive PushoutRaw (A B C : Type) (f : A → B) (g : A → C)
  | inl : B → PushoutRaw A B C f g
  | inr : C → PushoutRaw A B C f g

/-- Gluing relation for the pushout: inl (f a) ~ inr (g a). -/
inductive PushoutRel {A B C : Type} (f : A → B) (g : A → C) :
    PushoutRaw A B C f g → PushoutRaw A B C f g → Prop
  | glue (a : A) : PushoutRel f g (PushoutRaw.inl (f a)) (PushoutRaw.inr (g a))

/-- The higher inductive pushout type. -/
def Pushout {A B C : Type} (f : A → B) (g : A → C) :=
  Quot (PushoutRel f g)

namespace Pushout

def inl {A B C : Type} {f : A → B} {g : A → C} (b : B) : Pushout f g :=
  Quot.mk (PushoutRel f g) (PushoutRaw.inl b)

def inr {A B C : Type} {f : A → B} {g : A → C} (c : C) : Pushout f g :=
  Quot.mk (PushoutRel f g) (PushoutRaw.inr c)

theorem glue {A B C : Type} {f : A → B} {g : A → C} (a : A) :
    (inl (f a) : Pushout f g) = inr (g a) :=
  Quot.sound (PushoutRel.glue a)

def S1 := Pushout (fun _ : Bool => ()) (fun _ : Bool => ())

def base : S1 := inl ()

theorem loop : base = inr () := glue true

theorem loop_alt : base = inr () := glue false

/-- Path induction for the equality relation: transport a reflexive binary
    relation along an identification. -/
theorem path_induction {X : Type} (P : X → X → Prop)
    (refl : ∀ x, P x x) (x y : X) (p : x = y) : P x y := by
  subst p
  apply refl

end Pushout

open Pushout

/-- The quotient identification is inhabited by the path constructor. -/
theorem circle_loop_exists : base = inr () := loop

end TestHigherInductive

-- Test 3: degree-map algebra and the finite Freudenthal range.
namespace TestHomotopySphere

/-- A model of the n-th homotopy group, definitionally ℤ. -/
def HomotopyGroup (_n : ℕ) (_X : Type) := ℤ

/-- The degree-map invariant for affine maps on ℤ. -/
def degreeMap (f : ℤ → ℤ) : ℤ := f 1 - f 0

theorem degreeMap_id : degreeMap id = 1 := by
  simp [degreeMap]

theorem degreeMap_const (c : ℤ) : degreeMap (fun _ => c) = 0 := by
  simp [degreeMap]

theorem degreeMap_linear (a : ℤ) : degreeMap (fun x => a * x) = a := by
  simp [degreeMap]

/-- The degree of a translated linear map is unchanged. -/
theorem degreeMap_affine (a c : ℤ) : degreeMap (fun x => a * x + c) = a := by
  simp [degreeMap]

theorem degree_map_computation : degreeMap (fun x : ℤ => 2 * x) = 2 := by
  simp [degreeMap]

/-- Finite Freudenthal stable range: `n + 1 < k` implies `n + k < 2k`. -/
theorem freudenthal_stability_bound (n k : ℕ) (h : n + 1 < k) :
    n + k < k + k := by
  omega

theorem freudenthal_bound_test (n k : ℕ) (h : n + 1 < k) :
    n + k < k + k :=
  freudenthal_stability_bound n k h

/-- The stable range is non-empty: `(n, k) = (1, 3)`. -/
theorem freudenthal_stable_witness :
    ∃ n k : ℕ, n + 1 < k ∧ n + k < k + k := by
  refine ⟨1, 3, by norm_num, ?_⟩
  omega

end TestHomotopySphere

-- Finite bulk-edge arithmetic model.
namespace TestPhysicsApplication

open TestHomotopySphere

/-- Finite model: the number of edge modes is the absolute difference of the
    two integer labels. The two evaluations are concrete sanity checks. -/
theorem bulk_edge_correspondence :
    ∃ (edge_modes : ℤ → ℤ → ℕ),
      (∀ (c1 c2 : ℤ), edge_modes c1 c2 = (c1 - c2).natAbs) ∧
      edge_modes 2 0 = 2 ∧
      edge_modes 1 0 = 1 := by
  refine ⟨fun c1 c2 => (c1 - c2).natAbs, ?_, ?_, ?_⟩
  · intro c1 c2; rfl
  · norm_num
  · norm_num

end TestPhysicsApplication

#print axioms TestHigherInductive.circle_loop_exists
#print axioms TestHomotopySphere.freudenthal_stability_bound
#print axioms TestPhysicsApplication.bulk_edge_correspondence
