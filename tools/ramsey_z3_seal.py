"""Regenerate the Z3 transcript for the Ramsey R(3,3) degree-cap bridge.

Runs `smt/phase4/ramsey_clique_bound.smt2` through Z3 and writes the sidecar
`ramsey_clique_bound.log` that the anti-circularity `claim` gate requires.

Usage:
    C:\\Python314\\python.exe tools\\ramsey_z3_seal.py
"""

import os

import z3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "smt", "phase4", "ramsey_clique_bound.smt2")


def main():
    solver = z3.Solver()
    solver.from_file(SCRIPT)
    result = solver.check()
    print("result =", result)

    log_path = SCRIPT[:-5] + ".log"
    lines = ["$ " + SCRIPT, "(check-sat)", str(result)]
    with open(log_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print("wrote", log_path)


if __name__ == "__main__":
    main()
