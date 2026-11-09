"""Integrity-locked regression test runner for Math 3.0.
Executes manifesto pre-audit, sequential gate testing pipeline (Gates 1-6),
and compiles forensic Lean proofs, generating reports/regression_master_report.json.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import sys
import json
import subprocess
import time
from datetime import datetime, timezone
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
os.makedirs(REPORTS, exist_ok=True)

def run_cmd(cmd, timeout=300):
    start = time.perf_counter()
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "command": " ".join(cmd),
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
    print("[0/5] Running Manifest Pre-Audit (repokeeper.py)...")
    audit_res = run_cmd([sys.executable, os.path.join('mcp', 't2n', 'core', 'repokeeper.py')])
    master_report["steps"].append({"step": "manifest_pre_audit", "result": audit_res})
    if audit_res["exit_code"] != 0:
        print(f"FATAL: Manifest audit failed!\n{audit_res['stderr']}")
        sys.exit(1)
    print("  -> Manifest audit PASSED.")

    # Step 1: Gate 1 & 2 (suite_check.py --adversarial & r_hank check)
    print("[1/5] Running Gate 1 & 2 (tools/suite_check.py --adversarial)...")
    suite_res = run_cmd([sys.executable, os.path.join('tools', 'suite_check.py'), "--adversarial"])
    # Verify r_hank in lte_spectral_validation.json
    lte_path = os.path.join(REPORTS, "lte_spectral_validation.json")
    with open(lte_path, "r", encoding="utf-8") as f:
        lte_data = json.load(f)
    r_hank_val = lte_data["spectral_analysis"]["r_hank"]
    r_hank_rational = lte_data["spectral_analysis"]["r_hank_rational"]
    r_hank_ok = Fraction(r_hank_rational) == Fraction(25, 2)

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
    print("[2/5] Running Gate 3 & 4 (tools/newton_box_validator.py)...")
    newton_res = run_cmd([sys.executable, os.path.join('tools', 'newton_box_validator.py')])
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
    print("[3/5] Running Gate 5 & 6 (tools/z3_tribunal.py)...")
    z3_res = run_cmd([sys.executable, os.path.join('tools', 'z3_tribunal.py')])
    z3_report_path = os.path.join(REPORTS, "z3_tribunal_bounds.json")
    with open(z3_report_path, "r", encoding="utf-8") as f:
        z3_data = json.load(f)
    checks_map = {os.path.basename(c["path"]): c["result"] for c in z3_data["checks"]}
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

    # Step 4: Full Lean 4 surface compilation & placeholder audit
    print("[4/5] Running full Lean 4 surface audit...")
    lean_receipt = os.path.join(REPORTS, "lean_surface_audit.json")
    lean_res = run_cmd(
        [sys.executable, os.path.join('tools', 'lean_surface_audit.py'),
         "--jobs", "4", "--timeout", "60", "--json", lean_receipt],
        timeout=900,
    )
    try:
        with open(lean_receipt, "r", encoding="utf-8") as f:
            lean_data = json.load(f)
        lean_ok = (
            lean_data.get("verdict") == "PASSED"
            and lean_data.get("failed") == 0
            and lean_data.get("file_count", 0) >= 400
            and not lean_data.get("placeholder_files")
        )
        lean_summary = {
            "file_count": lean_data.get("file_count"),
            "compiled": lean_data.get("compiled"),
            "failed": lean_data.get("failed"),
            "placeholder_files": len(lean_data.get("placeholder_files", [])),
            "verdict": lean_data.get("verdict"),
        }
    except (OSError, json.JSONDecodeError) as error:
        lean_ok = False
        lean_summary = {"error": f"{type(error).__name__}: {error}"}
    step4_success = (lean_res["exit_code"] == 0 and lean_ok)
    master_report["steps"].append({
        "step": "lean_4_surface_audit",
        "result": lean_res,
        "summary": lean_summary,
        "passed": step4_success
    })
    if not step4_success:
        print("FATAL: Lean 4 surface audit failed or placeholders detected.")
        sys.exit(1)
    print(
        f"  -> Lean 4 surface PASSED "
        f"({lean_summary.get('compiled')}/{lean_summary.get('file_count')} files, "
        f"{lean_summary.get('placeholder_files')} placeholder files)."
    )

    # Step 5: Meta-audit of the audit surface itself.
    print("[5/5] Running blind-spot meta-audit (tools/blindspot_audit.py)...")
    blind_receipt = os.path.join(REPORTS, "blindspot_audit.json")
    blind_res = run_cmd(
        [sys.executable, os.path.join('tools', 'blindspot_audit.py')],
        timeout=600,
    )
    try:
        with open(blind_receipt, "r", encoding="utf-8") as f:
            blind_data = json.load(f)
        blind_findings = blind_data.get("findings", [])
        blind_warnings = blind_data.get("warnings", [])
        blind_ok = (
            blind_res["exit_code"] == 0
            and blind_data.get("verdict") == "PASSED"
            and not blind_findings
            and not blind_warnings
        )
        blind_summary = {
            "verdict": blind_data.get("verdict"),
            "findings": len(blind_findings),
            "warnings": len(blind_warnings),
            "lean_files": blind_data.get("stats", {}).get("lean_files"),
            "lean_theorems": blind_data.get("stats", {}).get("lean_theorems"),
            "python_files": blind_data.get("stats", {}).get("python_files"),
        }
    except (OSError, json.JSONDecodeError) as error:
        blind_ok = False
        blind_summary = {"error": f"{type(error).__name__}: {error}"}
    step5_success = blind_ok
    master_report["steps"].append({
        "step": "blindspot_meta_audit",
        "result": blind_res,
        "summary": blind_summary,
        "passed": step5_success
    })
    if not step5_success:
        print("FATAL: blind-spot meta-audit failed or reported warnings.")
        sys.exit(1)
    print(
        f"  -> Blind-spot audit PASSED "
        f"({blind_summary.get('findings')} findings, "
        f"{blind_summary.get('warnings')} warnings, "
        f"{blind_summary.get('lean_files')} Lean files)."
    )

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