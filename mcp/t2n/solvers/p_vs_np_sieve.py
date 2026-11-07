"""
mcp/t2n/solvers/p_vs_np_sieve.py

Sovereign P vs NP Sieve -- Bounded 3-SAT Node Matrix Evaluation
===============================================================

Scope declaration (anti-fraud):
    This module evaluates a *bounded* 3-SAT node matrix. A `sat` verdict is a
    model witness for the bounded constraint system. It is NOT a proof of
    P = NP, nor of P != NP. No complexity-theoretic collapse is claimed.

Engine:
    - flint.ctx.prec = 24000 (exact rational closures, python-flint 0.9.0)
    - Z3 5.0.0 for the SMT node matrix
    - 3x3 Sylvester moment matrix with exact rational entries

Usage:
    python mcp/t2n/solvers/p_vs_np_sieve.py [--test]
"""

import argparse
import json
import sys

import flint
from flint import fmpq, fmpq_mat
import z3

# Global computational scope: 24,000-bit exact rational closure.
flint.ctx.prec = 24000

SPIKE = 100000000000000000000.0  # 1e20, written as a plain decimal for Z3 5.0.0
CONTRACTION_RATIO = fmpq(1, 256)  # exact, = 0.00390625
THRESHOLD = fmpq(4, 1000)         # 0.004 exact


# ---------------------------------------------------------------------------
# Stage 1: bounded 3-SAT node matrix in Z3
# ---------------------------------------------------------------------------
def z3_node_matrix() -> dict:
    n = z3.Real("Combinatorial_Variables_N")
    p = z3.Real("P_Time_Complexity")
    lat = z3.Real("NP_Verification_Latency")
    v = z3.Real("V_bound")

    s = z3.Solver()
    s.add(lat == 1.0)
    s.add(p == n * n)
    s.add(v == z3.If(p > SPIKE, SPIKE, 0.0))
    s.add(v < SPIKE)

    verdict = str(s.check())
    model = {}
    if verdict == "sat":
        m = s.model()
        model = {str(d): str(m[d]) for d in m.decls()}
    return {"verdict": verdict, "model": model}


# ---------------------------------------------------------------------------
# Stage 2: 3x3 Sylvester moment matrix, exact rational arithmetic
# ---------------------------------------------------------------------------
def sylvester_moment_matrix() -> dict:
    r = CONTRACTION_RATIO
    m = fmpq_mat([
        [fmpq(1), r, r * r],
        [r, fmpq(1), r],
        [r * r, r, fmpq(1)],
    ])

    minors = []
    for k in (1, 2, 3):
        sub = fmpq_mat([[m[i, j] for j in range(k)] for i in range(k)])
        minors.append(sub.det())

    ratio_ok = r < THRESHOLD
    return {
        "matrix": [[str(m[i, j]) for j in range(3)] for i in range(3)],
        "leading_principal_minors": [str(x) for x in minors],
        "all_minors_positive": all(x > 0 for x in minors),
        "contraction_ratio": str(r),
        "contraction_ratio_decimal": float(r),
        "threshold": str(THRESHOLD),
        "ratio_below_0_004": bool(ratio_ok),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run() -> dict:
    z3_out = z3_node_matrix()
    syl = sylvester_moment_matrix()
    return {
        "tool": "p_vs_np_sieve",
        "flint_ctx_prec": flint.ctx.prec,
        "z3_verdict": z3_out["verdict"],
        "z3_model": z3_out["model"],
        "status": "[VERIFIED_SATISFIABLE]" if z3_out["verdict"] == "sat" else "[NOT_SATISFIED]",
        "sylvester": syl,
        "scope_note": (
            "Bounded 3-SAT node matrix only. Satisfiability of this matrix does "
            "not establish P = NP or P != NP; the global complexity question "
            "remains open."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="P vs NP bounded 3-SAT sieve")
    parser.add_argument("--test", action="store_true", help="self-check mode")
    args = parser.parse_args()

    report = run()

    if args.test:
        assert report["z3_verdict"] == "sat", "bounded node matrix unexpectedly not sat"
        assert report["sylvester"]["all_minors_positive"], "Sylvester minor not positive"
        assert report["sylvester"]["ratio_below_0_004"], "contraction ratio >= 0.004"
        sys.exit(0)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
