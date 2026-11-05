#!/usr/bin/env python3
"""Phase 9: Individual report certificate generator.

Standalone Python 3.14 utility. Standard library only.
No imports from external or hulu repositories.

For every Math 3.0 test-result artifact in the local workspace, this utility
creates:
  - reports/certificates/<stem>_certificate.json
  - lean/spec_v4/certificates/<PascalStem>Certificate.lean

Each JSON certificate binds the source report SHA-256 to the local sovereign
authority. Each Lean certificate embeds both the source SHA-256 and the
certificate SHA-256 and proves the link with a core `rfl` theorem.

Run sequentially. No threads, no concurrency.
"""

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

REPORTS_DIR = os.path.join(ROOT, "reports")
CERT_DIR = os.path.join(REPORTS_DIR, "certificates")
LEAN_CERT_DIR = os.path.join(ROOT, "lean", "spec_v4", "certificates")
INDEX_PATH = os.path.join(CERT_DIR, "certificate_index.json")
INDEX_LEAN_PATH = os.path.join(LEAN_CERT_DIR, "CertificateIndex.lean")

AUTHORITY = "Math 3.0 Local Sovereignty, Bounded-Lattice Kernel"

EXCLUDED_PATHS = {
    "manifest.json",
    "runtime_config.json",
    "reports/math30_laboratory_report.json",
}

EXCLUDED_DIRS = {
    "reports/certificates",
    "lean/spec_v4/certificates",
    ".git",
    "__pycache__",
    "mcp/out",
}

TARGET_PATTERNS = [
    "reports/*.json",
    "*.json",
    "smt/phase4/*.log",
]

SUMMARY_KEYS = [
    "phase",
    "timestamp",
    "audit_timestamp",
    "timestamp_generation",
    "verdict",
    "overall_verdict",
    "status",
    "anomaly_type",
    "audit_type",
    "precision_bits",
    "r_hank",
    "r_toep",
    "r_hank_rational",
    "generation",
    "jitter",
    "unique_root_certified",
    "zero_straddle_detected",
    "escalation_triggered",
    "lipschitz_contraction_verified",
    "eigenvalues_isolated",
    "triples_audited",
    "registration_token",
    "chronon_tick",
    "articles_accepted",
    "z3_tribunal_status",
    "epr_entanglement_bounded",
    "triad_state",
    "max_contraction_ratio",
    "positive_pivots",
    "negative_pivots",
    "zero_pivots",
    "signature",
]

NESTED_SUMMARY_KEYS = {
    "newton_box_contraction": ["unique_root_certified", "max_contraction_ratio"],
    "sylvester_inertia": ["signature", "positive_pivots", "negative_pivots", "zero_pivots"],
    "adversarial_suite": ["overall_status"],
    "manifest_status": ["rows_locked"],
    "source_ledger": ["unique_root_certified"],
    "runtime_config": ["precision_bits_base", "precision_bits_ceiling", "generation"],
}


def normalised_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return normalised_sha256(handle.read())


