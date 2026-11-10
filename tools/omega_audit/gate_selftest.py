#!/usr/bin/env python3
"""Executable falsification tests for the Math 3.0 strict gate.

Each case is a Lean file under reports/omega_audit/falsification/ with a known
trust status. The test runs the real strict gate as a subprocess and asserts
the exit code. This is the evidence that the gate rejects the evasion vectors
recorded in OMEGA-0013/OMEGA-0014, and that it still accepts clean files.

Usage:
  python tools/omega_audit/gate_selftest.py
  python tools/omega_audit/gate_selftest.py --surface   # also sweep Lean roots
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tools" / "omega_audit" / "gate_strict.py"
FIXTURES = ROOT / "reports" / "omega_audit" / "falsification"

# Expected exit codes: 0 = clean, 1 = trust token must be rejected.
CASES = (
    ("fixture_clean.lean", 0),
    ("fixture_comment_clean.lean", 0),
    ("fixture_g_plain_sorry.lean", 1),
    ("fixture_h_plain_axiom.lean", 1),
    ("fixture_c_private_axiom.lean", 1),
    ("fixture_d_attributed_axiom.lean", 1),
    ("fixture_e_sorryax.lean", 1),
    ("fixture_f_string_line_comment.lean", 1),
    ("fixture_a_constant.lean", 1),
)


def run_gate(path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(GATE), "check", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strict-gate falsification tests")
    parser.add_argument(
        "--surface",
        action="store_true",
        help="also sweep lean/spec_v4, Math30Kernel and Math30Interfaces",
    )
    args = parser.parse_args(argv)

    failures = 0
    print("=== MATH 3.0 STRICT GATE SELF-TEST ===")
    for name, expected in CASES:
        path = FIXTURES / name
        if not path.is_file():
            print("[MISSING] %s" % path)
            failures += 1
            continue
        actual, output = run_gate(path)
        ok = actual == expected
        print(
            "[%s] %s expected_exit=%d actual_exit=%d"
            % ("OK" if ok else "FAIL", name, expected, actual)
        )
        if not ok:
            failures += 1
            for line in output.splitlines():
                if "FAIL" in line or "verdict:" in line:
                    print("        %s" % line)

    if args.surface:
        proc = subprocess.run(
            [
                sys.executable,
                str(GATE),
                "check",
                "lean/spec_v4",
                "Math30Kernel",
                "Math30Interfaces",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        ok = proc.returncode == 0
        print("[%s] surface sweep exit=%d" % ("OK" if ok else "FAIL", proc.returncode))
        if not ok:
            failures += 1
            for line in ((proc.stdout or "") + (proc.stderr or "")).splitlines():
                if "FAIL" in line or "verdict:" in line:
                    print("        %s" % line)

    print("SELF-TEST RESULT: %s (%d failures)" % ("PASS" if failures == 0 else "FAIL", failures))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
