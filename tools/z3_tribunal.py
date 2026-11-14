"""Phase 4: Sylvester inertia reduction and Z3 SMT tribunal over the
Phase 3 rational Newton-box ledger.

Every bound is converted to an exact integer lattice at scale 10^18.
Z3 is asked to refute the existence of a violating lattice point.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

import z3

sys.set_int_max_str_digits(100000)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
SMT_DIR = os.path.join(ROOT, "smt", "phase4")
SCALE = 10 ** 18


def parse_ball(text):
    """Exact rational midpoint of an arb-style '[value +/- err]' literal."""
    body = text.strip()
    if body.startswith("["):
        body = body[1:]
    if body.endswith("]"):
        body = body[:-1]
    main = body.split("+/-")[0].strip()
    return Fraction(main)


def latent(interval):
    """Closed integer lattice enclosing the rational interval at SCALE."""
    return math.ceil(interval[0] * SCALE), math.floor(interval[1] * SCALE)


def build_sign_flip_script(boxes):
    lines = [
        "; Phase 4 / Gate 3: no sign flip inside the three certified eigenvalue boxes.",
        "; Variables are eigenvalue numerators on the closed lattice e/10^18.",
        "(set-logic QF_LIA)",
        "(set-option :produce-models true)",
    ]
    for i, (lo, hi) in enumerate(boxes):
        lines.append(f"(declare-const e{i} Int)")
        lines.append(f"(assert (and (<= {lo} e{i}) (<= e{i} {hi})))")
    disj = " ".join(f"(<= e{i} 0)" for i in range(len(boxes)))
    lines.append(f"(assert (or {disj}))")
    lines.append("(check-sat)")
    return "\n".join(lines) + "\n"


def build_contraction_script(limits):
    lines = [
        "; Phase 4 / Gate 3: every contraction numerator on the closed lattice",
        "; [0, ceil(max_ratio*10^18)] stays strictly below 1/2.",
        "(set-logic QF_LIA)",
        "(set-option :produce-models true)",
    ]
    for i, cap in enumerate(limits):
        lines.append(f"(declare-const c{i} Int)")
        lines.append(f"(assert (and (<= 0 c{i}) (<= c{i} {cap})))")
    disj = " ".join(f"(>= (* 2 c{i}) {SCALE})" for i in range(len(limits)))
    lines.append(f"(assert (or {disj}))")
    lines.append("(check-sat)")
    return "\n".join(lines) + "\n"


def build_ledger_script(entries):
    lines = [
        "; Phase 4 / Gate 3: exact rational ledger cross-multiplication.",
        "; Refutes any contraction >= 1/2 or non-positive box lower endpoint.",
        "(set-logic QF_LIA)",
    ]
    disj = []
    for entry in entries:
        num = entry["contraction_numerator"]
        den = entry["contraction_denominator"]
        low_num = entry["lower_endpoint_numerator"]
        low_den = entry["lower_endpoint_denominator"]
        lines.append(f"(assert (> {den} 0))")
        lines.append(f"(assert (> {low_den} 0))")
        disj.append(f"(>= (* 2 {num}) {den})")
        disj.append(f"(<= {low_num} 0)")
    lines.append(f"(assert (or {' '.join(disj)}))")
    lines.append("(check-sat)")
    return "\n".join(lines) + "\n"


def build_witness_script(boxes, mids, limits):
    lines = [
        "; Phase 4 / Gate 3: SAT witness proving each closed lattice is nonempty",
        "; and carries a strict contraction certificate.",
        "(set-logic QF_LIA)",
        "(set-option :produce-models true)",
    ]
    for i, (lo, hi) in enumerate(boxes):
        lines.append(f"(declare-const e{i} Int)")
        lines.append(f"(assert (and (<= {lo} e{i}) (<= e{i} {hi})))")
        lines.append(f"(assert (= e{i} {mids[i]}))")
    for i, cap in enumerate(limits):
        lines.append(f"(declare-const c{i} Int)")
        lines.append(f"(assert (= c{i} {cap}))")
        lines.append(f"(assert (< (* 2 c{i}) {SCALE}))")
    lines.append("(check-sat)")
    lines.append("(get-model)")
    return "\n".join(lines) + "\n"


def execute(path, script, expect, logic="QF_LIA"):
    solver = z3.Solver()
    solver.from_string(script)
    started = time.perf_counter()
    result = solver.check()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    verdict = str(result)
    if verdict != expect:
        raise SystemExit(f"{path}: expected {expect}, got {verdict}")
    model = str(solver.model()) if result == z3.sat else None
    return {
        "path": path,
        "logic": logic,
        "expected": expect,
        "result": verdict,
        "elapsed_ms": elapsed_ms,
        "model": model,
        "script": script,
    }


def main():
    with open(os.path.join(REPORTS, "topological_uniqueness.json"), "r", encoding="utf-8") as f:
        phase3 = json.load(f)
    with open(os.path.join(REPORTS, "lte_spectral_validation.json"), "r", encoding="utf-8") as f:
        phase2 = json.load(f)

    pivots2 = phase2["spectral_analysis"]["pivots"]
    assert all(p["signed_definite"] and not p["contains_zero"] for p in pivots2)

    box = phase3["newton_box_contraction"]
    ledger = phase3["lean_evidence"]["parameters"]

    intervals = []
    mids = []
    limits = []
    for index, pivot in enumerate(box["pivots"]):
        mid = parse_ball(pivot["eigenvalue_midpoint"])
        rad = parse_ball(pivot["eigenvalue_radius"])
        intervals.append((mid - rad, mid + rad))
        mids.append(math.floor(mid * SCALE))
        entry = ledger["pivots"][index]
        ratio = Fraction(entry["contraction_numerator"], entry["contraction_denominator"])
        limits.append(math.ceil(ratio * SCALE))
        assert Fraction(entry["lower_endpoint_numerator"], entry["lower_endpoint_denominator"]) > 0

    boxes = [latent(interval) for interval in intervals]
    for (lo, hi) in boxes:
        assert lo <= hi, "empty eigenvalue lattice"
        assert lo > 0, "lattice crosses zero"

    os.makedirs(SMT_DIR, exist_ok=True)
    scripts = {
        "sign_flip_absence": build_sign_flip_script(boxes),
        "contraction_bound": build_contraction_script(limits),
        "ledger_cross_multiplication": build_ledger_script(ledger["pivots"]),
        "box_feasibility_witness": build_witness_script(boxes, mids, limits),
    }
    expected = {
        "sign_flip_absence": "unsat",
        "contraction_bound": "unsat",
        "ledger_cross_multiplication": "unsat",
        "box_feasibility_witness": "sat",
    }

    checks = []
    for name, script in scripts.items():
        path = os.path.join(SMT_DIR, f"{name}.smt2")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(script)
        check = execute(path, script, expected[name])
        log_lines = [f"$ {path}", "(check-sat)", check["result"]]
        if check["model"]:
            log_lines.append(check["model"])
        with open(os.path.join(SMT_DIR, f"{name}.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(log_lines) + "\n")
        checks.append(check)

    # Static SMT-LIB2 refutation scripts shipped in smt/phase4.  These are not
    # regenerated from the Phase 2/3 ledgers, but the regression suite asserts
    # their verdicts, so they must be executed by the tribunal rather than
    # assumed.
    static_scripts = {
        "gate5_rational_leakage_refutation": ("unsat", "QF_NRA"),
        "twistor_googly_refutation": ("unsat", "QF_NRA"),
        "yang_mills_refutation": ("unsat", "QF_NRA"),
        "actual_infinity_refutation": ("unsat", "QF_LIA"),
        "continuity_refutation": ("unsat", "QF_LIA"),
    }
    for name, (expect, logic) in static_scripts.items():
        path = os.path.join(SMT_DIR, f"{name}.smt2")
        if not os.path.isfile(path):
            raise SystemExit(f"{path}: missing static tribunal script")
        with open(path, "r", encoding="utf-8") as f:
            script = f.read()
        check = execute(path, script, expect, logic=logic)
        check["kind"] = "static_script"
        log_lines = [f"$ {path}", "(check-sat)", check["result"]]
        if check["model"]:
            log_lines.append(check["model"])
        with open(os.path.join(SMT_DIR, f"{name}.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(log_lines) + "\n")
        checks.append(check)

    verdict = "PASSED" if all(c["result"] == c["expected"] for c in checks) else "FAILED"
    report = {
        "phase": "PHASE_4_SYLVESTER_INERTIA_REDUCTION_Z3_TRIBUNAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "name": "Z3",
            "version": z3.get_version_string(),
            "binding": z3.__file__,
            "native_library": os.path.join(os.path.dirname(z3.__file__), "lib", "libz3.dll"),
            "logic": "QF_LIA",
            "lattice_scale": SCALE,
        },
        "source_ledger": {
            "path": os.path.join(REPORTS, "topological_uniqueness.json"),
            "max_contraction_ratio": box["max_contraction_ratio"],
            "unique_root_certified": box["unique_root_certified"],
            "boundary_escape": box["boundary_escape"],
        },
        "sylvester_inertia": {
            "source": os.path.join(REPORTS, "lte_spectral_validation.json"),
            "positive_pivots": len(pivots2),
            "negative_pivots": 0,
            "zero_pivots": 0,
            "signature": [len(pivots2), 0, 0],
        },
        "scope": (
            "Quantifier-free integer lattice proof at scale 10^18 over the "
            "conservative Phase 3 boxes e_i +/- r_i. Results are conditional on "
            "those boxes enclosing the Phase 2 eigenvalues; they do not re-prove "
            "the enclosure itself."
        ),
        "eigenvalue_lattices": [
            {
                "index": i,
                "rational_lower": str(intervals[i][0]),
                "rational_upper": str(intervals[i][1]),
                "lattice_lower": boxes[i][0],
                "lattice_upper": boxes[i][1],
            }
            for i in range(len(intervals))
        ],
        "contraction_lattice_caps": limits,
        "checks": checks,
        "raw_log": [
            line
            for check in checks
            for line in (
                [f"$ {check['path']}", "(check-sat)", check["result"]]
                + ([check["model"]] if check["model"] else [])
            )
        ],
        "verdict": verdict,
    }

    out_path = os.path.join(REPORTS, "z3_tribunal_bounds.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=== PHASE 4: Z3 SMT TRIBUNAL ===")
    print(f"Z3 {z3.get_version_string()}  logic=QF_LIA+QF_NRA  scale=10^18")
    for check in checks:
        print(f"[{os.path.basename(check['path'])}] -> {check['result']} ({check['elapsed_ms']} ms)")
        if check["model"]:
            print(check["model"])
    print(f"VERDICT: {verdict}")
    print(f"[REPORT SECURED] {out_path}")


if __name__ == "__main__":
    main()