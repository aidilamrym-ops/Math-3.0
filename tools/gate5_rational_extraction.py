#!/usr/bin/env python3
"""Gate 5: exact rational extraction bridge from interval receipts to Lean `ℚ`.

The Gate 4 validators use python-flint balls with a rigorous midpoint/radius
enclosure.  Until this gate existed, downstream evidence was recovered with
``Fraction(str(float(...)))``, which silently discards precision and cannot be
audited.  This producer does three things:

1. Reads the exact ``{num, den}`` transports written by
   ``tools/lte_spectral_validator.py`` and ``tools/newton_box_validator.py``.
   Any missing, decimal, boolean, or non-positive-denominator field is a hard
   failure; there is no float fallback.
2. Regenerates ``lean/spec_v4/Gate5RationalExtractionValidation.lean`` with the
   generic bridge source embedded verbatim plus concrete numeric theorems.
   Every rational is emitted as ``exactRat (num) (den)``.
3. Compiles the certificate through ``lake env lean`` and writes
   ``reports/gate5_rational_extraction.json`` with source hashes, theorem
   counts, and the solver output.  A non-zero exit is a failed gate.

The generated certificate is self-contained: it imports only Mathlib, so a
fresh clone can re-check it with

    cd lean
    lake env lean spec_v4/Gate5RationalExtractionValidation.lean

without any hidden build artifact.  The embedded bridge is copied from
``Gate5RationalBridge.lean`` and its SHA-256 is pinned in the certificate header
and in the receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LEAN_DIR = ROOT / "lean"
SPEC_DIR = LEAN_DIR / "spec_v4"

BRIDGE = SPEC_DIR / "Gate5RationalBridge.lean"
CERTIFICATE = SPEC_DIR / "Gate5RationalExtractionValidation.lean"
TMP_CERTIFICATE = SPEC_DIR / "_tmp_gate5_validation.lean"
LTE_RECEIPT = REPORTS / "lte_spectral_validation.json"
NEWTON_RECEIPT = REPORTS / "topological_uniqueness.json"
RECEIPT = REPORTS / "gate5_rational_extraction.json"

HALF = Fraction(1, 2)
EXPECTED_PIVOTS = 3
THEOREMS_PER_PIVOT = 6
EXPECTED_DEFINITIONS = 6 * EXPECTED_PIVOTS
EXPECTED_THEOREMS = 2 * EXPECTED_PIVOTS * THEOREMS_PER_PIVOT


class Gate5Error(RuntimeError):
    """A fail-closed Gate 5 condition was violated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise Gate5Error(f"cannot read {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(data, dict):
        raise Gate5Error(f"{path.relative_to(ROOT)}: top level is not an object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Gate5Error(message)


def exact_fraction(payload: object, label: str) -> Fraction:
    """Decode an exact ``{num, den}`` transport, rejecting every lossy form."""
    require(isinstance(payload, dict), f"{label}: expected an exact {{num, den}} object")
    num = payload.get("num")
    den = payload.get("den")
    require(isinstance(num, int) and not isinstance(num, bool), f"{label}: numerator is not an int")
    require(isinstance(den, int) and not isinstance(den, bool), f"{label}: denominator is not an int")
    require(den > 0, f"{label}: denominator must be positive, got {den}")
    return Fraction(num, den)


def lean_rat(value: Fraction) -> str:
    return f"exactRat ({value.numerator}) ({value.denominator})"


def collect_lte() -> dict:
    path = LTE_RECEIPT
    data = load_json(path)
    spectral = data.get("spectral_analysis")
    require(isinstance(spectral, dict), "lte receipt: missing spectral_analysis")
    require(
        spectral.get("rigid_asymmetry_certified") is True,
        "lte receipt: rigid asymmetry is not certified",
    )
    require(
        spectral.get("zero_straddle_detected") is False,
        "lte receipt: zero straddle detected",
    )
    pivots = spectral.get("pivots")
    require(isinstance(pivots, list) and len(pivots) == EXPECTED_PIVOTS, "lte receipt: expected 3 pivots")
    rows = []
    for index, pivot in enumerate(pivots):
        require(isinstance(pivot, dict), f"lte pivot {index}: not an object")
        require(pivot.get("index") == index, f"lte pivot {index}: index mismatch")
        require(
            pivot.get("signed_definite") is True and pivot.get("contains_zero") is False,
            f"lte pivot {index}: signed_definite/contains_zero flags disagree with exact transport",
        )
        enclosure = pivot.get("enclosure_exact")
        require(isinstance(enclosure, dict), f"lte pivot {index}: missing enclosure_exact")
        lo = exact_fraction(enclosure.get("lo"), f"lte pivot {index} enclosure lo")
        hi = exact_fraction(enclosure.get("hi"), f"lte pivot {index} enclosure hi")
        mid = exact_fraction(pivot.get("mid_exact"), f"lte pivot {index} midpoint")
        require(lo <= mid <= hi, f"lte pivot {index}: midpoint outside its exact enclosure")
        require(lo > 0, f"lte pivot {index}: exact lower endpoint is not positive")
        rows.append({"index": index, "lo": lo, "mid": mid, "hi": hi})
    return {
        "path": path,
        "sha256": sha256_file(path),
        "precision_bits": spectral.get("precision_bits"),
        "pivots": rows,
    }


def collect_newton() -> dict:
    path = NEWTON_RECEIPT
    data = load_json(path)
    box = data.get("newton_box_contraction")
    require(isinstance(box, dict), "newton receipt: missing newton_box_contraction")
    require(box.get("unique_root_certified") is True, "newton receipt: unique root not certified")
    require(box.get("all_strict_inclusion") is True, "newton receipt: strict inclusion not certified")
    require(box.get("boundary_escape") is False, "newton receipt: boundary escape recorded")
    pivots = box.get("pivots")
    require(
        isinstance(pivots, list) and len(pivots) == EXPECTED_PIVOTS,
        "newton receipt: expected 3 pivots",
    )
    evidence = (
        ((data.get("lean_evidence") or {}).get("parameters") or {}).get("pivots")
        if isinstance(data.get("lean_evidence"), dict)
        else None
    )
    require(
        isinstance(evidence, list) and len(evidence) == EXPECTED_PIVOTS,
        "newton receipt: expected 3 lean_evidence pivots",
    )
    rows = []
    for index, pivot in enumerate(pivots):
        require(isinstance(pivot, dict), f"newton pivot {index}: not an object")
        require(pivot.get("index") == index, f"newton pivot {index}: index mismatch")
        require(pivot.get("strict_inclusion") is True, f"newton pivot {index}: strict inclusion false")
        contraction = exact_fraction(
            pivot.get("contraction_upper_exact"), f"newton pivot {index} contraction upper bound"
        )
        lo = exact_fraction(pivot.get("lower_endpoint_exact"), f"newton pivot {index} lower endpoint")
        hi = exact_fraction(pivot.get("upper_endpoint_exact"), f"newton pivot {index} upper endpoint")
        require(0 < contraction < HALF, f"newton pivot {index}: contraction bound not in (0, 1/2)")
        require(0 < lo <= hi, f"newton pivot {index}: endpoint interval is not positive")
        ev = evidence[index]
        require(isinstance(ev, dict), f"newton evidence {index}: not an object")
        require(ev.get("index") == index, f"newton evidence {index}: index mismatch")
        ev_contraction = exact_fraction(
            {
                "num": ev.get("contraction_numerator"),
                "den": ev.get("contraction_denominator"),
            },
            f"newton evidence {index} contraction",
        )
        ev_lower = exact_fraction(
            {
                "num": ev.get("lower_endpoint_numerator"),
                "den": ev.get("lower_endpoint_denominator"),
            },
            f"newton evidence {index} lower endpoint",
        )
        require(ev_contraction == contraction, f"newton evidence {index}: contraction drift")
        require(ev_lower == lo, f"newton evidence {index}: lower endpoint drift")
        rows.append({"index": index, "contraction": contraction, "lo": lo, "hi": hi})
    return {
        "path": path,
        "sha256": sha256_file(path),
        "precision_bits": box.get("precision_bits"),
        "pivots": rows,
    }


def build_lte_theorems(row: dict) -> tuple[list[str], list[str]]:
    index = row["index"]
    lo = f"ltePivot{index}Lo"
    mid = f"ltePivot{index}Mid"
    hi = f"ltePivot{index}Hi"
    definitions = [
        f"def {lo} : ℚ := {lean_rat(row['lo'])}",
        f"def {mid} : ℚ := {lean_rat(row['mid'])}",
        f"def {hi} : ℚ := {lean_rat(row['hi'])}",
    ]
    theorems = [
        (
            f"ltePivot{index}_lo_pos",
            f"0 < {lo}",
            f"  unfold {lo}\n  norm_num [exactRat]",
        ),
        (
            f"ltePivot{index}_lo_le_mid",
            f"{lo} ≤ {mid}",
            f"  unfold {lo} {mid}\n  norm_num [exactRat]",
        ),
        (
            f"ltePivot{index}_mid_le_hi",
            f"{mid} ≤ {hi}",
            f"  unfold {mid} {hi}\n  norm_num [exactRat]",
        ),
        (
            f"ltePivot{index}_mid_mem",
            f"Contains ⟨{lo}, {hi}⟩ {mid}",
            f"  exact contains_of_bounds ltePivot{index}_lo_le_mid ltePivot{index}_mid_le_hi",
        ),
        (
            f"ltePivot{index}_sign_sound",
            f"∀ q : ℚ, Contains ⟨{lo}, {hi}⟩ q → 0 < q",
            f"  intro q hq\n  exact contains_positive hq ltePivot{index}_lo_pos",
        ),
        (
            f"ltePivot{index}_lo_scale",
            f"{lo} * ({row['lo'].denominator} : ℚ) = ({row['lo'].numerator} : ℚ)",
            f"  unfold {lo}\n  exact exactRat_mul_den (by norm_num)",
        ),
    ]
    return definitions, theorems


def build_newton_theorems(row: dict) -> tuple[list[str], list[str]]:
    index = row["index"]
    contraction = f"newtonPivot{index}Contraction"
    lo = f"newtonPivot{index}Lo"
    hi = f"newtonPivot{index}Hi"
    definitions = [
        f"def {contraction} : ℚ := {lean_rat(row['contraction'])}",
        f"def {lo} : ℚ := {lean_rat(row['lo'])}",
        f"def {hi} : ℚ := {lean_rat(row['hi'])}",
    ]
    theorems = [
        (
            f"newtonPivot{index}_contraction_lt_half",
            f"{contraction} < (1 / 2 : ℚ)",
            f"  unfold {contraction}\n  norm_num [exactRat]",
        ),
        (
            f"newtonPivot{index}_lo_pos",
            f"0 < {lo}",
            f"  unfold {lo}\n  norm_num [exactRat]",
        ),
        (
            f"newtonPivot{index}_lo_le_hi",
            f"{lo} ≤ {hi}",
            f"  unfold {lo} {hi}\n  norm_num [exactRat]",
        ),
        (
            f"newtonPivot{index}_sign_sound",
            f"∀ q : ℚ, Contains ⟨{lo}, {hi}⟩ q → 0 < q",
            f"  intro q hq\n  exact contains_positive hq newtonPivot{index}_lo_pos",
        ),
        (
            f"newtonPivot{index}_lo_scale",
            f"{lo} * ({row['lo'].denominator} : ℚ) = ({row['lo'].numerator} : ℚ)",
            f"  unfold {lo}\n  exact exactRat_mul_den (by norm_num)",
        ),
        (
            f"newtonPivot{index}_contraction_scale",
            (
                f"{contraction} * ({row['contraction'].denominator} : ℚ) = "
                f"({row['contraction'].numerator} : ℚ)"
            ),
            f"  unfold {contraction}\n  exact exactRat_mul_den (by norm_num)",
        ),
    ]
    return definitions, theorems


def render_certificate(lte: dict, newton: dict, bridge_body: str, bridge_sha: str) -> tuple[str, list[str], int]:
    lines: list[str] = [
        "/-",
        "  GENERATED FILE - do not edit by hand.",
        "  Producer: tools/gate5_rational_extraction.py",
        "",
        "  Gate 5: exact rational extraction from the Gate 4 interval receipts.",
        "  Every numeric endpoint below is emitted as `exactRat (num) (den)`;",
        "  no decimal or floating-point literal occurs in this file.",
        "",
        f"  bridge_source_sha256:  {bridge_sha}",
        f"  lte_source_sha256:     {lte['sha256']}",
        f"  newton_source_sha256:  {newton['sha256']}",
        "",
        "  The generic bridge source is embedded as a re-namespaced snapshot",
        "  (Math30.Gate5.Certified) with its SHA-256 pinned below.  The file is",
        "  self-contained and can be re-checked on a fresh clone with:",
        "      cd lean && lake env lean spec_v4/Gate5RationalExtractionValidation.lean",
        "-/",
        "import Mathlib.Data.Rat.Defs",
        "import Mathlib.Tactic",
        "",
        bridge_body.rstrip(),
        "",
        "namespace Math30.Gate5.Certified",
        "",
        "/-! ### Concrete extraction certificate",
        "",
        "The generic bridge above is an embedded, re-namespaced snapshot of",
        "`Gate5RationalBridge.lean` (hash pinned in the header); the separate",
        "namespace keeps the canonical bridge module and this certificate from",
        "declaring the same constant twice.  Every rational below is an exact",
        "`(num, den)` pair from the receipts.  The theorems re-establish, inside",
        "Lean, every bound the producers used: positivity of each spectral",
        "enclosure, midpoint containment, Newton contraction below 1/2, and",
        "lossless scaling by the transported denominator. -/",
        "",
    ]
    theorem_names: list[str] = []
    definitions_count = 0
    for row in lte["pivots"]:
        definitions, theorems = build_lte_theorems(row)
        lines.append(f"/-! #### LTE pivot {row['index']} -/")
        lines.append("")
        lines.extend(definitions)
        lines.append("")
        for name, statement, proof in theorems:
            lines.append(f"theorem {name} : {statement} := by")
            lines.extend(proof.splitlines())
            lines.append("")
            theorem_names.append(name)
        definitions_count += len(definitions)
    for row in newton["pivots"]:
        definitions, theorems = build_newton_theorems(row)
        lines.append(f"/-! #### Newton pivot {row['index']} -/")
        lines.append("")
        lines.extend(definitions)
        lines.append("")
        for name, statement, proof in theorems:
            lines.append(f"theorem {name} : {statement} := by")
            lines.extend(proof.splitlines())
            lines.append("")
            theorem_names.append(name)
        definitions_count += len(definitions)
    lines.append("end Math30.Gate5.Certified")
    lines.append("")
    text = "\n".join(lines)
    require(
        definitions_count == EXPECTED_DEFINITIONS,
        f"generator bug: emitted {definitions_count} definitions, expected {EXPECTED_DEFINITIONS}",
    )
    require(
        len(theorem_names) == EXPECTED_THEOREMS,
        f"generator bug: emitted {len(theorem_names)} theorems, expected {EXPECTED_THEOREMS}",
    )
    return text, theorem_names, definitions_count


def strip_comments(source: str) -> str:
    source = re.sub(r"/-.*?-/", "", source, flags=re.DOTALL)
    source = re.sub(r"--[^\n]*", "", source)
    return source


def audit_generated_source(source: str) -> dict:
    code = strip_comments(source)
    decimal_literals = re.findall(r"(?<![\w.])\d+\.\d+", code)
    placeholders = re.findall(r"\b(?:sorry|admit|sorryAx|native_decide)\b", code)
    axiom_declarations = re.findall(r"(?m)^\s*(?:private\s+|protected\s+)?axiom\b", code)
    float_mentions = re.findall(r"\b(?:Float|float|ofScientific)\b", code)
    return {
        "decimal_literals": len(decimal_literals),
        "placeholder_tokens": len(placeholders),
        "axiom_declarations": len(axiom_declarations),
        "float_mentions": len(float_mentions),
    }


def compile_certificate(timeout: int) -> dict:
    display = ["lake", "env", "lean", str(TMP_CERTIFICATE.relative_to(LEAN_DIR))]
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            display,
            cwd=LEAN_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "command": display,
            "exit_code": None,
            "timed_out": True,
            "stdout": (error.stdout or "")[-4000:] if isinstance(error.stdout, str) else "",
            "stderr": (error.stderr or "")[-4000:] if isinstance(error.stderr, str) else "",
            "elapsed_s": round(time.perf_counter() - started, 3),
        }
    return {
        "command": display,
        "exit_code": proc.returncode,
        "timed_out": False,
        "stdout": (proc.stdout or "")[-4000:],
        "stderr": (proc.stderr or "")[-4000:],
        "elapsed_s": round(time.perf_counter() - started, 3),
    }


def run(timeout: int) -> dict:
    started = time.perf_counter()
    require(BRIDGE.is_file(), f"missing bridge source: {BRIDGE.relative_to(ROOT)}")
    bridge_text = BRIDGE.read_text(encoding="utf-8")
    bridge_sha = sha256_bytes(bridge_text.encode("utf-8"))
    marker = "namespace Math30.Gate5"
    require(marker in bridge_text, "bridge source does not declare namespace Math30.Gate5")
    bridge_body = bridge_text[bridge_text.index(marker):]
    # Re-namespace the embedded snapshot so the canonical bridge module and the
    # certificate never declare the same constant.  The embedded bytes are
    # otherwise identical and the source hash is pinned in the header.
    embedded_body = bridge_body.replace(
        "namespace Math30.Gate5", "namespace Math30.Gate5.Certified"
    ).replace("end Math30.Gate5", "end Math30.Gate5.Certified")

    lte = collect_lte()
    newton = collect_newton()
    source, theorem_names, definitions_count = render_certificate(
        lte, newton, embedded_body, bridge_sha
    )
    source_audit = audit_generated_source(source)
    require(source_audit["decimal_literals"] == 0, "generated certificate contains a decimal literal")
    require(source_audit["placeholder_tokens"] == 0, "generated certificate contains a placeholder token")
    require(source_audit["axiom_declarations"] == 0, "generated certificate declares an axiom")
    require(source_audit["float_mentions"] == 0, "generated certificate mentions floating point")

    TMP_CERTIFICATE.write_text(source, encoding="utf-8", newline="\n")
    try:
        compile_result = compile_certificate(timeout)
        require(compile_result["exit_code"] == 0, "generated certificate failed to compile")
        os.replace(TMP_CERTIFICATE, CERTIFICATE)
    finally:
        if TMP_CERTIFICATE.exists():
            TMP_CERTIFICATE.unlink()

    certificate_sha = sha256_file(CERTIFICATE)
    checks = {
        "exact_transport_present": True,
        "no_lossy_literals": True,
        "bridge_hash_in_header": bridge_sha in source,
        "bridge_body_embedded": embedded_body.rstrip() in source,
        "compile_exit_zero": compile_result["exit_code"] == 0,
        "definition_count_ok": definitions_count == EXPECTED_DEFINITIONS,
        "theorem_count_ok": len(theorem_names) == EXPECTED_THEOREMS,
        "lte_pivots_exact": len(lte["pivots"]) == EXPECTED_PIVOTS,
        "newton_pivots_exact": len(newton["pivots"]) == EXPECTED_PIVOTS,
        "all_lte_intervals_positive": all(row["lo"] > 0 for row in lte["pivots"]),
        "all_newton_contractions_below_half": all(
            row["contraction"] < HALF for row in newton["pivots"]
        ),
    }
    verdict = "PASSED" if all(checks.values()) else "FAILED"
    return {
        "gate": "GATE_5_EXACT_RATIONAL_EXTRACTION",
        "timestamp": utc_now(),
        "verdict": verdict,
        "sources": {
            "lte_spectral_validation": {
                "path": str(lte["path"].relative_to(ROOT)),
                "sha256": lte["sha256"],
                "precision_bits": lte["precision_bits"],
                "pivots": len(lte["pivots"]),
            },
            "topological_uniqueness": {
                "path": str(newton["path"].relative_to(ROOT)),
                "sha256": newton["sha256"],
                "precision_bits": newton["precision_bits"],
                "pivots": len(newton["pivots"]),
            },
        },
        "bridge": {
            "path": str(BRIDGE.relative_to(ROOT)),
            "sha256": bridge_sha,
            "embedded_verbatim": True,
        },
        "certificate": {
            "path": str(CERTIFICATE.relative_to(ROOT)),
            "sha256": certificate_sha,
            "bytes": CERTIFICATE.stat().st_size,
            "lines": source.count("\n") + 1,
            "definitions": definitions_count,
            "theorems": len(theorem_names),
            "theorem_names": theorem_names,
        },
        "checks": checks,
        "source_audit": source_audit,
        "compile": compile_result,
        "elapsed_s": round(time.perf_counter() - started, 3),
        "scope_note": (
            "This gate certifies exact transport of the Gate 4 interval endpoints "
            "and their signs. It does not certify the upstream floating-point "
            "matrix entries from which those balls were computed; that trust "
            "boundary remains the python-flint arb construction."
        ),
    }


def write_receipt(receipt: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")


def main(argv: list[str]) -> int:
    timeout = 1800
    if "--timeout" in argv:
        index = argv.index("--timeout")
        require(index + 1 < len(argv), "--timeout requires a value")
        timeout = int(argv[index + 1])
    try:
        receipt = run(timeout)
    except Exception as error:  # noqa: BLE001 - gate must fail closed and record why
        receipt = {
            "gate": "GATE_5_EXACT_RATIONAL_EXTRACTION",
            "timestamp": utc_now(),
            "verdict": "FAILED",
            "error": f"{type(error).__name__}: {error}",
        }
        write_receipt(receipt)
        print(f"GATE 5 FAILED: {type(error).__name__}: {error}")
        return 1
    write_receipt(receipt)
    print(
        "GATE 5 PASSED: %d definitions, %d theorems, compile %.1fs"
        % (
            receipt["certificate"]["definitions"],
            receipt["certificate"]["theorems"],
            receipt["compile"]["elapsed_s"],
        )
    )
    print(f"CERTIFICATE: {receipt['certificate']['path']} ({receipt['certificate']['bytes']} bytes)")
    print(f"RECEIPT: {RECEIPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
