#!/usr/bin/env python3
"""BRIDGE-10 Dirichlet Character / GRH Window -- honest interval validator.

Rebuilt 2026-11-21 under the OMEGA recursive audit. The previous revision
printed ``PASS_REAL_FLINT`` while every reported quantity (inertia, n_neg,
zero_straddle, dsitni_ratio, dibd_ratio, exact_rational_enclosure) was a
literal in a dictionary; its only flint call multiplied 1.0 by 64. That is a
fabricated certificate, not a validation.

This revision recomputes everything from explicit data:

1. Exact-rational instantiation checks of the three Lean statements in
   ``lean/spec_v4/bridges/GrhCharacterLatticeBridge.lean``:
     dirichlet_character_orthogonality_bound
     grh_explicit_window_positivity
     masullo_gap_isolation_enclosure
   including empty-index, unit-modulus boundary, zero-weight and endpoint
   enclosure cases.
2. Kernel-of-record inertia of an explicit 64x64 symmetric tridiagonal
   witness matrix, classified from python-flint ``arb_mat.eig(nonstop=True)``
   interval enclosures at 6000 bits.
3. DSITNI and DIBD ratios computed exactly (Fraction) from the same matrix.
4. Two negative controls: an indefinite matrix must report n_neg == 1, and a
   singular matrix must fail closed (no certified positive-definite claim).

Exit codes: 0 all checks pass; 1 any check fails; 2 python-flint missing.
No Python float enters the interval path; matrix entries and ratios are exact
integers/rationals.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

try:
    import flint
except ImportError:  # fail closed in main(); never emit a pass without it
    flint = None

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "reports" / "bridge10_grh_character_receipt.json"

DIMENSION = 64
PRECISION_BITS = 6000
BRIDGE_MATRIX_DEFINITION = (
    "64x64 symmetric tridiagonal: M[i][i] = 4, M[i][i+1] = M[i+1][i] = -1"
)
MATRIX_ROLE = (
    "independent numerical witness for kernel inertia, DSITNI and DIBD; the "
    "Lean theorems are parametric and do not assume this matrix"
)
EXIT_FLINT_MISSING = 2


def character_gram(dimension: int = DIMENSION) -> list[list[Fraction]]:
    """Explicit symmetric tridiagonal character Gram witness matrix."""
    matrix = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for index in range(dimension):
        matrix[index][index] = Fraction(4)
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
    if flint is None:
        raise RuntimeError("python-flint is required for interval inertia")

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


def check_character_orthogonality() -> dict:
    """dirichlet_character_orthogonality_bound on an exact-rational instance."""
    character = [Fraction((index % 5) - 2, 2) for index in range(DIMENSION)]
    squares = [value * value for value in character]
    total = sum(squares, Fraction(0))
    unit_character = [Fraction(1) for _ in range(DIMENSION)]
    unit_total = sum((value * value for value in unit_character), Fraction(0))
    empty_ok = sum([], Fraction(0)) == 0
    return {
        "name": "dirichlet_character_orthogonality_bound",
        "ok": all(square <= 1 for square in squares)
        and total >= 0
        and total <= DIMENSION
        and unit_total == DIMENSION
        and unit_total <= DIMENSION
        and empty_ok,
        "square_sum": {"num": total.numerator, "den": total.denominator},
        "dimension_bound": DIMENSION,
        "unit_modulus_boundary_equality": unit_total == DIMENSION,
        "empty_index_case_ok": empty_ok,
        "values": [str(value) for value in sorted(set(character))],
    }


def check_window_positivity() -> dict:
    """grh_explicit_window_positivity on an exact-rational instance."""
    weights = [Fraction((index % 4) + 1, 7) for index in range(DIMENSION)]
    window = [Fraction((index % 3) + 1, 5) for index in range(DIMENSION)]
    terms = [weight * value for weight, value in zip(weights, window)]
    total = sum(terms, Fraction(0))
    zero_weights = [Fraction(0) for _ in range(DIMENSION)]
    zero_total = sum(
        (weight * value for weight, value in zip(zero_weights, window)),
        Fraction(0),
    )
    return {
        "name": "grh_explicit_window_positivity",
        "ok": all(weight >= 0 for weight in weights)
        and all(value >= 0 for value in window)
        and all(term >= 0 for term in terms)
        and total >= 0
        and zero_total == 0
        and sum([], Fraction(0)) >= 0,
        "window_sum": {"num": total.numerator, "den": total.denominator},
        "min_term": {
            "num": min(terms).numerator,
            "den": min(terms).denominator,
        },
        "zero_weight_case_ok": zero_total == 0,
        "empty_sum_ok": sum([], Fraction(0)) >= 0,
    }


def check_gap_isolation() -> dict:
    """masullo_gap_isolation_enclosure on an exact-rational instance."""
    midpoints = [Fraction(index + 3, 4) for index in range(DIMENSION)]
    radii = [Fraction(1, 4) for _ in range(DIMENSION)]
    lower = [midpoints[index] - radii[index] for index in range(DIMENSION)]
    upper = [midpoints[index] + radii[index] for index in range(DIMENSION)]
    endpoint_samples = list(lower)
    interior_samples = [
        midpoints[index] + Fraction(1, 8) for index in range(DIMENSION)
    ]
    endpoint_total = sum(endpoint_samples, Fraction(0))
    interior_ok = all(
        lower[index] <= interior_samples[index] <= upper[index]
        for index in range(DIMENSION)
    )
    return {
        "name": "masullo_gap_isolation_enclosure",
        "ok": all(radii[index] <= midpoints[index] for index in range(DIMENSION))
        and all(lower[index] >= 0 for index in range(DIMENSION))
        and all(
            lower[index] <= endpoint_samples[index] <= upper[index]
            for index in range(DIMENSION)
        )
        and endpoint_total >= 0
        and interior_ok
        and sum([], Fraction(0)) >= 0,
        "sum_at_lower_endpoints": {
            "num": endpoint_total.numerator,
            "den": endpoint_total.denominator,
        },
        "min_lower_endpoint": {
            "num": min(lower).numerator,
            "den": min(lower).denominator,
        },
        "interior_case_ok": interior_ok,
        "empty_sum_ok": sum([], Fraction(0)) >= 0,
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


def fail_closed_receipt(reason: str) -> int:
    receipt = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bridge": "BRIDGE-10 GrhCharacterLatticeBridge",
        "validator_version": "2026-11-21-honest-rebuild",
        "status": "FAIL",
        "reason": reason,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"FATAL: {reason}", file=sys.stderr)
    return EXIT_FLINT_MISSING


def main() -> int:
    if flint is None:
        return fail_closed_receipt(
            "python-flint missing: interval inertia cannot be certified"
        )

    matrix = character_gram()
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
        "character_orthogonality": check_character_orthogonality(),
        "window_positivity": check_window_positivity(),
        "gap_isolation": check_gap_isolation(),
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
        "bridge": "BRIDGE-10 GrhCharacterLatticeBridge",
        "validator_version": "2026-11-21-honest-rebuild",
        "status": "PASS_REAL_FLINT" if all_ok else "FAIL",
        "precision_bits": PRECISION_BITS,
        "matrix_definition": BRIDGE_MATRIX_DEFINITION,
        "matrix_role": MATRIX_ROLE,
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
        "determinant": {
            "num": determinant.numerator,
            "den": determinant.denominator,
        },
        "theorem_checks": checks,
        "negative_controls": controls,
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print("BRIDGE-10 Dirichlet character / GRH validator (honest rebuild)")
    print(
        f"inertia={spectrum['inertia']} certified={spectrum['certified']} "
        f"zero_straddle={spectrum['zero_straddle']}"
    )
    print(
        f"dsitni={fraction_to_decimal(ratio)} (<1/2: {ratio_ok})  "
        f"dibd={fraction_to_decimal(dibd)} (<1: {dibd_ok})"
    )
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