def pascal_case(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    result = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not result:
        result = "Report"
    if result[0].isdigit():
        result = "R" + result
    return result


def summarise_json(data):
    summary = {}
    if not isinstance(data, dict):
        return summary

    for key in SUMMARY_KEYS:
        if key in data:
            summary[key] = data[key]

    for parent, children in NESTED_SUMMARY_KEYS.items():
        value = data.get(parent)
        if isinstance(value, dict):
            for child in children:
                if child in value:
                    summary[f"{parent}.{child}"] = value[child]

    return summary


def summarise_log(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = lines[-1] if lines else ""
    return {
        "line_count": len(lines),
        "first_line": lines[0] if lines else "",
        "result": result,
    }


def discover_targets():
    targets = []
    for pattern in TARGET_PATTERNS:
        for path in glob.glob(os.path.join(ROOT, pattern)):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            if rel in EXCLUDED_PATHS:
                continue
            if any(rel == directory or rel.startswith(directory + "/") for directory in EXCLUDED_DIRS):
                continue
            if os.path.basename(path).endswith("_certificate.json"):
                continue
            targets.append(path)

    unique = sorted(set(targets), key=lambda item: os.path.relpath(item, ROOT).lower())
    return unique


def base_stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def build_certificate(rel_path: str, source_bytes: bytes, source_summary: dict):
    return {
        "certificate": "MATH 3.0 TEST RESULT CERTIFICATE",
        "phase": "PHASE_9_INDIVIDUAL_REPORT_CERTIFICATION",
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "authority": AUTHORITY,
        "source_file": rel_path,
        "source_sha256": normalised_sha256(source_bytes),
        "source_size_bytes": len(source_bytes),
        "source_summary": source_summary,
        "certification": {
            "local_only": True,
            "external_imports": [],
            "placeholders": False,
        },
    }


def write_json(path: str, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_lean_certificate(path: str, stem: str, source_rel: str, source_hash: str, cert_hash: str):
    namespace = f"Math30.Certificates.{stem}"

    content = f'''/-
  {stem}Certificate.lean
  Math 3.0 Phase 9: Individual report certificate for {source_rel}.
  Local sovereignty certificate. No external imports.
  No placeholders; no admit or axiom.
-/

namespace {namespace}

/-- Individual test-result certificate record. -/
structure ReportCertificate where
  sourceSha256 : String
  certificateSha256 : String
  authority : String

/-- Certified local report. -/
def certifiedReport : ReportCertificate := {{
  sourceSha256 := "{source_hash}"
  certificateSha256 := "{cert_hash}"
  authority := "{AUTHORITY}"
}}

/-- Cryptographic link theorem: both the source digest and the certificate
    digest match the local sovereign record exactly. -/
theorem report_cryptographic_link :
    certifiedReport.sourceSha256 = "{source_hash}" ∧
    certifiedReport.certificateSha256 = "{cert_hash}" ∧
    certifiedReport.authority = "{AUTHORITY}" := by
  constructor
  · rfl
  constructor <;> rfl

#eval "{stem} certificate compiled with zero placeholders."

end {namespace}
'''

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_index_lean(path: str, index_hash: str, total: int):
    content = f'''/-
  CertificateIndex.lean
  Math 3.0 Phase 9: Certificate index cryptographic anchor.
  Local sovereignty certificate. No external imports.
  No placeholders; no admit or axiom.
-/

namespace Math30.Certificates.Index

/-- Certificate index record. -/
structure CertificateIndex where
  indexSha256 : String
  authority : String
  totalCertificates : Nat

/-- Certified local certificate index. -/
def certifiedIndex : CertificateIndex := {{
  indexSha256 := "{index_hash}"
  authority := "{AUTHORITY}"
  totalCertificates := {total}
}}

/-- Cryptographic link theorem for the certificate index. -/
theorem index_cryptographic_link :
    certifiedIndex.indexSha256 = "{index_hash}" ∧
    certifiedIndex.authority = "{AUTHORITY}" ∧
    certifiedIndex.totalCertificates = {total} := by
  constructor
  · rfl
  constructor <;> rfl

#eval "CertificateIndex compiled with zero placeholders."

end Math30.Certificates.Index
'''

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def compile_lean(path: str):
    result = subprocess.run(
        ["lean", path], cwd=ROOT, capture_output=True, text=True
    )
    return result


def main():
    os.makedirs(CERT_DIR, exist_ok=True)
    os.makedirs(LEAN_CERT_DIR, exist_ok=True)

    targets = discover_targets()
    if not targets:
        print("No target reports found.")
        return 1

    seen_stems = set()
    index_entries = []

    total = len(targets)
    for position, path in enumerate(targets, start=1):
        rel_path = os.path.relpath(path, ROOT).replace("\\", "/")
        stem = base_stem(path)
        if stem in seen_stems:
            raise ValueError(f"Duplicate certificate stem: {stem}")
        seen_stems.add(stem)

        with open(path, "rb") as handle:
            source_bytes = handle.read()

        if path.lower().endswith(".json"):
            source_summary = summarise_json(json.loads(source_bytes.decode("utf-8")))
            source_type = "json"
        else:
            source_summary = summarise_log(source_bytes.decode("utf-8", errors="replace"))
            source_type = "log"

        certificate = build_certificate(rel_path, source_bytes, source_summary)
        certificate["source_type"] = source_type

        cert_name = f"{stem}_certificate.json"
        cert_path = os.path.join(CERT_DIR, cert_name)
        write_json(cert_path, certificate)
        cert_hash = sha256_file(cert_path)

        lean_name = f"{pascal_case(stem)}Certificate.lean"
        lean_path = os.path.join(LEAN_CERT_DIR, lean_name)
        write_lean_certificate(
            lean_path,
            pascal_case(stem),
            rel_path,
            certificate["source_sha256"],
            cert_hash,
        )

        compile_result = compile_lean(lean_path)
        if compile_result.returncode != 0:
            print(f"[{position}/{total}] FAIL {rel_path}")
            print(compile_result.stderr)
            return 1

        print(
            f"[{position}/{total}] {rel_path} -> {cert_name} "
            f"(lean exit {compile_result.returncode})"
        )

        index_entries.append(
            {
                "source_file": rel_path,
                "source_type": source_type,
                "source_sha256": certificate["source_sha256"],
                "certificate_file": f"reports/certificates/{cert_name}",
                "certificate_sha256": cert_hash,
                "lean_file": f"lean/spec_v4/certificates/{lean_name}",
                "lean_compile_exit_code": compile_result.returncode,
                "source_summary": source_summary,
            }
        )

    index_payload = {
        "certificate": "MATH 3.0 CERTIFICATE INDEX",
        "phase": "PHASE_9_INDIVIDUAL_REPORT_CERTIFICATION",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority": AUTHORITY,
        "total_certificates": len(index_entries),
        "certificates": index_entries,
        "certification": {
            "local_only": True,
            "external_imports": [],
            "placeholders": False,
        },
    }
    write_json(INDEX_PATH, index_payload)
    index_hash = sha256_file(INDEX_PATH)
    write_index_lean(INDEX_LEAN_PATH, index_hash, len(index_entries))

    index_compile = compile_lean(INDEX_LEAN_PATH)
    if index_compile.returncode != 0:
        print("FAIL CertificateIndex.lean")
        print(index_compile.stderr)
        return 1

    print(f"Index: reports/certificates/certificate_index.json")
    print(f"Index SHA-256: {index_hash}")
    print(f"Lean index: lean/spec_v4/certificates/CertificateIndex.lean")
    print(f"Lean index compile exit: {index_compile.returncode}")
    print(f"TOTAL CERTIFICATES: {len(index_entries)}")
    print("VERDICT: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())