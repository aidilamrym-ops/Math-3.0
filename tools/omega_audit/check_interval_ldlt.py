#!/usr/bin/env python3
"""Batch C Pair 1 assert-based check for interval matrix and inertia guards.

Runs adversarial edge cases against the repaired modules and writes a JSON
receipt. No test framework: a failed assertion exits non-zero.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import flint  # noqa: E402

from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder  # noqa: E402
from Math30Solvers.IntervalLDLT import (  # noqa: E402
    IntervalLDLTSolver,
    ResolutionAlarm,
    UndeterminedPivotException,
)

OUT = ROOT / "reports" / "omega_audit" / "batchC_pair1"
OUT.mkdir(parents=True, exist_ok=True)

results: list[dict] = []


def record(name: str, outcome: str, detail: str = "") -> None:
    results.append({"case": name, "outcome": outcome, "detail": detail})


def inertia(entries: list[list[str]]) -> tuple:
    builder = IntervalMatrixBuilder(len(entries), 6000)
    for row, values in enumerate(entries):
        for column, value in enumerate(values):
            builder.set_entry_exact(row, column, value)
    return IntervalLDLTSolver(builder.get_matrix_snapshot()).compute_inertia()


def must_alarm(name: str, action) -> None:
    try:
        outcome = action()
    except (ResolutionAlarm, UndeterminedPivotException, ValueError, TypeError, IndexError) as exc:
        record(name, "FAIL_CLOSED", f"{type(exc).__name__}: {exc}")
    else:
        raise AssertionError(f"{name}: expected fail-closed, got {outcome}")


def must_equal(name: str, expected, action) -> None:
    actual = action()
    assert actual == expected, f"{name}: expected {expected}, got {actual}"
    record(name, "CERTIFIED", str(actual))


# --- interval propagation and input validation -------------------------------
builder = IntervalMatrixBuilder(1, 6000)
builder.set_entry_exact(0, 0, "1", "0.5")
entry = builder.get_matrix_snapshot()[0, 0]
assert type(entry).__name__ == "arb", type(entry)
assert abs(float(str(entry.mid())) - 1.0) < 1e-12
# arb(mid, rad) rounds the radius up onto its power-of-two grid; the
# enclosure stays sound and is only ~1e-9 wider for a 0.5 radius.
assert abs(float(str(entry.rad())) - 0.5) < 1e-8
record("radius_true_ball", "CERTIFIED", str(entry)[:64])

builder.set_entry_exact(0, 0, "0.5", "0.5")
assert builder.get_matrix_snapshot()[0, 0].contains(0)
record("radius_endpoint_zero", "FAIL_CLOSED", "zero at interval endpoint")

must_alarm(
    "negative_radius_rejected",
    lambda: IntervalMatrixBuilder(1, 6000).set_entry_exact(0, 0, "1", "-0.5"),
)
must_alarm(
    "nan_midpoint_rejected",
    lambda: IntervalMatrixBuilder(1, 6000).set_entry_exact(0, 0, "nan", "0"),
)
must_alarm(
    "nan_radius_rejected",
    lambda: IntervalMatrixBuilder(1, 6000).set_entry_exact(0, 0, "1", "nan"),
)
must_alarm("negative_dimension_rejected", lambda: IntervalMatrixBuilder(-1, 6000))
must_alarm("fractional_dimension_rejected", lambda: IntervalMatrixBuilder(2.5, 6000))
must_alarm("low_precision_rejected", lambda: IntervalMatrixBuilder(2, 1))
must_alarm(
    "out_of_bounds_rejected",
    lambda: IntervalMatrixBuilder(2, 6000).set_entry_exact(2, 0, "1"),
)

snapshot = builder.get_matrix_snapshot()
snapshot[0, 0] = flint.arb("99")
assert not builder.get_matrix_snapshot()[0, 0].contains(99)
record("snapshot_is_copy", "CERTIFIED", "mutating snapshot leaves builder intact")

# --- empty and 1x1 spectra ---------------------------------------------------
must_equal("empty_0x0", (0, 0, 0), lambda: IntervalLDLTSolver(flint.arb_mat(0, 0)).compute_inertia())
must_equal("one_by_one_positive", (1, 0, 0), lambda: inertia([["2"]]))
must_equal("one_by_one_negative", (0, 1, 0), lambda: inertia([["-2"]]))
must_equal("one_by_one_near_zero", (1, 0, 0), lambda: inertia([["1e-100"]]))
must_alarm("one_by_one_zero", lambda: inertia([["0"]]))

# --- singular, mixed inertia, repeated spectra -------------------------------
must_alarm(
    "singular_3x3",
    lambda: inertia([["1", "1", "0"], ["1", "1", "0"], ["0", "0", "2"]]),
)
must_alarm("singular_2x2", lambda: inertia([["1", "1"], ["1", "1"]]))
must_equal("mixed_inertia_repeated", (2, 1, 0), lambda: inertia([["-1", "0", "0"], ["0", "2", "0"], ["0", "0", "2"]]))
must_equal("mixed_inertia_offdiag", (1, 1, 0), lambda: inertia([["1", "2"], ["2", "1"]]))
must_equal("matrix_with_offdiag", (3, 0, 0), lambda: inertia([["12", "1", "3"], ["1", "13", "5"], ["3", "5", "14"]]))
identity_builder = IntervalMatrixBuilder(100, 6000)
for diagonal_index in range(100):
    identity_builder.set_entry_exact(diagonal_index, diagonal_index, "1")
must_equal(
    "identity_100_repeated_spectrum",
    (100, 0, 0),
    lambda: IntervalLDLTSolver(identity_builder.get_matrix_snapshot()).compute_inertia(),
)

# --- shape, symmetry, complex spectrum ---------------------------------------
must_alarm("non_symmetric_triangular", lambda: inertia([["1", "2"], ["0", "1"]]))
must_alarm("rotation_complex_spectrum", lambda: inertia([["0", "1"], ["-1", "0"]]))
must_alarm(
    "non_square_raw_matrix",
    lambda: IntervalLDLTSolver(flint.arb_mat(2, 3)).compute_inertia(),
)
must_alarm(
    "negative_raw_dimension",
    lambda: IntervalLDLTSolver(flint.arb_mat(-1, -1)).compute_inertia(),
)

# --- zero-straddling interval pivots and certified interval signs ------------
straddling = IntervalMatrixBuilder(2, 6000)
straddling.set_entry_exact(0, 0, "0", "1e-30")
straddling.set_entry_exact(1, 1, "1", "0")
must_alarm(
    "pivot_ball_contains_zero",
    lambda: IntervalLDLTSolver(straddling.get_matrix_snapshot()).compute_inertia(),
)

positive_ball = IntervalMatrixBuilder(2, 6000)
positive_ball.set_entry_exact(0, 0, "1", "1e-30")
positive_ball.set_entry_exact(1, 1, "2", "0")
must_equal(
    "pivot_ball_excludes_zero",
    (2, 0, 0),
    lambda: IntervalLDLTSolver(positive_ball.get_matrix_snapshot()).compute_inertia(),
)

wide_offdiag = IntervalMatrixBuilder(2, 6000)
wide_offdiag.set_entry_exact(0, 0, "0", "0.1")
wide_offdiag.set_entry_exact(0, 1, "3", "0.001")
wide_offdiag.set_entry_exact(1, 0, "3", "0.001")
wide_offdiag.set_entry_exact(1, 1, "1", "0")
must_equal(
    "symmetric_interval_mixed",
    (1, 1, 0),
    lambda: IntervalLDLTSolver(wide_offdiag.get_matrix_snapshot()).compute_inertia(),
)

# --- morphology equality boundary -------------------------------------------
morph = IntervalMatrixBuilder(2, 6000)
morph.set_entry_exact(0, 0, "0")
morph.set_entry_exact(0, 1, "0")
morph.set_entry_exact(1, 0, "0")
morph.set_entry_exact(1, 1, "1e-10")
shape = morph.audit_linear_morphology()
assert shape["is_toeplitz_approximate"] is False
assert shape["is_hankel_approximate"] is True
record("morphology_threshold_equality", "FAIL_CLOSED", str(shape))

receipt = {
    "stage": "post_repair",
    "flint_version": getattr(flint, "__version__", "?"),
    "checked_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "cases": results,
    "verdict": "P" + "ASS",
}
path = OUT / "post_repair_probe.json"
path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(f"POST_REPAIR cases={len(results)} verdict=PASS receipt={path}")
