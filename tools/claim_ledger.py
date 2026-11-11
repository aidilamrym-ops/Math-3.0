#!/usr/bin/env python3
"""Claims ledger: map each README claim to a concrete provenance.

Reads the README and the theorem-name audit result to produce a machine‑readable
ledger (`claims/ledger.json`).  Each entry contains:
  - id                : the backticked identifier from the README
  - prose             : the original line from the README that mentions the identifier
  - artifact          : the Lean file(s) that declare the name
  - theorem_name      : the same name (for readability)
  - provenance        : "local"  – the declaration lives inside Math 3.0,
                         "imported" – the name is imported from Mathlib or other external module
  - class             : "kernel theorem", "bounded model" or "numerical evidence"

The ledger is written to `reports/claims/ledger.json`.  An HTML‑styled summary
is also emitted for quick manual verification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.MD"
REPORTS = ROOT / "reports"
LEDGER_DIR = REPORTS / "claims"
LEDGER_JSON = LEDGER_DIR / "ledger.json"
THEOREM_AUDIT_JSON = REPORTS / "readme_theorem_audit.json"

# Simple heuristics for provenance / class detection
MATHLIB_INDICATORS = {"mathlib", "Mathlib"}
BOUNDED_KEYWORDS = {"finite", "lattice", "bounded", "model", "evidence"}
NUMERICAL_KEYWORDS = {"zeta", "riemann", "hypothesis", "critical", "interval", "trace", "spectral"}


def extract_cited(readme_text: str) -> list[tuple[str, str]]:
    """Return (identifier, prose_line) for every backticked identifier in README.
    The prose line is the original line that contains the identifier (including
    the backticks)."""
    entries: list[tuple[str, str]] = []
    for line in readme_text.splitlines():
        for m in re.finditer(r"`([^`\n]+)`", line):
            ident = m.group(1).strip()
            if not ident or ident.lower() in {"true", "false", "sorry", "admit"}:
                continue
            # skip identifiers ending with common code suffixes
            if any(ident.lower().endswith(suf) for suf in [".lean", ".py", ".json", ".md", ".txt", ".smt2"]):
                continue
            entries.append((ident, line.strip()))
    # deduplicate preserving order
    seen = set()
    deduped: list[tuple[str, str]] = []
    for ident, prose in entries:
        if ident not in seen:
            seen.add(ident)
            deduped.append((ident, prose))
    return deduped


def load_theorem_audit():
    if not THEOREM_AUDIT_JSON.is_file():
        print(f"WARNING: {THEOREM_AUDIT_JSON} not found – run readme_theorem_audit.py first.", file=sys.stderr)
        return {}
    return json.loads(THEOREM_AUDIT_JSON.read_text(encoding="utf-8"))


def detect_provenance(path: str) -> str:
    lowered = path.lower()
    if any(indicator in lowered for indicator in MATHLIB_INDICATORS):
        return "imported"
    # Heuristic: files under staging/user_disertasi/lean/certificates are imported
    if "staging" in lowered and "certificates" in lowered:
        return "imported"
    return "local"


def detect_class(name: str, prose: str) -> str:
    lowered_name = name.lower()
    lowered_prose = prose.lower()
    # Very rough classification – these thresholds are deliberately simple
    # but sufficient for the current corpus.
    if any(k in lowered_prose for k in NUMERICAL_KEYWORDS):
        return "numerical evidence"
    if any(k in lowered_name or k in lowered_prose for k in BOUNDED_KEYWORDS):
        return "bounded model"
    # If the prose mentions "kernel theorem" or the name matches a known pure kernel pattern, label as kernel
    if "kernel theorem" in lowered_prose:
        return "kernel theorem"
    if "cantor_no_surjection" in lowered_name or "universal_finitary_information_conservation" in lowered_name:
        return "kernel theorem"
    # Default to "bounded model" for most finite‑lattice citations; otherwise kernel
    if "finite" in lowered_prose or "lattice" in lowered_prose:
        return "bounded model"
    return "kernel theorem"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readme", default=None)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    readme_path = Path(args.readme).resolve() if args.readme else README
    readme_text = readme_path.read_text(encoding="utf-8")

    out_dir = Path(args.out_dir).resolve() if args.out_dir else LEDGER_DIR.parent / "claims"
    out_dir.mkdir(parents=True, exist_ok=True)

    cited = extract_cited(readme_text)
    audit = load_theorem_audit()
    resolved_map = audit.get("resolved_map", {}) if audit else {}

    ledger = []
    for ident, prose in cited:
        artifacts = resolved_map.get(ident, [])
        provenance = "unknown"
        if artifacts:
            # Use first artifact to infer provenance – this is a simplification.
            provenance = detect_provenance(artifacts[0])
        class_label = detect_class(ident, prose)
        ledger.append({
            "id": ident,
            "prose": prose,
            "artifact": artifacts,
            "theorem_name": ident,
            "provenance": provenance,
            "class": class_label,
        })

    # Write JSON ledger
    (out_dir / "ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Also dump a summary markdown in reports/claims/
    md_path = out_dir / "ledger.md"
    md_path.write_text(
        f"# Claims Ledger\n\n"
        f"- Generated: {__doc__}\n"
        f"- Total claims tracked: {len(ledger)}\n\n"
        f"| ID | Prose | Artifact(s) | Provenance | Class |\n"
        f"|---|---|---|---|---|\n"
        + "\n".join(
            f"| `{e['id']}` | `{e['prose']}` | `{', '.join(e['artifact'])}` | `{e['provenance']}` | `{e['class']}` |"
            for e in ledger
        ),
        encoding="utf-8",
    )

    print(f"Claims ledger written to {out_dir / 'ledger.json'} with {len(ledger)} entries.")
    return 0

if __name__ == "__main__":
    sys.exit(main())