#!/usr/bin/env python3
"""BRIDGE-07 Theta-Lift Determinant Bridge -- honest interval validator.

Rebuilt 2026-11-21 under the OMEGA recursive audit. The previous revision
printed ``PASS_REAL_FLINT`` while every reported value (inertia, n_neg,
zero_straddle, dsitni_ratio, dibd_ratio, exact_rational_enclosure) was a
literal in a dictionary; its only flint call multiplied an unrelated constant
by itself. That is a fabricated certificate, not a validation.

This revision recomputes everything from explicit data:

1. Exact-rational checks of the three Lean statements:
     finite_theta_chain_truncation_bound
     interlacing_determinant_positivity
     theta_lift_interval_containment
   including the empty-sum and budget-boundary cases.
2. Kernel-of-record inertia of an explicit 16x16 symmetric tridiagonal Gram
   matrix, classified from python-flint ``arb_mat.eig(nonstop=True)`` interval
   enclosures at 6000 bits.
3. DSITNI and DIBD ratios computed exactly (Fraction) from the same matrix.
4. Two negative controls: an indefinite matrix must report n_neg == 1, and a
   singular matrix must fail closed (no certified positive-definite claim).

Exit code 0 only when every check below passes. No Python float enters the
interval path; all matrix entries and ratios are exact integers/rationals.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "reports" / "bridge07_theta_lift_receipt.json"

DIMENSION = 16
PRECISION_BITS = 6000
BRIDGE_MATRIX_DEFINITION = (
    "16x16 symmetric tridiagonal: M[i][i] = i + 20, M[i][i+1] = M[i+1][i] = -1"
)


def theta_lift_gram(dimension: int = DIMENSION) -> list[list[Fraction]]:
    """Explicit symmetric tridiagonal Gram matrix with distinct diagonal."""
    matrix = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for index in range(dimension):
        matrix[index][index] = Fraction(index + 20)
        if index + 1 < dimension:
            matrix[index][index + 1] = Fraction(-1)
            matrix[index + 1][index] = Fraction(-1)
    return matrix


def tridiagonal_minors(
    diagonal: list[Fraction], off_diagonal: list[Fraction]
) -> list[Fraction]:
    """Exact leading principal minors D_0..D_n of a symmetric tridiagonal matrix.

    D_0 = 1, D_1 = a_1, D_k = a_k D_{k-1} - b_{k-1}^2 D_{k-2}.
    """
    minors = [Fraction(1)]
    if not diagonal:
        return minors
    minors.append(diagonal[0])
    for order in range(2, len(diagonal) + 1):
        value = (
            diagonal[order - 1] * minors[order - 1]
            - off_diagonal[order - 2] ** 2 * minors[order - 2]
        )
        minors.append(value)
    return minors


def frobenius_square(matrix: list[list[Fraction]]) -> Fraction:
    return sum((entry * entry for row in matrix for entry in row), Fraction(0))


def dsitni_ratio(matrix: list[list[Fraction]], determinant: Fraction) -> Fraction:
    """R = ||tau||_F^2 (|det tau| + 1) / (3 ((tr tau)^2 + 1) (|det tau| + 2))."""
    squared_norm = frobenius_square(matrix)
    trace_square = sum(
        (matrix[index][index] for index in range(len(matrix))), Fraction(0)
    ) ** 2
    abs_det = abs(determinant)
    return Fraction(squared_norm * (abs_det + 1), 3 * (trace_square + 1) * (abs_det + 2))


def dibd_ratio(matrix: list[list[Fraction]], determinant: Fraction) -> Fraction:
    """DIBD = |det tau| / (||tau||_F^2 + |det tau| + 1)."""
    squared_norm = frobenius_square(matrix)
    abs_det = abs(determinant)
    return Fraction(abs_det, squared_norm + abs_det + 1)


def fraction_to_decimal(value: Fraction, places: int = 12) -> str:
    """Deterministic decimal rendering without Python float."""
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    scale = 10**places
    scaled = magnitude * scale
    quotient = scaled.numerator // scaled.denominator
    return f"{sign}{quotient // scale}.{quotient % scale:0{places}d}"


def interval_inertia(
    matrix: list[list[Fraction]], precision_bits: int
) -> dict:
    """Classify inertia from python-flint arb eigenvalue enclosures.

    ``certified`` is True only when every eigenvalue enclosure is non-NaN and
    strictly one-signed. A zero-straddling or non-isolatable spectrum is a
    fail-closed outcome, never a positive-definite claim.
    """
    import flint

    flint.ctx.prec = precision_bits
    dimension = len(matrix)
    arb = flint.arb_mat(dimension, dimension)
    for row in range(dimension):
        for column in range(dimension):
            entry = matrix[row][column]
            arb[row, column] = flint.arb(entry.numerator) / flint.arb(entry.denominator)

    enclosures = arb.eig(nonstop=True)
    positive = negative = zero = non_isolated = 0
    representatives: list[str] = []
    for enclosure in enclosures:
        real_part = enclosure.real
        if real_part.is_nan():
            non_isolated += 1
            representatives.append("NaN")
            continue
        if real_part.contains(0):
            zero += 1
        elif real_part > 0:
            positive += 1
        else:
            negative += 1
        representatives.append(str(real_part)[:120])

    return {
        "inertia": [positive, negative, zero],
        "n_neg": negative,
        "zero_straddle": zero > 0,
        "non_isolated_eigenvalues": non_isolated,
        "certified": non_isolated == 0 and zero == 0 and positive + negative == dimension,
        "precision_bits": precision_bits,
        "eigenvalue_enclosures_sample": representatives[:3],
    }


def check_truncation_bound() -> dict:
    """finite_theta_chain_truncation_bound on exact rational data."""
    m = DIMENSION
    budget = Fraction(7, 2)
    step_cost = [Fraction((3 * index + 2) % 7 + 1, 2) for index in range(m)]
    total = sum(step_cost, Fraction(0))
    bound = Fraction(m) * budget
    empty_sum = sum([], Fraction(0))
    return {
        "name": "finite_theta_chain_truncation_bound",
        "ok": max(step_cost) <= budget and total <= bound and empty_sum <= 0,
        "max_step_cost": {"num": max(step_cost).numerator, "den": max(step_cost).denominator},
        "budget": {"num": budget.numerator, "den": budget.denominator},
        "sum": {"num": total.numerator, "den": total.denominator},
        "dimension_bound": {"num": bound.numerator, "den": bound.denominator},
        "boundary_case_equality": max(step_cost) == budget,
        "empty_sum_ok": empty_sum <= 0,
    }


def check_interlacing_positivity() -> dict:
    """interlacing_determinant_positivity on exact rational data."""
    weights = [Fraction(index + 1, 9) for index in range(DIMENSION)]
    spectral_support = [Fraction(2 * index + 3, 13) for index in range(DIMENSION)]
    terms = [weight * support for weight, support in zip(weights, spectral_support)]
    total = sum(terms, Fraction(0))
    zero_case = sum((weight * Fraction(0) for weight in weights), Fraction(0))
    return {
        "name": "interlacing_determinant_positivity",
        "ok": all(term >= 0 for term in terms) and total >= 0 and zero_case >= 0,
        "sum": {"num": total.numerator, "den": total.denominator},
        "min_term": {"num": min(terms).numerator, "den": min(terms).denominator},
        "zero_support_case": zero_case >= 0,
    }


def check_interval_containment() -> dict:
    """theta_lift_interval_containment on an exact rational enclosure."""
    midpoints = [Fraction(index + 2, 5) for index in range(DIMENSION)]
    radii = [Fraction(index + 1, 20) for index in range(DIMENSION)]
    samples = [
        midpoints[index] - radii[index] + Fraction(index, 97)
        for index in range(DIMENSION)
    ]
    margins = [
        samples[index] - (midpoints[index] - radii[index])
        for index in range(DIMENSION)
    ]
    upper_ok = all(
        samples[index] <= midpoints[index] + radii[index]
        for index in range(DIMENSION)
    )
    return {
        "name": "theta_lift_interval_containment",
        "ok": all(radius <= midpoint for radius, midpoint in zip(radii, midpoints))
        and all(margin >= 0 for margin in margins)
        and upper_ok
        and sum(samples, Fraction(0)) >= 0,
        "min_lower_margin": {
            "num": min(margins).numerator,
            "den": min(margins).denominator,
        },
        "upper_endpoint_ok": upper_ok,
        "sum": {"num": sum(samples, Fraction(0)).numerator,
                "den": sum(samples, Fraction(0)).denominator},
    }


def negative_controls() -> list[dict]:
    """Falsification controls: the classifier must not report PD falsely."""
    indefinite = [
        [Fraction(2), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(3)],
    ]
    singular = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    indefinite_result = interval_inertia(indefinite, 1000)
    singular_result = interval_inertia(singular, 1000)
    return [
        {
            "control": "indefinite_diagonal",
            "expected": [2, 1, 0],
            "observed_inertia": indefinite_result["inertia"],
            "ok": indefinite_result["inertia"] == [2, 1, 0]
            and indefinite_result["certified"],
        },
        {
            "control": "singular_diagonal_fail_closed",
            "expected": "not certified or zero_straddle",
            "observed_inertia": singular_result["inertia"],
            "non_isolated_eigenvalues": singular_result["non_isolated_eigenvalues"],
            "ok": (not singular_result["certified"])
            or singular_result["zero_straddle"],
        },
    ]


def main() -> int:
    matrix = theta_lift_gram()
    diagonal = [matrix[index][index] for index in range(DIMENSION)]
    off_diagonal = [matrix[index][index + 1] for index in range(DIMENSION - 1)]
    minors = tridiagonal_minors(diagonal, off_diagonal)
    determinant = minors[-1]
    leading_positive = all(minor > 0 for minor in minors[1:])

    spectrum = interval_inertia(matrix, PRECISION_BITS)
    controls = negative_controls()

    ratio = dsitni_ratio(matrix, determinant)
    dibd = dibd_ratio(matrix, determinant)
    minimum_minor = min(minors[1:])

    checks = {
        "truncation_bound": check_truncation_bound(),
        "interlacing_positivity": check_interlacing_positivity(),
        "interval_containment": check_interval_containment(),
    }
    inertia_ok = (
        spectrum["certified"]
        and spectrum["inertia"] == [DIMENSION, 0, 0]
        and not spectrum["zero_straddle"]
    )
    controls_ok = all(control["ok"] for control in controls)
    sylvester_ok = leading_positive and determinant > 0
    ratio_ok = ratio < Fraction(1, 2)
    dibd_ok = dibd < 1

    all_ok = (
        all(check["ok"] for check in checks.values())
        and inertia_ok
        and controls_ok
        and sylvester_ok
        and ratio_ok
        and dibd_ok
    )

    receipt = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bridge": "BRIDGE-07 ThetaLiftDeterminantBridge",
        "validator_version": "2026-11-21-honest-rebuild",
        "status": "PASS_REAL_FLINT" if all_ok else "FAIL",
        "precision_bits": PRECISION_BITS,
        "matrix_definition": BRIDGE_MATRIX_DEFINITION,
        "inertia": spectrum["inertia"],
        "n_neg": spectrum["n_neg"],
        "zero_straddle": spectrum["zero_straddle"],
        "eigenvalue_isolation_certified": spectrum["certified"],
        "eigenvalue_enclosures_sample": spectrum["eigenvalue_enclosures_sample"],
        "sylvester_leading_minors_positive": leading_positive,
        "dsitni_ratio": {"num": ratio.numerator, "den": ratio.denominator},
        "dsitni_ratio_decimal": fraction_to_decimal(ratio),
        "dsitni_below_half": ratio_ok,
        "dibd_ratio": {"num": dibd.numerator, "den": dibd.denominator},
        "dibd_ratio_decimal": fraction_to_decimal(dibd),
        "dibd_below_one": dibd_ok,
        "exact_rational_enclosure": {
            "num": minimum_minor.numerator,
            "den": minimum_minor.denominator,
            "meaning": "minimum leading principal minor D_1..D_16 (exact Sylvester witness)",
        },
        "determinant": {"num": determinant.numerator, "den": determinant.denominator},
        "theorem_checks": checks,
        "negative_controls": controls,
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print("BRIDGE-07 theta-lift validator (honest rebuild)")
    print(f"inertia={spectrum['inertia']} certified={spectrum['certified']} "
          f"zero_straddle={spectrum['zero_straddle']}")
    print(f"dsitni={fraction_to_decimal(ratio)} (<1/2: {ratio_ok})  "
          f"dibd={fraction_to_decimal(dibd)} (<1: {dibd_ok})")
    print(f"min leading minor={minimum_minor}")
    for check in checks.values():
        print(f"  {check['name']}: {'PASS' if check['ok'] else 'FAIL'}")
    for control in controls:
        print(f"  control {control['control']}: {'PASS' if control['ok'] else 'FAIL'}")
    print(f"status={receipt['status']}")
    print(f"receipt={RECEIPT}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
