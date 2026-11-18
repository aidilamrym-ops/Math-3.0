import Mathlib.Tactic

/-!
# Guinand–Weil Spectral Trace Bridge (BRIDGE-05)

This file formalizes three finite/rational mechanisms that certify
interval-to-trace positivity over compactly supported test windows, in the
style of the Guinand–Weil explicit formula: interval enclosures with
non-negative lower margin force non-negativity of the enclosed spectral sum,
non-negative critical-line ordinates make the weighted zero sum non-negative,
and a compact-support cutoff makes the spectral sum exactly finite (the tail
contribution vanishes identically, not merely approximately).

1. `critical_line_zero_sum_nonneg`: non-negative critical-line ordinate values
   `Φ (γ i)` yield a non-negative weighted sum over a non-empty `Fin N`.
2. `compact_support_tail_vanishes`: a compact-support cutoff `Φ t = 0` outside
   `[-R, R]` makes every weighted spectral tail contribution exactly zero.
3. `interval_enclosure_preserves_weil_positivity`: an enclosure with
   non-negative lower margin (`rad i ≤ mid i`) preserves non-negativity of the
   true spectral sum `∑ x i`.

Scope: Every statement is finite and rational. This module proves certified
interval-to-trace positivity over compactly supported test windows. It does
**not** claim a proof of the Riemann Hypothesis; RH remains OPEN.
-/

namespace Math30.Bridges

/-- Non-negativity of the weighted critical-line zero sum.

With `hΦ : ∀ i : Fin N, 0 ≤ Φ (γ i)` the critical-line ordinate values are
non-negative, so the weighted sum `∑ (m i : ℚ) * Φ (γ i)` is non-negative on a
non-empty index set `Fin N` (non-emptiness supplied by `hN : 1 ≤ N`).

The primary hypothesis `hΦ` is load-bearing: a negative ordinate value would
make the corresponding weighted term negative and the sum need not be
non-negative. -/
theorem critical_line_zero_sum_nonneg
    (N : ℕ) (m : Fin N → ℕ) (γ : Fin N → ℚ) (Φ : ℚ → ℚ)
    (hΦ : ∀ i : Fin N, 0 ≤ Φ (γ i))
    (hN : 1 ≤ N)
    (hm : ∀ i : Fin N, 1 ≤ m i) :
    Nonempty (Fin N) ∧ 0 ≤ Finset.sum Finset.univ (fun i : Fin N => (m i : ℚ) * Φ (γ i)) := by
  constructor
  · refine ⟨⟨0, ?_⟩⟩
    have hNpos : 1 ≤ N := hN
    omega
  · apply Finset.sum_nonneg
    intro i _
    have hmi_nat : 0 ≤ m i := by
      have hm_one : 1 ≤ m i := hm i
      omega
    have hmi : 0 ≤ (m i : ℚ) := by exact_mod_cast hmi_nat
    have hphi : 0 ≤ Φ (γ i) := hΦ i
    exact mul_nonneg hmi hphi

/-- Compact support makes the spectral tail vanish exactly.

For a test function with compact support cutoff
`hsupp : ∀ t : ℚ, R < |t| → Φ t = 0` (with `0 ≤ R`), every ordinate `t`
outside the window (`R < |t|`) has `Φ t = 0`, hence any weighted spectral
contribution `w * Φ t` is identically zero. This makes finite truncation of
the spectral sum exact rather than approximate.

The primary hypothesis `hsupp` is load-bearing: without the compact-support
cutoff the tail contribution need not vanish. -/
theorem compact_support_tail_vanishes
    (R w t : ℚ) (Φ : ℚ → ℚ)
    (hsupp : ∀ t : ℚ, R < |t| → Φ t = 0)
    (hR : 0 ≤ R)
    (ht : R < |t|) :
    w * Φ t = 0 := by
  have hzero : Φ t = 0 := hsupp t ht
  have hRn : 0 ≤ R := hR
  rw [hzero]
  ring

/-- Interval enclosures preserve Weil positivity.

Given midpoints `mid`, radii `rad`, and enclosed true values `x` with
`hmargin : ∀ i : Fin N, rad i ≤ mid i` (non-negative lower interval bound) and
`henc : ∀ i : Fin N, mid i - rad i ≤ x i ∧ x i ≤ mid i + rad i`, each true
value satisfies `0 ≤ x i`, hence the spectral sum `∑ x i` is non-negative.

The primary hypothesis `hmargin` is load-bearing: if a radius exceeds its
midpoint, the lower interval bound is negative and the enclosed value may be
negative. -/
theorem interval_enclosure_preserves_weil_positivity
    (N : ℕ) (mid rad x : Fin N → ℚ)
    (hmargin : ∀ i : Fin N, rad i ≤ mid i)
    (henc : ∀ i : Fin N, mid i - rad i ≤ x i ∧ x i ≤ mid i + rad i) :
    0 ≤ Finset.sum Finset.univ (fun i : Fin N => x i) := by
  apply Finset.sum_nonneg
  intro i _
  have hmarg : rad i ≤ mid i := hmargin i
  have hlo : mid i - rad i ≤ x i := (henc i).1
  linarith

end Math30.Bridges
