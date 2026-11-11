#!/usr/bin/env python3
"""Bridge coverage audit: map JSON reports to Lean source files.

Detects mismatches between the two sets of artefacts:
  - JSON reports that do NOT have a corresponding Lean file (JSON no mirror)
  - Lean files that do NOT have a corresponding JSON report (certificates no mirror)

This is L5 from the recursive development plan.
"""

from __future__ import annotations

import argparse
import json
from typing import Any
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
LEAN_ROOT = ROOT / "lean"
LEAN_ROOTS = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]

def normalize_path(path_str: str) -> str:
    # Resolve relative indicators and clean up Windows slashes
    clean = path_str.replace("\\", "/")
    # If absolute path under ROOT, convert to relative
    root_str = str(ROOT).replace("\\", "/")
    if clean.startswith(root_str):
        clean = clean[len(root_str):].lstrip("/")
    # Handle ../ prefix if coming from lean/ directory
    if clean.startswith("../"):
        clean = clean[3:]
    return clean

def collect_lean_files() -> dict[str, None]:
    lean_files: dict[str, None] = {}
    for root in LEAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.lean"):
            try:
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                rel = str(path).replace("\\", "/")
            lean_files[rel] = None
    return lean_files

def collect_report_files() -> dict[str, None]:
    reports: dict[str, None] = {}
    if not REPORTS_DIR.is_dir():
        return reports
    
    # Helper to recursively find path-like values in nested JSON
    def find_paths(obj: Any):
        if isinstance(obj, dict):
            # Check for common fields that indicate a Lean file reference
            if "path" in obj and (str(obj["path"]).endswith(".lean") or "/" in str(obj["path"])):
                reports[normalize_path(str(obj["path"]))] = None
            if "lean_path" in obj:
                # Resolve relative lean_path if possible (heuristically)
                reports[normalize_path(str(obj["lean_path"]))] = None
            for v in obj.values():
                find_paths(v)
        elif isinstance(obj, list):
            for v in obj:
                find_paths(v)

    for path in REPORTS_DIR.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            find_paths(data)
        except Exception:
            continue
    return reports

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve() if args.out_dir else REPORTS_DIR / "bridge_coverage"
    out_dir.mkdir(parents=True, exist_ok=True)

    lean_files = collect_lean_files()
    report_files = collect_report_files()

    json_no_mirror = [p for p in report_files if p not in lean_files]
    cert_no_mirror = [p for p in lean_files if p not in report_files]

    summary = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lean_files_count": len(lean_files),
        "report_files_count": len(report_files),
        "json_no_mirror_count": len(json_no_mirror),
        "cert_no_mirror_count": len(cert_no_mirror),
        "json_no_mirror_examples": json_no_mirror[:20],
        "cert_no_mirror_examples": cert_no_mirror[:20],
    }

    json_path = out_dir / "bridge_coverage.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = out_dir / "bridge_coverage.md"
    md_lines = [
        "# Bridge Coverage Audit",
        "",
        f"- Generated: {summary['generated']}",
        f"- Total Lean files scanned: **{summary['lean_files_count']}**",
        f"- Total report files scanned: **{summary['report_files_count']}**",
        f"- JSON reports without a mirror Lean file: **{summary['json_no_mirror_count']}**",
        f"- Lean certificates without a mirror report: **{summary['cert_no_mirror_count']}**",
        "",
    ]
    if summary["json_no_mirror_count"]:
        md_lines += ["## JSON no mirror examples", ""]
        for ex in summary["json_no_mirror_examples"]:
            md_lines.append(f"- `{ex}`")
    if summary["cert_no_mirror_count"]:
        md_lines += ["## Certificates no mirror examples", ""]
        for ex in summary["cert_no_mirror_examples"]:
            md_lines.append(f"- `{ex}`")

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"bridge_coverage done: {len(lean_files)} lean, {len(report_files)} reports")
    return 0

if __name__ == "__main__":
    sys.exit(main())