#!/usr/bin/env python3
"""Audit every Lean file cited by README.MD by actually type-checking it.

`gate_strict.py` scans tokens; it does not compile.  This tool closes that gap for
the files the README claims are verified.  It resolves cited paths, deduplicates
them, compiles each with `lake env lean`, and writes a machine-readable report.

Runs sequentially by default (``--workers 1``); the ceiling is two Lean
processes.  An unresolved cited path fails the audit.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
README = ROOT / "README.MD"


def resolve_candidates(path_text: str) -> list[Path]:
    p = Path(path_text.replace("\\", "/"))
    candidates: list[Path] = []

    if p.parts and p.parts[0] == "lean":
        candidates.append(ROOT / p)
    else:
        candidates.extend(
            [
                LEAN_ROOT / p,
                LEAN_ROOT / "spec_v4" / p,
                LEAN_ROOT / "spec_v4" / "certificates" / p,
                LEAN_ROOT / "spec_v4" / "adversarial_tests" / p,
                LEAN_ROOT / "spec_v4" / "smt_bridge" / p,
                LEAN_ROOT / "smt_bridge" / p,
            ]
        )
    return candidates


def collect_files() -> tuple[list[Path], list[str]]:
    text = README.read_text(encoding="utf-8")
    cited = sorted(set(re.findall(r"`([^`]+\.lean)`", text)))
    found: dict[Path, str] = {}
    unresolved: list[str] = []

    for item in cited:
        for candidate in resolve_candidates(item):
            if candidate.is_file():
                found.setdefault(candidate.resolve(), item)
                break
        else:
            unresolved.append(item)

    return sorted(found), unresolved


def compile_one(path: Path) -> dict:
    try:
        rel = path.relative_to(LEAN_ROOT)
    except ValueError:
        return {
            "path": str(path),
            "rc": None,
            "status": "OUTSIDE_LEAN_ROOT",
            "stdout": "",
            "stderr": "",
        }

    try:
        proc = subprocess.run(
            ["lake", "env", "lean", str(rel)],
            cwd=LEAN_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )
        status = "PASS" if proc.returncode == 0 else "FAIL"
        return {
            "path": str(path.relative_to(ROOT)),
            "lean_path": str(rel),
            "rc": proc.returncode,
            "status": status,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "path": str(path.relative_to(ROOT)),
            "lean_path": str(rel),
            "rc": None,
            "status": "TIMEOUT",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    workers = max(1, min(2, args.workers))

    files, unresolved = collect_files()
    results: list[dict] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(compile_one, f) for f in files]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda r: (r["status"], r["path"]))
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "readme": str(README.relative_to(ROOT)),
        "workers": workers,
        "cited_unique_files": len(files),
        "unresolved_citations": unresolved,
        "counts": counts,
        "results": results,
    }

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "readme_lean_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md_lines = [
        "# README Lean Claim Audit",
        "",
        f"- Generated: {report['generated']}",
        f"- Workers: {workers}",
        f"- Cited unique files: {len(files)}",
        f"- Unresolved citations: {len(unresolved)}",
        f"- Counts: {counts}",
        "",
        "| Status | File | Notes |",
        "|---|---|---|",
    ]
    for r in results:
        note = ""
        if r["status"] != "PASS":
            first = (r["stderr"] or r["stdout"]).strip().splitlines()
            note = first[0][:180] if first else ""
        md_lines.append(f"| {r['status']} | `{r['path']}` | {note} |")
    if unresolved:
        md_lines += ["", "## Unresolved citations", ""]
        md_lines += [f"- `{u}`" for u in unresolved]
    (reports_dir / "readme_lean_audit.md").write_text(
        "\n".join(md_lines) + "\n", encoding="utf-8"
    )

    print(f"cited_unique_files={len(files)}")
    print(f"unresolved_citations={len(unresolved)}")
    print(f"counts={counts}")
    for r in results:
        if r["status"] != "PASS":
            print(f"{r['status']}: {r['path']}")
    # An unresolved citation is a failed claim, not a stylistic warning: the
    # README says the file exists and is compiled.  Before this repair the
    # exit code ignored `unresolved`, so a fabricated path passed the audit.
    return 0 if (
        counts.get("FAIL", 0) == 0
        and counts.get("TIMEOUT", 0) == 0
        and not unresolved
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
