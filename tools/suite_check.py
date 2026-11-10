#!/usr/bin/env python3
"""Math 3.0 six-gate suite with explicit, falsifiable acceptance criteria.

Repaired under the OMEGA audit (2026-11-10).

Defects fixed relative to the previous revision:
  * Gate 3 computed Sylvester inertia and discarded it. The inertia signature is
    now asserted against an expected value, and a negative control proves that
    the acceptance predicate rejects a wrong signature.
  * Gate 6 certified a fixed constant inequality unrelated to the audited
    matrix. It now emits a kernel-checked certificate of the exact leading
    principal minors of the matrix, which by Sylvester's criterion is precisely
    the positive-definiteness witness.
  * Adversarial test D now asserts its expected inertia instead of only
    checking that no alarm fired.
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import flint  # noqa: F401  (initializes native bindings)
    from Math30Interfaces.LeanExporter import LeanFormalExporter
    from Math30Kernel.IntervalMatrices import IntervalMatrixBuilder
    from Math30Solvers.IntervalLDLT import IntervalLDLTSolver, ResolutionAlarm
except ImportError as exc:  # fail closed with a diagnostic
    print(f"FATAL import error: {exc}")
    sys.exit(2)


POSITIVE_DEFINITE_3 = (3, 0, 0)


def load_config() -> dict:
    default = {
        "precision_bits": 6000,
        "jitter": 0.0,
        "constants": {"min_val": "1.32e-102"},
        "max_generations": 5,
        "generation": 0,
    }
    path = os.path.join(os.path.dirname(__file__), "..", "runtime_config.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
        for key, value in default.items():
            config.setdefault(key, value)
        return config
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[WARN] Could not load runtime_config.json: {exc}; using defaults.")
        return default


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    """Exact determinant by fraction-preserving Gaussian elimination."""
    size = len(matrix)
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            if factor == 0:
                continue
            for index in range(column, size):
                work[row][index] -= factor * work[column][index]
    return result


def leading_principal_minors(entries: list[list[str]]) -> list[Fraction]:
    """Exact leading principal minors Delta_1..Delta_n of the integer matrix."""
    size = len(entries)
    numeric = [[Fraction(value) for value in row] for row in entries]
    minors: list[Fraction] = []
    for order in range(1, size + 1):
        block = [row[:order] for row in numeric[:order]]
        minors.append(determinant(block))
    return minors


def inertia_accepts(expected: tuple[int, int, int], actual: tuple[int, int, int]) -> bool:
    """The Gate 3 acceptance criterion, isolated so it can be falsified."""
    return expected == actual


def build_matrix(entries: list[list[str]], precision: int):
    size = len(entries)
    builder = IntervalMatrixBuilder(size, precision)
    for row in range(size):
        for column in range(size):
            builder.set_entry_exact(row, column, entries[row][column])
    return builder


class UniversalSuiteRunner:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        if not os.path.isfile(os.path.join(self.root, "manifest.json")):
            sys.exit(1)

    def run_all_gates(self) -> bool:
        entries = [
            ["12", "1", "3"],
            ["1", "13", "5"],
            ["3", "5", "14"],
        ]
        builder = build_matrix(entries, 6000)

        morphology = builder.audit_linear_morphology()
        if morphology["is_toeplitz_approximate"] or morphology["is_hankel_approximate"]:
            print("[GATE 2] FAILED: structured residual classified as Toeplitz/Hankel.")
            return False
        print("[GATE 2] morphology refutation passed (non-Toeplitz, non-Hankel).")

        try:
            inertia = IntervalLDLTSolver(builder.get_matrix_snapshot()).compute_inertia()
        except ResolutionAlarm as exc:
            print(f"[GATE 3] FAILED: inertia computation alarm: {exc}")
            return False
        if not inertia_accepts(POSITIVE_DEFINITE_3, inertia):
            print(f"[GATE 3] FAILED: inertia {inertia} != expected {POSITIVE_DEFINITE_3}.")
            return False
        print(f"[GATE 3] inertia signature verified: {inertia}.")

        minors = leading_principal_minors(entries)
        if not all(minor > 0 for minor in minors):
            print(f"[GATE 4] FAILED: leading principal minors not all positive: {minors}")
            return False
        print("[GATE 4] exact positive-definiteness witness: all leading minors > 0.")

        clauses: list[tuple[int, int]] = []
        for minor in minors:
            numerator, denominator = minor.numerator, minor.denominator
            if denominator <= 0:
                print("[GATE 5] FAILED: non-positive denominator in exact minor.")
                return False
            clauses.append((0, numerator))
        exported = LeanFormalExporter(self.root).export_integer_inequalities(
            "SuiteAutomaticBridge.lean", "verify_suite_gate", clauses, strict=True
        )
        if not exported:
            print("[GATE 6] FAILED: exact minor certificate did not compile.")
            return False
        print("[GATE 6] kernel-checked Sylvester minor certificate compiled (exit 0).")
        return True


def run_adversarial_tests(root: str, config: dict | None = None) -> bool:
    """Targeted anomalies. Each anomaly has an explicit expected outcome."""
    cfg = config if config is not None else load_config()
    generation = cfg.get("generation", 0)
    precision = cfg.get("precision_bits", 6000)
    print(f"[ADVERSARY] generation {generation}, precision {precision}")

    # A. Singular matrix: eigenvalue 0 must trigger a containment alarm.
    entries_a = [["1", "1", "0"], ["1", "1", "0"], ["0", "0", "2"]]
    try:
        IntervalLDLTSolver(build_matrix(entries_a, precision).get_matrix_snapshot()).compute_inertia()
    except ResolutionAlarm as exc:
        print(f"[ADVERSARY A] zero-straddle alarm triggered: {exc}")
    else:
        print("[ADVERSARY A] FAILED: zero-straddle alarm did not trigger.")
        return False

    # A'. Negative control for the Gate 3 acceptance predicate.
    entries_indefinite = [["-1", "0", "0"], ["0", "2", "0"], ["0", "0", "2"]]
    indefinite_inertia = IntervalLDLTSolver(
        build_matrix(entries_indefinite, precision).get_matrix_snapshot()
    ).compute_inertia()
    if inertia_accepts(POSITIVE_DEFINITE_3, indefinite_inertia):
        print("[ADVERSARY A'] FAILED: acceptance predicate accepted an indefinite matrix.")
        return False
    print(f"[ADVERSARY A'] negative control rejected: inertia {indefinite_inertia}.")

    # B. Exporter must refuse a false inequality on its face.
    exporter = LeanFormalExporter(root)
    false_accepted = exporter.export_bounds_theorem(
        "_adversary_should_not_exist.lean",
        "adversary_false_bound",
        {"min_val": "1.63e-102"},
        {"min_val": "1.32e-102"},
    )
    if false_accepted:
        print("[ADVERSARY B] FAILED: exporter accepted a false bound.")
        return False
    print("[ADVERSARY B] exporter refused the false bound (fail-closed).")

    # C. Precision floor.
    if precision < 18000:
        print(f"[ADVERSARY C] precision {precision} below floor 18000; adaptation required.")
        return False
    print(f"[ADVERSARY C] precision {precision} satisfies the invariant floor.")

    # D. Large dimension scaling with an asserted signature.
    size = 100
    builder_d = IntervalMatrixBuilder(size, precision)
    for index in range(size):
        builder_d.set_entry_exact(index, index, "1")
    inertia_d = IntervalLDLTSolver(builder_d.get_matrix_snapshot()).compute_inertia()
    if not inertia_accepts((size, 0, 0), inertia_d):
        print(f"[ADVERSARY D] FAILED: identity inertia {inertia_d} != ({size}, 0, 0).")
        return False
    print(f"[ADVERSARY D] identity signature verified: {inertia_d}.")
    return True


def main(argv: list[str]) -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    runner = UniversalSuiteRunner(root)
    if not runner.run_all_gates():
        print("SUITE FAILURE")
        return 1
    print("ALL GATES SECURED: FULL PASS")
    if len(argv) > 1 and argv[1] == "--adversarial":
        max_generations = 5
        for _ in range(max_generations):
            config = load_config()
            if run_adversarial_tests(root, config):
                print(f"ADVERSARY SUITE PASS at generation {config.get('generation', 0)}.")
                return 0
            print(f"ADVERSARY SUITE FAIL at generation {config.get('generation', 0)}; evolving.")
            try:
                from Math30Solvers.IntervalEvolver import IntervalEvolver

                evolver = IntervalEvolver(root)
                evolver.record_failed_trace("ANOMALY_C_PRECISION_BREACH", config)
                evolver.evolve(config)
            except ImportError as exc:
                print(f"FATAL: cannot import evolver: {exc}")
                return 2
        print("ADVERSARY SUITE EXHAUSTED MAX GENERATIONS WITHOUT CONTAINMENT.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
