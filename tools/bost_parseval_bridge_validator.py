#!/usr/bin/env python3
"""BRIDGE-08 Bost Slope / Path-Quadric Parseval -- honest interval validator.

Rebuilt 2026-11-21 under the OMEGA recursive audit. The previous revision
printed ``PASS_REAL_FLINT`` while every reported value (inertia, n_neg,
zero_straddle, dsitni_ratio, dibd_ratio, exact_rational_enclosure) was a
literal in a dictionary; its only flint call multiplied an unrelated constant
by the dimension. That is a fabricated certificate, not a validation.

This revision recomputes everything from explicit data:

1. Exact-rational checks of the three Lean statements:
     bost_slope_height_budget_bound
     path_quadric_parseval_energy_conservation
     iterated_parseval_remainder_suppression
   including the budget-equality boundary and the C = X = 0 case.
2. Kernel-of-record inertia of an explicit 64x64 symmetric tridiagonal
   path-quadric Gram matrix, classified from python-flint
   ``arb_mat.eig(nonstop=True)`` interval enclosures at 6000 bits.
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
RECEIPT = ROOT / "reports" / "bridge08_bost_parseval_receipt.json"

DIMENSION = 64
PRECISION_BITS = 6000
BRIDGE_MATRIX_DEFINITION = (
    "64x64 symmetric tridiagonal: M[i][i] = 3, M[i][i+1] = M[i+1][i] = -1"
)


def path_quadric_gram(dimension: int = DIMENSION) -> list[list[Fraction]]:
    """Explicit symmetric tridiagonal path-quadric Gram matrix."""
    matrix = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for index in range(dimension):
        matrix[index][index] = Fraction(3)
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


def interval_inertia(matrix: list[list[Fraction]], precision_bits: int) -> dict:
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


def check_height_budget() -> dict:
    """bost_slope_height_budget_bound on exact rational data."""
    m = DIMENSION
    capacity_unit = Fraction(5, 2)
    products = [Fraction((2 * index + 3) % 5 + 1, 2) for index in range(m)]
    total = sum(products, Fraction(0))
    bound = Fraction(m) * capacity_unit
    empty_sum = sum([], Fraction(0))
    return {
        "name": "bost_slope_height_budget_bound",
        "ok": max(products) <= capacity_unit and total <= bound and empty_sum <= 0,
        "max_product": {"num": max(products).numerator, "den": max(products).denominator},
        "capacity_unit": {
            "num": capacity_unit.numerator,
            "den": capacity_unit.denominator,
        },
        "sum": {"num": total.numerator, "den": total.denominator},
        "dimension_bound": {"num": bound.numerator, "den": bound.denominator},
        "boundary_case_equality": max(products) == capacity_unit,
        "empty_sum_ok": empty_sum <= 0,
    }


def check_parseval_energy() -> dict:
    """path_quadric_parseval_energy_conservation on exact rational data."""
    amplitudes = [Fraction((index % 5) + 1, 4) for index in range(DIMENSION)]
    energies = [amplitude * amplitude for amplitude in amplitudes]
    energy_max = Fraction(25, 16)
    total = sum(energies, Fraction(0))
    bound = Fraction(DIMENSION) * energy_max
    return {
        "name": "path_quadric_parseval_energy_conservation",
        "ok": all(energy >= 0 for energy in energies)
        and all(energy <= energy_max for energy in energies)
        and total <= bound,
        "energy_sum": {"num": total.numerator, "den": total.denominator},
        "energy_bound": {"num": bound.numerator, "den": bound.denominator},
        "max_energy": {
            "num": max(energies).numerator,
            "den": max(energies).denominator,
        },
        "energy_max": {"num": energy_max.numerator, "den": energy_max.denominator},
    }


def check_iterated_remainder() -> dict:
    """iterated_parseval_remainder_suppression on exact rational data."""
    coefficient = Fraction(3, 2)
    variable = Fraction(4, 5)
    remainder = Fraction(1)
    hypothesis = remainder**2 <= coefficient**2 * variable
    conclusion = remainder**2 <= (coefficient * variable + coefficient) ** 2
    degenerate = (Fraction(0) ** 2 <= (Fraction(0) * Fraction(0) + Fraction(0)) ** 2)
    return {
        "name": "iterated_parseval_remainder_suppression",
        "ok": hypothesis and conclusion and degenerate,
        "hypothesis_holds": hypothesis,
        "conclusion_holds": conclusion,
        "degenerate_case_ok": degenerate,
        "parameters": {
            "R": str(remainder),
            "C": str(coefficient),
            "X": str(variable),
        },
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
    matrix = path_quadric_gram()
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
        "height_budget": check_height_budget(),
        "parseval_energy": check_parseval_energy(),
        "iterated_remainder": check_iterated_remainder(),
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
        "bridge": "BRIDGE-08 BostSlopeParsevalBridge",
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
            "meaning": "minimum leading principal minor D_1..D_64 (exact Sylvester witness)",
        },
        "determinant": {"num": determinant.numerator, "den": determinant.denominator},
        "theorem_checks": checks,
        "negative_controls": controls,
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print("BRIDGE-08 Bost slope / Parseval validator (honest rebuild)")
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
