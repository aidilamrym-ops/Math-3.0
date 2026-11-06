"""Spectral meta-analyzer for the sealed OpenAI-Math catalogue.

Reads the 373 family report JSONs plus their certificates and Lean anchors,
extracts the Hankel residual and Planck containment status, and emits a
consolidated metadata signature log.

Important provenance note: the f/g coordinates used to generate these reports
were produced by the deterministic index formula
    f_mid = 2 * family_index + 1
    g_mid = family_index + 5
so the Hankel residual for the formula-driven families is exactly
    r_hank = family_index - 4.
Any "cluster" of shared residuals is therefore an artifact of that formula,
not an emergent mathematical correlation between the underlying manuscripts.
"""

import glob
import hashlib
import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from fractions import Fraction

ROOT = r"D:\Opencode AI Agent\Math 3.0 Tools"
REPORTS = os.path.join(ROOT, "reports")
CERTS = os.path.join(REPORTS, "certificates")
LEANS = os.path.join(ROOT, "lean", "spec_v4", "certificates")
OUT = os.path.join(REPORTS, "math30_discovered_intelligence.json")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ball_mid(text):
    if not text:
        return None
    m = re.search(r"\[\s*([+-]?\d+(?:\.\d+)?)", text)
    if not m:
        return None
    return Fraction(m.group(1))


def lean_string(lean_text, field):
    m = re.search(rf'{field}\s*:=\s*"([0-9a-fA-F]{{64}})"', lean_text)
    return m.group(1).lower() if m else None


records = []
integrity = {
    "reports_checked": 0,
    "certificates_found": 0,
    "lean_files_found": 0,
    "cert_source_sha_match": 0,
    "lean_source_sha_match": 0,
    "lean_cert_sha_match": 0,
    "mismatches": [],
}

report_files = sorted(glob.glob(os.path.join(REPORTS, "openai_family_*.json")))
for path in report_files:
    base = os.path.basename(path)
    m = re.match(r"openai_family_(\d{3})\.json$", base)
    if not m:
        continue

    idx = int(m.group(1))
    data = json.load(open(path, encoding="utf-8"))

    coeffs = data.get("coefficients", {})
    try:
        f_mid = Fraction(str(coeffs.get("f_convergent")))
        g_mid = Fraction(str(coeffs.get("g_divergent")))
    except Exception:
        f_mid = None
        g_mid = None

    residual_exact = (f_mid - g_mid) if (f_mid is not None and g_mid is not None) else None
    residual_ball = parse_ball_mid(data.get("r_hank"))
    radius_ok = bool(data.get("micro_cutoff", {}).get("radius_leq_planck", False))
    precision_bits = data.get("precision_bits")
    verdict = data.get("verdict", "")

    integrity["reports_checked"] += 1

    cert_path = os.path.join(CERTS, f"openai_family_{idx:03d}_certificate.json")
    lean_path = os.path.join(LEANS, f"OpenaiFamily{idx:03d}Certificate.lean")

    cert_source_match = False
    lean_source_match = False
    lean_cert_match = False

    if os.path.exists(cert_path):
        integrity["certificates_found"] += 1
        cert = json.load(open(cert_path, encoding="utf-8"))
        actual_source = sha256_file(path)
        cert_source_match = cert.get("source_sha256") == actual_source
        if cert_source_match:
            integrity["cert_source_sha_match"] += 1

        if os.path.exists(lean_path):
            integrity["lean_files_found"] += 1
            lean_text = open(lean_path, encoding="utf-8").read()
            actual_cert = sha256_file(cert_path)
            lean_source = lean_string(lean_text, "sourceSha256")
            lean_cert = lean_string(lean_text, "certificateSha256")
            lean_source_match = lean_source == actual_source
            lean_cert_match = lean_cert == actual_cert
            if lean_source_match:
                integrity["lean_source_sha_match"] += 1
            if lean_cert_match:
                integrity["lean_cert_sha_match"] += 1
    else:
        actual_source = sha256_file(path)

    if not (cert_source_match and lean_source_match and lean_cert_match):
        integrity["mismatches"].append(
            {
                "family_index": idx,
                "cert_source_match": cert_source_match,
                "lean_source_match": lean_source_match,
                "lean_cert_match": lean_cert_match,
            }
        )

    records.append(
        {
            "family_index": idx,
            "f_mid": str(f_mid) if f_mid is not None else None,
            "g_mid": str(g_mid) if g_mid is not None else None,
            "computed_hankel_residual": str(residual_exact) if residual_exact is not None else None,
            "hankel_residual_ball_mid": str(residual_ball) if residual_ball is not None else None,
            "residual_consistent": residual_exact == residual_ball if (residual_exact is not None and residual_ball is not None) else False,
            "radius_leq_planck_status": radius_ok,
            "precision_bits": precision_bits,
            "verdict": verdict,
        }
    )

# ---- exact residual groups -------------------------------------------------
groups = {}
for rec in records:
    key = rec["computed_hankel_residual"]
    if key is None:
        continue
    groups.setdefault(key, []).append(rec["family_index"])

shared_groups = {k: v for k, v in groups.items() if len(v) > 1}

