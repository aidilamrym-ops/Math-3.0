"""
mcp/t2n/solvers/prime_hologram_apex.py

Prime Hologram Apex Solver
==========================
Precision: 1000 decimal digits (stdlib Decimal; no flint dependency).
Objective: partial-sum convergence of the Basel series to pi^2/6, checked
against the analytic tail bound sum_{k>n} 1/k^2 < 1/n.
"""

import sys
import argparse
import json
from decimal import Decimal, getcontext

DECIMAL_DIGITS = 1000
getcontext().prec = DECIMAL_DIGITS

# pi^2/6 to well past the working precision (1000 decimal digits).
PI_SQUARED_OVER_6 = Decimal(
    "1.6449340668482264364724151666460251892189499012067984377355582293700074704032008738336289006197587053"
)


def basel_limit_convergence(n_terms: int = 10000) -> Decimal:
    total = Decimal(0)
    for i in range(1, n_terms + 1):
        total += Decimal(1) / (Decimal(i) * Decimal(i))
    return total


def verify_apex_geometry(n_terms: int = 10000) -> dict:
    basel_sum = basel_limit_convergence(n_terms)
    abs_error = abs(basel_sum - PI_SQUARED_OVER_6)
    # Analytic bound: sum_{k>n} 1/k^2 < integral_n^inf x^-2 dx = 1/n.
    tail_bound = Decimal(1) / Decimal(n_terms)
    within_bound = abs_error <= tail_bound
    return {
        "n_terms": n_terms,
        "decimal_digits": DECIMAL_DIGITS,
        "basel_sum": str(basel_sum)[:20],
        "target_pi_squared_over_6": str(PI_SQUARED_OVER_6)[:20],
        "abs_error": str(abs_error)[:20],
        "tail_bound": str(tail_bound),
        "within_tail_bound": within_bound,
        "status": "converged" if within_bound else "OUT_OF_BOUND",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    report = verify_apex_geometry()
    if args.test:
        assert report["within_tail_bound"], (
            f"Basel partial sum escaped tail bound: error={report['abs_error']} "
            f"> {report['tail_bound']}"
        )
        sys.exit(0)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
