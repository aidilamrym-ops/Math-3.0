from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder
from Math30Solvers.IntervalLDLT import IntervalLDLTSolver


def build(entries: list[list[str]], precision: int = 6000):
    size = len(entries)
    builder = IntervalMatrixBuilder(size, precision)
    for row in range(size):
        for column in range(size):
            builder.set_entry_exact(row, column, entries[row][column])
    return builder


def run(label: str, entries: list[list[str]]) -> None:
    print(f"== {label}")
    try:
        matrix = build(entries).get_matrix_snapshot()
        print(f"   shape={matrix.nrows()}x{matrix.ncols()}")
        try:
            eigenvalues = matrix.eig(nonstop=True)
            preview = [str(item.real)[:48] for item in eigenvalues[:4]]
            print(f"   eig_count={len(eigenvalues)} preview={preview}")
        except Exception as exc:  # noqa: BLE001 - probe wants the exact failure
            print(f"   eig_EXC={type(exc).__name__}: {exc}")
        try:
            inertia = IntervalLDLTSolver(matrix).compute_inertia()
            print(f"   inertia={inertia}")
        except Exception as exc:  # noqa: BLE001
            print(f"   inertia_EXC={type(exc).__name__}: {exc}")
    except Exception as exc:  # noqa: BLE001
        print(f"   build_EXC={type(exc).__name__}: {exc}")


run("empty_0x0", [])
run("one_by_one_positive", [["2"]])
run("one_by_one_negative", [["-2"]])
run("one_by_one_zero", [["0"]])
run("one_by_one_near_zero", [["1e-100"]])
run("one_by_one_zero_straddle", [["0"]])
run(
    "singular_3x3_diag_1_1_0",
    [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "0"]],
)
run("mixed_inertia_diag", [["-1", "0", "0"], ["0", "2", "0"], ["0", "0", "2"]])
run("non_symmetric", [["1", "2"], ["0", "1"]])
run(
    "symmetric_indefinite_tridiag_16",
    [
        [("0" if row == column else ("1" if abs(row - column) == 1 else "0"))
         for column in range(16)]
        for row in range(16)
    ],
)
run("near_zero_pivot_2x2", [["1", "1"], ["1", "1.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001"]])
run("interval_diagonal_positive", [["1", "0"], ["0", "1"]])
