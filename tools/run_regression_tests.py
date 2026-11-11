"""Integrity-locked regression test runner for Math 3.0.

Repaired 2026-11-10 under the OMEGA audit. The defects fixed here were:

  * Step 0 called ``repokeeper.py`` without ``--verify``. That *rewrote* the
    manifest instead of auditing it, so the "pre-audit" could never fail and
    silently erased any tampering. It now runs ``--verify`` and the independent
    verifier.
  * Every failure path called ``sys.exit(1)`` before the report was written,
    leaving the previous ``FULL PASS`` report on disk. The report is now
    written on every path, including failures.
  * Step 1 read ``reports/lte_spectral_validation.json`` without regenerating
    it, and compared a hard-coded ``"25/2"`` field to 25/2. It now runs the
    validator and checks the computed enclosure, pivot signs, and receipt
    freshness. The old check was a tautology.
  * Steps used the receipt timestamp, which is hard-coded in the Z3 tribunal;
    freshness is now measured by the receipt file's mtime before/after the
    generating command.
  * Step 4 ran a bare ``lean`` from the repository root. Files importing
    Mathlib fail there with ``unknown module prefix 'Mathlib'``. The surface
    audit now compiles through ``lake env lean`` (repaired in the same batch).
  * The runner never invoked the anti-circularity gate. A repo-wide strict
    sweep is now a first-class step.

The runner verifies the manifest at the start. The receipts it writes make the
ledger stale by design; reseal with ``python mcp/t2n/core/repokeeper.py`` and
verify with ``--verify`` afterwards.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REGRESSION_REPORT = REPORTS / "regression_master_report.json"

LEAN_ROOTS = ("lean", "Math30Kernel", "Math30Interfaces")
LEAN_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".lake",
    "staging",
    "fixtures",
    "repaired",
}

LTE_RECEIPT = REPORTS / "lte_spectral_validation.json"
NEWTON_RECEIPT = REPORTS / "topological_uniqueness.json"
GATE5_RECEIPT = REPORTS / "gate5_rational_extraction.json"
GATE5_CERT = ROOT / "lean/spec_v4/Gate5RationalExtractionValidation.lean"
GATE5_BRIDGE = ROOT / "lean/spec_v4/Gate5RationalBridge.lean"
Z3_RECEIPT = REPORTS / "z3_tribunal_bounds.json"
LEAN_RECEIPT = REPORTS / "lean_surface_audit.json"
BLINDSPOT_RECEIPT = REPORTS / "blindspot_audit.json"
GATE_RECEIPT = REPORTS / "anti_circularity_gate.json"

Z3_EXPECTED = {
    "sign_flip_absence.smt2": "unsat",
    "contraction_bound.smt2": "unsat",
    "ledger_cross_multiplication.smt2": "unsat",
    "box_feasibility_witness.smt2": "sat",
    "gate5_rational_leakage_refutation.smt2": "unsat",
    "twistor_googly_refutation.smt2": "unsat",
    "yang_mills_refutation.smt2": "unsat",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tail(text: str, limit: int = 4000) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else "..." + text[-limit:]


def run_cmd(command: list[object], timeout: int) -> dict:
    """Run a command and always return a structured result (never raise)."""
    started = time.perf_counter()
    display = [str(part) for part in command]
    try:
        proc = subprocess.run(
            display,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        return {
            "command": display,
            "exit_code": None,
            "timed_out": True,
            "stdout": tail(stdout),
            "stderr": tail(stderr or "timeout after %ss" % timeout),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    except OSError as error:
        return {
            "command": display,
            "exit_code": None,
            "timed_out": False,
            "stdout": "",
            "stderr": "%s: %s" % (type(error).__name__, error),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    return {
        "command": display,
        "exit_code": proc.returncode,
        "timed_out": False,
        "stdout": tail(proc.stdout or ""),
        "stderr": tail(proc.stderr or ""),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def load_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {"__error__": "top level is not an object"}
    except (OSError, json.JSONDecodeError) as error:
        return {"__error__": "%s: %s" % (type(error).__name__, error)}


def mtime_ns(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return 0


def sha256_file(path: Path) -> str | None:
    try:
        import hashlib

        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def discover_lean() -> list[Path]:
    files: set[Path] = set()
    for base in LEAN_ROOTS:
        base_path = ROOT / base
        if not base_path.is_dir():
            continue
        for current, dirnames, filenames in os.walk(base_path):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in LEAN_EXCLUDED_PARTS and not name.startswith(".")
            ]
            for name in filenames:
                if name.endswith(".lean"):
                    files.add(Path(current) / name)
    return sorted(files)


def step_manifest() -> dict:
    repokeeper = run_cmd(
        [sys.executable, "mcp/t2n/core/repokeeper.py", "--verify"], 1800
    )
    independent = run_cmd(
        [sys.executable, "tools/omega_audit/manifest_verify.py"], 1800
    )
    checks = {
        "repokeeper_verify_ok": repokeeper["exit_code"] == 0,
        "independent_verify_ok": independent["exit_code"] == 0,
    }
    return {
        "step": "manifest",
        "passed": all(checks.values()),
        "checks": checks,
        "results": [repokeeper, independent],
    }


def step_spectrum() -> dict:
    suite = run_cmd([sys.executable, "tools/suite_check.py", "--adversarial"], 1800)
    before = mtime_ns(LTE_RECEIPT)
    lte = run_cmd([sys.executable, "tools/lte_spectral_validator.py"], 1800)
    after = mtime_ns(LTE_RECEIPT)
    data = load_json(LTE_RECEIPT)
    spectral = data.get("spectral_analysis") or {}
    pivots = spectral.get("pivots") or []
    checks = {
        "suite_exit_zero": suite["exit_code"] == 0,
        "lte_exit_zero": lte["exit_code"] == 0,
        "lte_receipt_rewritten": after > before,
        "rigid_asymmetry_certified": spectral.get("rigid_asymmetry_certified") is True,
        "zero_straddle_absent": spectral.get("zero_straddle_detected") is False,
        "three_pivots": len(pivots) == 3,
        "all_pivots_positive": bool(pivots)
        and all(
            pivot.get("signed_definite") is True
            and pivot.get("contains_zero") is False
            for pivot in pivots
        ),
    }
    return {
        "step": "spectrum",
        "passed": all(checks.values()),
        "checks": checks,
        "r_hank": spectral.get("r_hank"),
        "r_hank_target_rational": spectral.get("r_hank_target_rational"),
        "r_hank_target_contained": spectral.get("r_hank_target_contained"),
        "precision_bits": spectral.get("precision_bits"),
        "receipt_error": data.get("__error__"),
        "results": [suite, lte],
    }


def step_newton_box() -> dict:
    before = mtime_ns(NEWTON_RECEIPT)
    newton = run_cmd([sys.executable, "tools/newton_box_validator.py"], 1800)
    after = mtime_ns(NEWTON_RECEIPT)
    data = load_json(NEWTON_RECEIPT)
    box = data.get("newton_box_contraction") or {}
    pivots = box.get("pivots") or []
    ratio = box.get("max_contraction_ratio")
    checks = {
        "newton_exit_zero": newton["exit_code"] == 0,
        "receipt_rewritten": after > before,
        "unique_root_certified": box.get("unique_root_certified") is True,
        "boundary_escape_absent": box.get("boundary_escape") is False,
        "three_pivots": len(pivots) == 3,
        "all_strict_inclusion": bool(pivots)
        and all(pivot.get("strict_inclusion") is True for pivot in pivots),
        "max_ratio_below_half": isinstance(ratio, (int, float))
        and not isinstance(ratio, bool)
        and 0 <= ratio < 0.5,
    }
    return {
        "step": "newton_box",
        "passed": all(checks.values()),
        "checks": checks,
        "max_contraction_ratio": ratio,
        "receipt_error": data.get("__error__"),
        "results": [newton],
    }


def step_rational_extraction() -> dict:
    before_receipt = mtime_ns(GATE5_RECEIPT)
    before_cert = mtime_ns(GATE5_CERT)
    generator = run_cmd([sys.executable, "tools/gate5_rational_extraction.py"], 3600)
    after_receipt = mtime_ns(GATE5_RECEIPT)
    after_cert = mtime_ns(GATE5_CERT)
    data = load_json(GATE5_RECEIPT)
    certificate = data.get("certificate") or {}
    sources = data.get("sources") or {}
    bridge = data.get("bridge") or {}
    compile_info = data.get("compile") or {}
    source_audit = data.get("source_audit") or {}
    lte_source = sources.get("lte_spectral_validation") or {}
    newton_source = sources.get("topological_uniqueness") or {}
    theorem_names = certificate.get("theorem_names") or []
    try:
        certificate_text = GATE5_CERT.read_text(encoding="utf-8")
    except OSError:
        certificate_text = ""
    imports = [
        line.strip()
        for line in certificate_text.splitlines()
        if line.strip().startswith("import ")
    ]
    checks = {
        "generator_exit_zero": generator["exit_code"] == 0,
        "receipt_rewritten": after_receipt > before_receipt,
        "certificate_rewritten": after_cert > before_cert,
        "verdict_passed": data.get("verdict") == "PASSED",
        "compile_exit_zero": compile_info.get("exit_code") == 0,
        "compile_not_timed_out": compile_info.get("timed_out") is False,
        "certificate_hash_matches": certificate.get("sha256") == sha256_file(GATE5_CERT),
        "lte_source_hash_matches": lte_source.get("sha256") == sha256_file(LTE_RECEIPT),
        "newton_source_hash_matches": newton_source.get("sha256") == sha256_file(NEWTON_RECEIPT),
        "bridge_hash_matches": bridge.get("sha256") == sha256_file(GATE5_BRIDGE),
        "three_lte_pivots": lte_source.get("pivots") == 3,
        "three_newton_pivots": newton_source.get("pivots") == 3,
        "eighteen_definitions": certificate.get("definitions") == 18,
        "thirty_six_theorems": certificate.get("theorems") == 36,
        "all_named_theorems_present": len(theorem_names) == 36
        and all(name in certificate_text for name in theorem_names),
        "no_decimal_literals": source_audit.get("decimal_literals") == 0,
        "no_placeholder_tokens": source_audit.get("placeholder_tokens") == 0,
        "no_axiom_declarations": source_audit.get("axiom_declarations") == 0,
        "mathlib_only_imports": bool(imports)
        and all(line.startswith("import Mathlib") for line in imports),
        "independent_decimal_scan_clean": re.search(r"(?<![\w.])\d+\.\d+", certificate_text)
        is None,
        "independent_placeholder_scan_clean": re.search(
            r"\b(?:sorry|admit|native_decide)\b", certificate_text
        )
        is None,
        "gate_checks_all_true": isinstance(data.get("checks"), dict)
        and bool(data["checks"])
        and all(value is True for value in data["checks"].values()),
    }
    return {
        "step": "rational_extraction",
        "passed": all(checks.values()),
        "checks": checks,
        "certificate": str(GATE5_CERT.relative_to(ROOT)),
        "certificate_sha256": certificate.get("sha256"),
        "compile_elapsed_s": compile_info.get("elapsed_s"),
        "receipt_error": data.get("__error__"),
        "results": [generator],
    }


def step_z3() -> dict:
    before = mtime_ns(Z3_RECEIPT)
    tribunal = run_cmd([sys.executable, "tools/z3_tribunal.py"], 1800)
    after = mtime_ns(Z3_RECEIPT)
    data = load_json(Z3_RECEIPT)
    checks_list = data.get("checks") or []
    observed: dict[str, object] = {}
    for check in checks_list:
        name = os.path.basename(str(check.get("path", "")))
        observed[name] = check.get("result")
    checks = {
        "z3_exit_zero": tribunal["exit_code"] == 0,
        "receipt_rewritten": after > before,
        "verdict_passed": data.get("verdict") == "PASSED",
        "exactly_four_checks": len(checks_list) == 4,
    }
    for name, expected in Z3_EXPECTED.items():
        checks["%s_is_%s" % (name, expected)] = observed.get(name) == expected
    return {
        "step": "z3_tribunal",
        "passed": all(checks.values()),
        "checks": checks,
        "observed": observed,
        "receipt_error": data.get("__error__"),
        "results": [tribunal],
    }


def step_lean_surface() -> dict:
    files = discover_lean()
    before = mtime_ns(LEAN_RECEIPT)
    audit = run_cmd(
        [
            sys.executable,
            "tools/lean_surface_audit.py",
            "--jobs",
            "2",
            "--timeout",
            "600",
            "--json",
            str(LEAN_RECEIPT),
        ],
        10800,
    )
    after = mtime_ns(LEAN_RECEIPT)
    data = load_json(LEAN_RECEIPT)
    checks = {
        "audit_exit_zero": audit["exit_code"] == 0,
        "receipt_rewritten": after > before,
        "verdict_passed": data.get("verdict") == "PASSED",
        "failed_zero": data.get("failed") == 0,
        "compiled_equals_file_count": data.get("compiled") == data.get("file_count"),
        "file_count_matches_discovery": data.get("file_count") == len(files),
        "no_placeholder_files": not data.get("placeholder_files"),
    }
    return {
        "step": "lean_surface",
        "passed": all(checks.values()),
        "checks": checks,
        "discovered_files": len(files),
        "receipt_file_count": data.get("file_count"),
        "receipt_error": data.get("__error__"),
        "results": [audit],
    }


def step_blindspot() -> dict:
    before = mtime_ns(BLINDSPOT_RECEIPT)
    audit = run_cmd([sys.executable, "tools/blindspot_audit.py"], 1800)
    after = mtime_ns(BLINDSPOT_RECEIPT)
    data = load_json(BLINDSPOT_RECEIPT)
    checks = {
        "audit_exit_zero": audit["exit_code"] == 0,
        "receipt_rewritten": after > before,
        "verdict_passed": data.get("verdict") == "PASSED",
        "no_findings": not data.get("findings"),
        "no_warnings": not data.get("warnings"),
    }
    return {
        "step": "blindspot",
        "passed": all(checks.values()),
        "checks": checks,
        "receipt_error": data.get("__error__"),
        "results": [audit],
    }


def step_anti_circularity() -> dict:
    files = discover_lean()
    before = mtime_ns(GATE_RECEIPT)
    gate = run_cmd(
        [
            sys.executable,
            "tools/omega_audit/gate_strict.py",
            "check",
            "lean/spec_v4",
            "Math30Kernel",
            "Math30Interfaces",
            "--json",
            str(GATE_RECEIPT),
        ],
        1800,
    )
    after = mtime_ns(GATE_RECEIPT)
    data = load_json(GATE_RECEIPT)
    checks = {
        "gate_exit_zero": gate["exit_code"] == 0,
        "receipt_rewritten": after > before,
        "verdict_passed": data.get("verdict") == "PASS",
        "no_findings": not data.get("findings"),
        "no_not_run": not data.get("not_run"),
        "files_scanned_matches_discovery": data.get("files_scanned") == len(files),
    }
    return {
        "step": "anti_circularity",
        "passed": all(checks.values()),
        "checks": checks,
        "files_scanned": data.get("files_scanned"),
        "discovered_files": len(files),
        "receipt_error": data.get("__error__"),
        "results": [gate],
    }


STEPS = (
    ("manifest", step_manifest),
    ("spectrum", step_spectrum),
    ("newton_box", step_newton_box),
    ("rational_extraction", step_rational_extraction),
    ("z3_tribunal", step_z3),
    ("lean_surface", step_lean_surface),
    ("blindspot", step_blindspot),
    ("anti_circularity", step_anti_circularity),
)


def main() -> int:
    started_at = utc_now()
    print("=== MATH 3.0: REGRESSION TEST PIPELINE ===")
    report: dict = {
        "timestamp": started_at,
        "phase": "REGRESSION_MASTER_CLOSURE",
        "root": str(ROOT),
        "steps": [],
        "verdict": "FAILED",
        "manifest_note": (
            "The manifest is verified before the run. Receipts written by this "
            "run make it stale by design; reseal with "
            "`python mcp/t2n/core/repokeeper.py` and re-verify with `--verify`."
        ),
    }

    for index, (name, function) in enumerate(STEPS, start=1):
        try:
            result = function()
        except Exception as error:  # a step boundary must fail closed and be recorded
            result = {
                "step": name,
                "passed": False,
                "error": "%s: %s" % (type(error).__name__, error),
            }
        result.setdefault("step", name)
        report["steps"].append(result)
        status = "PASS" if result.get("passed") else "FAIL"
        print("[%d/%d] %-18s %s" % (index, len(STEPS), name, status))
        if not result.get("passed"):
            for check, value in (result.get("checks") or {}).items():
                if not value:
                    print("        check failed: %s" % check)
            if result.get("error"):
                print("        error: %s" % result["error"])

    passed = bool(report["steps"]) and all(step.get("passed") for step in report["steps"])
    report["verdict"] = "FULL PASS" if passed else "FAILED"
    report["finished_at"] = utc_now()

    REPORTS.mkdir(parents=True, exist_ok=True)
    try:
        with open(REGRESSION_REPORT, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
    except OSError as error:
        print("FATAL: cannot write %s: %s" % (REGRESSION_REPORT, error))
        return 2

    print("========================================")
    print("VERDICT: %s" % report["verdict"])
    print("[REPORT SECURED] %s" % REGRESSION_REPORT)
    print("[NOTE] Reseal the ledger after this run: python mcp/t2n/core/repokeeper.py")
    print("========================================")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
