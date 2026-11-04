"""Integrity-locked regression test runner for Math 3.0.
Executes manifesto pre-audit, sequential gate testing pipeline (Gates 1-6),
and compiles forensic Lean proofs, generating reports/regression_master_report.json.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.join(ROOT, "reports")
os.makedirs(REPORTS, exist_ok=True)

def run_cmd(cmd, timeout=300):
    start = time.perf_counter()
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "command": cmd,
        "exit_code": res.returncode,
        "stdout": res.stdout.strip(),
        "stderr": res.stderr.strip(),
        "elapsed_ms": elapsed
    }

def main():
    print("=== MATH 3.0: REGRESSION TEST PIPELINE ===")
    master_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": "REGRESSION_MASTER_CLOSURE",
        "steps": [],
        "verdict": "FAILED"
    }

    # Step 0: Manifest pre-audit
    print("[0/4] Running Manifest Pre-Audit (repokeeper.py)...")
    audit_res = run_cmd(f"python {os.path.join('mcp', 't2n', 'core', 'repokeeper.py')}")
    master_report["steps"].append({"step": "manifest_pre_audit", "result": audit_res})
    if audit_res["exit_code"] != 0:
        print(f"FATAL: Manifest audit failed!\n{audit_res['stderr']}")
        sys.exit(1)
    print("  -> Manifest audit PASSED.")

    # Step 1: Gate 1 & 2 (suite_check.py --adversarial & r_hank check)
    print("[1/4] Running Gate 1 & 2 (suite_check.py --adversarial)...")
    suite_res = run_cmd("python suite_check.py --adversarial")
    # Verify r_hank in lte_spectral_validation.json
    lte_path = os.path.join(REPORTS, "lte_spectral_validation.json")
    with open(lte_path, "r", encoding="utf-8") as f:
        lte_data = json.load(f)
    r_hank_val = lte_data["spectral_analysis"]["r_hank"]
    r_hank_rational = lte_data["spectral_analysis"]["r_hank_rational"]
    r_hank_ok = (r_hank_rational == "25/2" and abs(float(r_hank_val) - 12.5) < 1e-9)

    step1_success = (suite_res["exit_code"] == 0 and r_hank_ok)
    master_report["steps"].append({
        "step": "gate_1_2_spectrum_audit",
        "result": suite_res,
        "r_hank_rational": r_hank_rational,
        "r_hank_numeric": r_hank_val,
        "passed": step1_success
    })
    if not step1_success:
        print("FATAL: Gate 1 & 2 audit failed.")
        sys.exit(1)
    print("  -> Gate 1 & 2 PASSED (r_hank = 25/2).")

    # Step 2: Gate 3 & 4 (newton_box_validator.py)
    print("[2/4] Running Gate 3 & 4 (newton_box_validator.py)...")
    newton_res = run_cmd("python newton_box_validator.py")
    topo_path = os.path.join(REPORTS, "topological_uniqueness.json")
    with open(topo_path, "r", encoding="utf-8") as f:
        topo_data = json.load(f)
    box_data = topo_data["newton_box_contraction"]
    unique_certified = box_data["unique_root_certified"]
    max_ratio = box_data["max_contraction_ratio"]
    step2_success = (newton_res["exit_code"] == 0 and unique_certified and max_ratio < 0.5)
    master_report["steps"].append({
        "step": "gate_3_4_newton_box",
        "result": newton_res,
        "unique_root_certified": unique_certified,
        "max_contraction_ratio": max_ratio,
        "passed": step2_success
    })
    if not step2_success:
        print("FATAL: Gate 3 & 4 Newton box verification failed.")
        sys.exit(1)
    print(f"  -> Gate 3 & 4 PASSED (unique={unique_certified}, max_ratio={max_ratio} < 0.5).")

    # Step 3: Gate 5 & 6 (z3_tribunal.py)
    print("[3/4] Running Gate 5 & 6 (z3_tribunal.py)...")
    z3_res = run_cmd("python z3_tribunal.py")
    z3_report_path = os.path.join(REPORTS, "z3_tribunal_bounds.json")
    with open(z3_report_path, "r", encoding="utf-8") as f:
        z3_data = json.load(f)
    checks_map = {c["path"].split("\\")[-1]: c["result"] for c in z3_data["checks"]}
    sign_flip_ok = (checks_map.get("sign_flip_absence.smt2") == "unsat")
    ledger_ok = (checks_map.get("ledger_cross_multiplication.smt2") == "unsat")
    z3_verdict = z3_data["verdict"] == "PASSED"
    step3_success = (z3_res["exit_code"] == 0 and sign_flip_ok and ledger_ok and z3_verdict)
    master_report["steps"].append({
        "step": "gate_5_6_z3_tribunal",
        "result": z3_res,
        "checks": checks_map,
        "passed": step3_success
    })
    if not step3_success:
        print("FATAL: Gate 5 & 6 Z3 tribunal failed.")
        sys.exit(1)
    print("  -> Gate 5 & 6 PASSED (Z3 QF_LIA verified).")

    # Step 4: Lean 4 Kernel compilation & anti-circularity scan
    print("[4/4] Running Lean 4 Kernel compilation & placeholder audit...")
    lean_file = os.path.join(ROOT, "lean", "spec_v4", "ForensicEvidence.lean")
    with open(lean_file, "r", encoding="utf-8") as f:
        lean_content = f.read()
    has_placeholders = any(w in lean_content for w in ["sorry", "admit", "axiom"])
    lean_res = run_cmd(f"lean {os.path.join('lean', 'spec_v4', 'ForensicEvidence.lean')}")
    step4_success = (lean_res["exit_code"] == 0 and not has_placeholders)
    master_report["steps"].append({
        "step": "lean_4_kernel_audit",
        "result": lean_res,
        "has_placeholders": has_placeholders,
        "passed": step4_success
    })
    if not step4_success:
        print("FATAL: Lean 4 verification failed or placeholders detected.")
        sys.exit(1)
    print("  -> Lean 4 Kernel PASSED (exit 0, zero placeholders).")

    master_report["verdict"] = "FULL PASS"
    report_path = os.path.join(REPORTS, "regression_master_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=2)

    print("========================================")
    print("ALL REGRESSION TESTS PASSED SUCCESSFULLY.")
    print(f"[REPORT SECURED] {report_path}")
    print("========================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
