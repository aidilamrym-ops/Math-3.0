"""Append batch-6 findings to the autonomous anomaly register (idempotent)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reports" / "autonomous_pipeline_anomalies.json"

ADD = [
    {
        "id": "OMEGA-0056",
        "batch": 6,
        "asset": "README.MD",
        "stage": "ADVERSARIAL_AUDIT",
        "severity": "HIGH",
        "category": "STALE_CLAIM",
        "finding": (
            "The Phase 50 (ActualInfinityRefutation.lean) and Phase 51 "
            "(ContinuityRefutation.lean) certificates were absent from the public "
            "inventory and phase history: section 10 listed 25 certificates ending "
            "at Phase 49, section 13 ended at Phase 49, and the Lean-surface counts "
            "still said 493 while 495 Lean files existed. The prior batch had "
            "announced a Phase 50 README update that was not present."
        ),
        "evidence": (
            "README.MD section 10 inventory ended at ErdosSzekeresRamsey.lean "
            "(Phase 49); Select-String for ActualInfinity/Phase 50/Phase 51 returned "
            "no matches; reports/full_surface_lean_audit.json recorded total_files=493 "
            "while the filesystem enumerated 495 Lean sources."
        ),
        "impact": (
            "The public certificate and phase ledger understated verified coverage "
            "by two Lean certificates and two Lean files, so a reader could not "
            "reproduce the claimed inventory from the README."
        ),
        "action": (
            "Added sections 5.13 and 5.14, two inventory rows, and Phase 50/51 "
            "history rows; corrected the certificate count to 27 and Lean-surface "
            "count to 495. Scope notes state that the finite-lattice results do not "
            "refute ZFC infinity or the abstract mathematical continuum. Reran the "
            "full-surface audit and both README audits before resealing."
        ),
        "status": "FIXED",
    },
    {
        "id": "OMEGA-0057",
        "batch": 6,
        "asset": "smt/phase4/actual_infinity_refutation.smt2",
        "stage": "ADVERSARIAL_AUDIT",
        "severity": "HIGH",
        "category": "CIRCULAR_WITNESS",
        "finding": (
            "The original QF_NIA script asserted total_states > capacity and "
            "total_states * step_cost <= capacity together with step_cost >= 1. "
            "Under the positive-capacity context, step_cost >= 1 already entails "
            "the negation of the final capacity assertion, so the unsat was a "
            "direct self-contradiction between axioms rather than a derived "
            "finite-capacity obstruction."
        ),
        "evidence": (
            "Anti-Circularity Gate audit: CIRCULAR, asserts=4, ctx=sat, "
            "script=unsat, core=[0,1,2,3]; 'assertion #1 is logically equivalent "
            "to the negation of the claim (#3)'."
        ),
        "impact": (
            "The SMT companion was advertised as an unsat refutation but the "
            "auditor classified it as a non-result. Only the Lean theorem "
            "actual_infinity_violates_conservation carries the general claim."
        ),
        "action": (
            "Preserved the flawed script at reports/omega_audit/flawed_certificates/"
            "actual_infinity_refutation.circular.smt2.txt; replaced it with a "
            "concrete four-step QF_LIA unrolling (capacity 3, strictly increasing "
            "states 0..4); updated the tribunal logic to QF_LIA; reran Z3 (unsat) "
            "and the Anti-Circularity Gate (GENUINE=2, PASS). README now labels the "
            "SMT as a concrete finite instance and identifies Lean as the general "
            "proof."
        ),
        "status": "FIXED",
    },
]


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    existing = {row["id"] for row in data["anomalies"]}
    added = 0
    for row in ADD:
        if row["id"] not in existing:
            data["anomalies"].append(row)
            added += 1
    data["updated_utc"] = datetime.now(timezone.utc).isoformat()
    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"appended={added} total={len(data['anomalies'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
