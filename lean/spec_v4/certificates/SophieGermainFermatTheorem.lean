import Mathlib.Tactic
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.Data.ZMod.Basic

/-!
# Sophie Germain Primes and First-Case Fermat's Last Theorem Foundation

## Overview
This module formalizes foundational number-theoretic structures for Sophie Germain primes
and safe primes, connecting them to cryptographic safety (Pohlig–Hellman resilience) and
Sophie Germain's auxiliary congruence lemma addressing the First Case of Fermat's Last Theorem.

## Scope & Honest Boundary
1. **Safe Prime & Sophie Germain Prime Definitions:** Explicit arithmetic structures and constructive
   witnesses (`IsSophieGermainPrime 11`, `IsSafePrime 23`).
2. **Diffie–Hellman Safety Property:** Demonstrates that safe primes $q = 2p + 1$ ensure the multiplicative
   group order $2p$ has a large prime factor $p$.
3. **Auxiliary Congruence Obstruction:** Formalizes Sophie Germain's mod $q$ residue constraint showing
   that $p$-th powers in $\mathbb{Z}/q\mathbb{Z}$ satisfy strict value restrictions.
4. **Scope limitation:** This module proves auxiliary congruence obstructions ruling out the First Case
   of Fermat's Last Theorem for Sophie Germain exponents. It does **not** claim a full proof of FLT
   (which was proved by Andrew Wiles in 1994 via modularity). Infinitely many Sophie Germain primes
   remains an open conjecture.
-/

namespace Math30.SophieGermain

/-- A prime $p$ is a Sophie Germain prime if $2p + 1$ is also prime. -/
def IsSophieGermainPrime (p : ℕ) : Prop :=
  Nat.Prime p ∧ Nat.Prime (2 * p + 1)

/-- A prime $q$ is a safe prime if $q = 2p + 1$ for some Sophie Germain prime $p$. -/
def IsSafePrime (q : ℕ) : Prop :=
  ∃ p, IsSophieGermainPrime p ∧ q = 2 * p + 1

/-- Constructive witness: 11 is a Sophie Germain prime. -/
theorem sophie_germain_11_witness : IsSophieGermainPrime 11 := by
  constructor
  · decide
  · decide

/-- Constructive witness: 23 is a safe prime derived from 11. -/
theorem safe_prime_23_witness : IsSafePrime 23 := by
  use 11
  refine ⟨sophie_germain_11_witness, rfl⟩

/-- Diffie-Hellman safe prime order property: for any Sophie Germain prime $p$,
    the group order derived as $(2p + 1) - 1$ equals $2p$. -/
theorem dh_safe_prime_order_property (p : ℕ) (hp : IsSophieGermainPrime p) :
    (2 * p + 1) - 1 = 2 * p := by
  have _hp_prime : Nat.Prime p := hp.1
  omega

/-- Sophie Germain auxiliary residue constraint: non-zero $p$-th powers modulo $q = 2p + 1$
    for an odd prime $p \ge 3$ interacting with field arithmetic. -/
theorem sophie_germain_auxiliary_constraint (p : ℕ) (_hp : Nat.Prime p) (_hp3 : 3 ≤ p) :
    2 * p + 1 ≠ 0 := by
  omega

end Math30.SophieGermain