# ---- statistics ------------------------------------------------------------
residual_fractions = [Fraction(r["computed_hankel_residual"]) for r in records if r["computed_hankel_residual"] is not None]
variance_exact = statistics.pvariance(residual_fractions) if len(residual_fractions) > 1 else Fraction(0)
mean_exact = statistics.mean(residual_fractions) if residual_fractions else Fraction(0)
stdev_float = math.sqrt(float(variance_exact)) if variance_exact else 0.0

# ---- linear-law check ------------------------------------------------------
linear_matches = []
linear_exceptions = []
for rec in records:
    if rec["computed_hankel_residual"] is None:
        continue
    expected = rec["family_index"] - 4
    if Fraction(rec["computed_hankel_residual"]) == expected:
        linear_matches.append(rec["family_index"])
    else:
        linear_exceptions.append(
            {
                "family_index": rec["family_index"],
                "residual": rec["computed_hankel_residual"],
                "expected_index_minus_4": expected,
            }
        )

# ---- integrity summary -----------------------------------------------------
integrity["all_three_hashes_match"] = (
    integrity["reports_checked"]
    == integrity["cert_source_sha_match"]
    == integrity["lean_source_sha_match"]
    == integrity["lean_cert_sha_match"]
)

payload = {
    "schema": "MATH30_DISCOVERED_INTELLIGENCE_V1",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source": "reports/openai_family_###.json + reports/certificates/ + lean/spec_v4/certificates/",
    "family_count": len(records),
    "parameters": [
        "family_index",
        "computed_hankel_residual",
        "radius_leq_planck_status",
    ],
    "statistics": {
        "count": len(residual_fractions),
        "mean_exact": str(mean_exact),
        "mean_float": float(mean_exact),
        "variance_exact": str(variance_exact),
        "variance_float": float(variance_exact),
        "stdev_float": stdev_float,
        "min_exact": str(min(residual_fractions)) if residual_fractions else None,
        "max_exact": str(max(residual_fractions)) if residual_fractions else None,
        "unique_residual_values": len(groups),
        "shared_residual_groups": len(shared_groups),
    },
    "planck_containment": {
        "all_true": all(r["radius_leq_planck_status"] for r in records),
        "true_count": sum(1 for r in records if r["radius_leq_planck_status"]),
        "false_count": sum(1 for r in records if not r["radius_leq_planck_status"]),
        "precision_bits_values": sorted({r["precision_bits"] for r in records if r["precision_bits"] is not None}),
    },
    "linear_law": {
        "formula": "computed_hankel_residual == family_index - 4",
        "match_count": len(linear_matches),
        "exception_count": len(linear_exceptions),
        "exceptions": linear_exceptions,
    },
    "shared_residual_groups": shared_groups,
    "records": records,
    "integrity": integrity,
    "forensic_note": (
        "The dominant linear relation residual = family_index - 4 is a direct consequence "
        "of the deterministic coordinate formula f_mid = 2*index + 1, g_mid = index + 5 used "
        "by the batch pipeline. It is not an emergent mathematical correlation between the "
        "OpenAI manuscripts. Shared residual values (for example residual 1 shared by families "
        "005, 197 and 198) are likewise formula artifacts, not evidence of a common mathematical "
        "invariant. Discipline-level clustering was not attempted because the artifacts do not "
        "store a discipline label."
    ),
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2, ensure_ascii=False)

print("SPECTRAL META-ANALYZER")
print("======================")
print(f"Families parsed              : {len(records)}")
print(f"Residual values (unique)     : {len(groups)}")
print(f"Shared residual groups       : {len(shared_groups)}")
print(f"Mean residual (exact)        : {mean_exact}")
print(f"Variance (exact)             : {variance_exact}")
print(f"Variance (float)             : {float(variance_exact):.6f}")
print(f"Standard deviation           : {stdev_float:.6f}")
print(f"Min / max residual           : {min(residual_fractions)} / {max(residual_fractions)}")
print(f"Planck containment all-true  : {payload['planck_containment']['all_true']}")
print(f"Precision contexts           : {payload['planck_containment']['precision_bits_values']}")
print()
print("LINEAR LAW CHECK (residual == family_index - 4)")
print(f"  matches    : {len(linear_matches)}")
print(f"  exceptions : {len(linear_exceptions)}")
for exc in linear_exceptions:
    print(f"    family {exc['family_index']:03d}: residual={exc['residual']} (expected {exc['expected_index_minus_4']})")
print()
print("SHARED RESIDUAL GROUPS")
for key, members in sorted(shared_groups.items(), key=lambda kv: Fraction(kv[0])):
    print(f"  residual {key}: families {members}")
print()
print("INTEGRITY")
print(f"  reports checked           : {integrity['reports_checked']}")
print(f"  certificates found        : {integrity['certificates_found']}")
print(f"  Lean files found          : {integrity['lean_files_found']}")
print(f"  cert source SHA matches   : {integrity['cert_source_sha_match']}")
print(f"  Lean source SHA matches   : {integrity['lean_source_sha_match']}")
print(f"  Lean cert SHA matches     : {integrity['lean_cert_sha_match']}")
print(f"  all three hashes match    : {integrity['all_three_hashes_match']}")
print()
print(f"Signature log written to : {OUT}")
