#!/usr/bin/env python3
"""Math 3.0 adversarial meta-audit (fail-closed).

This replaces the earlier placeholder hunter that printed ``CONTAINED`` even
when its checks raised.  Every vector now returns an explicit boolean, the
final verdict is derived from the vector results, and a failed vector makes the
process exit non-zero.

Vectors
-------
1. Exact large-integer sign/product integrity near the quantum cut.
2. Interval zero-straddle detection with a real ``arb`` ball.
3. Denominator guard: a zero denominator must be rejected.
4. Verdict aggregation: a report with a failing check must not read PASSED.
5. Placeholder scanner: code ``sorry`` is caught, comment ``sorry`` is not.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
sys.path.insert(0, str(ROOT / "tools"))

from smt_lean_bridge import find_placeholders  # noqa: E402

try:
    import flint
except ImportError:
    print("FATAL: python-flint missing.")
    raise SystemExit(2)


def run_vector(
    name: str,
    check: Callable[[], bool],
    results: list[dict[str, Any]],
) -> None:
    try:
        passed = bool(check())
        detail = "ok" if passed else "check returned false"
    except Exception as error:  # explicit failure capture, never a silent pass
        passed = False
        detail = f"{type(error).__name__}: {error}"
        traceback.print_exc()
    results.append({"vector": name, "passed": passed, "detail": detail})
    print(f"  -> {name}: {'PASS' if passed else 'FAIL'} ({detail})")


def vector_large_integer() -> bool:
    cut = 10**61
    large_num = cut * 777
    large_den = cut * 555
    product = large_num * large_den
    return product > 0 and product % (cut * cut) == 0 and large_num // cut == 777


def vector_zero_straddle() -> bool:
    flint.ctx.prec = 24000
    mid = flint.arb("14.13472514173469379045725198356247")
    eps = flint.arb("1e-9000")
    positive_ball = mid + eps
    cancelled_ball = mid - mid
    return (not positive_ball.contains(0)) and cancelled_ball.contains(0)


def vector_denominator_guard() -> bool:
    def interval_is_valid(lower_num: int, lower_den: int, upper_num: int, upper_den: int) -> bool:
        if lower_den <= 0 or upper_den <= 0:
            return False
        return lower_num * upper_den <= upper_num * lower_den

    return (
        not interval_is_valid(1, 0, 2, 1)
        and not interval_is_valid(1, 1, 2, 0)
        and interval_is_valid(1, 2, 3, 2)
    )


def vector_verdict_aggregation() -> bool:
    def aggregate(checks: list[bool]) -> str:
        return "PASSED" if checks and all(checks) else "FAILED"

    return aggregate([True, True]) == "PASSED" and aggregate([True, False]) == "FAILED" and aggregate([]) == "FAILED"


def vector_placeholder_scanner() -> bool:
    code = "theorem bad : True := by\n  sorry\n"
    comment = "-- sorry is only a comment here\ntheorem ok : True := by\n  trivial\n"
    return bool(find_placeholders(code)) and not find_placeholders(comment)


def main() -> int:
    print("=== MATH 3.0 ADVERSARIAL META-AUDIT ===")
    results: list[dict[str, Any]] = []
    run_vector("large_integer", vector_large_integer, results)
    run_vector("zero_straddle", vector_zero_straddle, results)
    run_vector("denominator_guard", vector_denominator_guard, results)
    run_vector("verdict_aggregation", vector_verdict_aggregation, results)
    run_vector("placeholder_scanner", vector_placeholder_scanner, results)

    passed = bool(results) and all(item["passed"] for item in results)
    verdict = "PASSED" if passed else "FAILED"
    report = {
        "audit": "math30_adversarial_meta_audit",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "precision_bits": 24000,
        "vectors": results,
        "verdict": verdict,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS / "meta_blindspot_audit.json"
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"VERDICT: {report['verdict']}")
    print(f"receipt: {out_path}")
    return 0 if verdict == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
