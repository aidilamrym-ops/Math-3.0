from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import flint  # noqa: E402

from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder  # noqa: E402
from Math30Solvers.IntervalLDLT import IntervalLDLTSolver  # noqa: E402

OUT = ROOT / "reports" / "flawed_artifacts" / "interval_ldlt_soundness_2026-11-21"
OUT.mkdir(parents=True, exist_ok=True)


def build(entries: list[list[str]], precision: int = 6000) -> IntervalMatrixBuilder:
    builder = IntervalMatrixBuilder(len(entries), precision)
    for row, values in enumerate(entries):
        for column, value in enumerate(values):
            builder.set_entry_exact(row, column, value)
    return builder


def observe_inertia(entries: list[list[str]]) -> dict:
    record: dict = {"entries": entries}
    try:
        matrix = build(entries).get_matrix_snapshot()
        record["shape"] = [matrix.nrows(), matrix.ncols()]
        try:
            record["inertia"] = list(IntervalLDLTSolver(matrix).compute_inertia())
        except Exception as exc:  # noqa: BLE001
            record["inertia_exception"] = f"{type(exc).__name__}: {exc}"
        try:
            values = matrix.eig(nonstop=True)
            record["eig_nan"] = [bool(value.real.is_nan()) for value in values]
        except Exception as exc:  # noqa: BLE001
            record["eig_exception"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001
        record["build_exception"] = f"{type(exc).__name__}: {exc}"
    return record


report: dict = {
    "stage": "pre_repair",
    "flint_version": getattr(flint, "__version__", "?"),
    "observations": {},
}

report["observations"]["symmetric_mixed_2x2_expected_1_1_0"] = observe_inertia(
    [["1", "2"], ["2", "1"]]
)
report["observations"]["non_symmetric_triangular"] = observe_inertia(
    [["1", "2"], ["0", "1"]]
)
report["observations"]["identity_2"] = observe_inertia([["1", "0"], ["0", "1"]])
report["observations"]["singular_3x3"] = observe_inertia(
    [["1", "1", "0"], ["1", "1", "0"], ["0", "0", "2"]]
)
report["observations"]["one_by_one_near_zero"] = observe_inertia([["1e-100"]])

# Radius semantics: the documented rad_str should widen symmetrically about mid.
builder = IntervalMatrixBuilder(1, 6000)
builder.set_entry_exact(0, 0, "1", "0.5")
entry = builder.get_matrix_snapshot()[0, 0]
report["observations"]["radius_semantics_mid1_rad0.5"] = {
    "entry": str(entry)[:120],
    "mid": str(entry.mid())[:60],
    "rad": str(entry.rad())[:60],
    "contains_zero": bool(entry.contains(0)),
}

try:
    builder_neg = IntervalMatrixBuilder(1, 6000)
    builder_neg.set_entry_exact(0, 0, "1", "-0.5")
    negative_entry = builder_neg.get_matrix_snapshot()[0, 0]
    report["observations"]["negative_radius"] = {
        "accepted": True,
        "entry": str(negative_entry)[:120],
    }
except Exception as exc:  # noqa: BLE001
    report["observations"]["negative_radius"] = {
        "accepted": False,
        "exception": f"{type(exc).__name__}: {exc}",
    }

negative_dimension = IntervalMatrixBuilder(-1, 6000)
report["observations"]["negative_dimension"] = {
    "requested": -1,
    "shape": [negative_dimension.get_matrix_snapshot().nrows(),
              negative_dimension.get_matrix_snapshot().ncols()],
}

zero = flint.arb_mat(0, 0)
try:
    zero_values = zero.eig(multiple=True)
    report["observations"]["empty_eig_multiple"] = {
        "count": len(zero_values),
        "exception": None,
    }
except Exception as exc:  # noqa: BLE001
    report["observations"]["empty_eig_multiple"] = {
        "count": None,
        "exception": f"{type(exc).__name__}: {exc}",
    }

report["api"] = {
    "arb_has_is_inf": hasattr(flint.arb(1), "is_inf"),
    "arb_has_is_finite": hasattr(flint.arb(1), "is_finite"),
    "arb_mat_has_copy": hasattr(flint.arb_mat(2, 2), "copy"),
}

report["source_sha256"] = {
    "Math30Kernel/IntervalMatrices.py": hashlib.sha256(
        (ROOT / "Math30Kernel" / "IntervalMatrices.py").read_bytes()
    ).hexdigest(),
    "Math30Solvers/IntervalLDLT.py": hashlib.sha256(
        (ROOT / "Math30Solvers" / "IntervalLDLT.py").read_bytes()
    ).hexdigest(),
}

receipt = OUT / "pre_repair_probe.json"
receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
print(f"RECEIPT={receipt}")
