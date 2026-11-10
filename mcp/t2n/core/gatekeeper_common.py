#!/usr/bin/env python3
"""Shared fail-closed gatekeeper wrapper.

The per-target scripts under `mcp/t2n/core/user_disertasi_gatekeeper_target*.py`
delegate here.  Every verdict comes from `gatekeeper_real.audit`, which extracts
SMT-LIB2 fences from the source and runs the real Z3 solver.  Missing sources
and unparseable SMT blocks are recorded as failures; no certificate is invented
and no user source file is moved or deleted.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gatekeeper_real

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "reports" / "user_certified_blueprints.json"


def derive_smt_result(checks: dict) -> str:
    results = checks.get("z3_results") or []
    if not results:
        return "not_run"
    if all(result == "unsat" for result in results):
        return "unsat"
    if all(result == "sat" for result in results):
        return "sat"
    return "mixed"


def update_registry(theorem: str, record: dict) -> None:
    try:
        rows = json.loads(REGISTRY.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            rows = []
    except (OSError, json.JSONDecodeError):
        rows = []
    rows = [row for row in rows if row.get("theorem") != theorem]
    rows.append(record)
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def run_gatekeeper(target_name: str, theorem: str) -> int:
    target = Path(target_name)
    if not target.is_absolute():
        target = ROOT / target

    print(f"[GATEKEEPER] theorem={theorem}")
    print(f"[GATEKEEPER] source={target}")

    if not target.is_file():
        record = {
            "theorem": theorem,
            "source": str(target),
            "status": "UNVERIFIABLE_MISSING_SOURCE",
            "kind": "MISSING_SOURCE",
            "checks": {},
            "smt_result": "not_run",
            "reason": "source file not found; refusing to certify",
        }
        update_registry(theorem, record)
        print("[ERROR] Source file not found. No certificate was written.")
        return 1

    result = gatekeeper_real.audit(target)
    record = {
        "theorem": theorem,
        "source": str(target),
        "status": result["status"],
        "kind": result["kind"],
        "checks": result["checks"],
        "smt_result": derive_smt_result(result["checks"]),
    }
    update_registry(theorem, record)
    print(f"[{result['status']}] {result['kind']} :: {json.dumps(result['checks'])}")
    return 0 if result["status"] == "PASS" else 1
