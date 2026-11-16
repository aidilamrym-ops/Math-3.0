-- HomotopyAlgebraLattice.lean
-- Math 3.0: equality paths on the finite information lattice.
--
-- Scope:
--   * `Path A a b` is definitionally equality `a = b`;
--   * the groupoid laws (reflexivity, symmetry, transitivity) and dependent
--     transport along equality are proved;
--   * concrete witnesses on `ℤ` exercise the definitions.
--
-- Claim limits:
--   * this is NOT a synthetic homotopy type theory development;
--   * no higher paths, univalence, or homotopy groups are formalized here;
--   * `Path` carries no interval or quotient structure beyond `Eq`.

import Mathlib.Data.Int.Basic
import Mathlib.Tactic

namespace Math30.Homotopy

/-- Path space equality wrapper in the discrete lattice. -/
def Path (A : Type) (a b : A) : Prop := a = b

/-- Reflexivity path. -/
theorem refl_path (A : Type) (a : A) : Path A a a := rfl

/-- Symmetry path. -/
theorem symm_path (A : Type) (a b : A) (p : Path A a b) : Path A b a := p.symm

/-- Transitivity path. -/
theorem trans_path (A : Type) (a b c : A) (p1 : Path A a b) (p2 : Path A b c) : Path A a c :=
  Eq.trans p1 p2

/-- Dependent transport along a path: the equality eliminator. -/
def transport {A : Type} (P : A → Type) {a b : A} (p : Path A a b) (x : P a) : P b :=
  p ▸ x

/-- Transport along the reflexivity path is the identity. -/
theorem transport_refl {A : Type} (P : A → Type) (a : A) (x : P a) :
    transport P (refl_path A a) x = x := rfl

theorem path_concat_valid (a b c : ℤ) (p1 : Path ℤ a b) (p2 : Path ℤ b c) :
    Path ℤ a c :=
  trans_path ℤ a b c p1 p2

/-- A concrete inhabitant: `0` is equal to itself. -/
theorem path_witness_zero : Path ℤ 0 0 :=
  refl_path ℤ 0

/-- A concrete symmetry application, not merely the abstract law. -/
theorem path_symm_zero : Path ℤ 0 0 :=
  symm_path ℤ 0 0 (refl_path ℤ 0)

/-- A concrete transport computation: transporting `7` along `2 = 2`. -/
theorem path_transport_witness :
    transport (fun _ : ℤ => ℤ) (refl_path ℤ 2) 7 = 7 :=
  rfl

#print axioms path_concat_valid
#print axioms path_transport_witness

end Math30.Homotopy
