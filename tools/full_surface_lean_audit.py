#!/usr/bin/env python3
"""Full-surface Lean compile audit for Math 3.0.

`gate_strict.py` only scans trust tokens; it never type-checks.  This tool runs
`lake env lean` over every `.lean` file in the three claimed surfaces:

  - lean/spec_v4        (recursive)
  - Math30Kernel        (recursive, outside the lake package root)
  - Math30Interfaces    (recursive, outside the lake package root)

Each file is compiled independently (no local module imports exist, so this is
sound), with at most two concurrent Lean processes.  Results stream to a
checkpoint file so an interrupted run can be resumed, and a final JSON + Markdown
report is written to `reports/`.

Usage:
    python tools/full_surface_lean_audit.py [--workers 2] [--timeout 240]
                                            [--resume] [--only PATH_SUBSTRING]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
REPORTS = ROOT / "reports"
CHECKPOINT = REPORTS / "_full_surface_progress.jsonl"
JSON_REPORT = REPORTS / "full_surface_lean_audit.json"
MD_REPORT = REPORTS / "full_surface_lean_audit.md"

SURFACES = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]


def enumerate_files() -> list[Path]:
    files: list[Path] = []
    for surface in SURFACES:
        if not surface.exists():
            continue
        files.extend(sorted(surface.rglob("*.lean")))
    return sorted(set(f.resolve() for f in files))


def lean_relative(path: Path) -> str:
    """Path as passed to `lake env lean` (cwd = lean/), e.g. ../Math30Kernel/X.lean."""
    return os.path.relpath(path, LEAN_ROOT).replace("\\", "/")


def parse_warnings(stdout: str, stderr: str) -> int:
    return (stdout + "\n" + stderr).count("warning:")


def first_error_line(stdout: str, stderr: str) -> str:
    for line in (stderr + "\n" + stdout).splitlines():
        if "error" in line:
            return line.strip()[:300]
    for line in (stderr + "\n" + stdout).splitlines():
        if line.strip():
            return line.strip()[:300]
    return ""


def compile_one(path: Path, timeout: int) -> dict:
    rel = lean_relative(path)
    started = time.time()
    try:
        proc = subprocess.run(
            ["lake", "env", "lean", rel],
            cwd=LEAN_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        elapsed = round(time.time() - started, 2)
        warnings = parse_warnings(proc.stdout, proc.stderr)
        status = "PASS" if proc.returncode == 0 else "FAIL"
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "lean_path": rel,
            "rc": proc.returncode,
            "status": status,
            "warnings": warnings,
            "seconds": elapsed,
            "error": "" if status == "PASS" else first_error_line(proc.stdout, proc.stderr),
            "stdout_tail": proc.stdout[-2000:] if status != "PASS" else "",
            "stderr_tail": proc.stderr[-2000:] if status != "PASS" else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "lean_path": rel,
            "rc": None,
            "status": "TIMEOUT",
            "warnings": 0,
            "seconds": round(time.time() - started, 2),
            "error": f"exceeded {timeout}s",
            "stdout_tail": "",
            "stderr_tail": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "lean_path": rel,
            "rc": None,
            "status": "ERROR",
            "warnings": 0,
            "seconds": round(time.time() - started, 2),
            "error": f"{type(exc).__name__}: {exc}"[:300],
            "stdout_tail": "",
            "stderr_tail": "",
        }


def load_checkpoint() -> dict[str, dict]:
    done: dict[str, dict] = {}
    if CHECKPOINT.exists():
        for line in CHECKPOINT.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("path"):
                done[row["path"]] = row
    return done


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--only", default=None, help="only paths containing this substring")
    args = parser.parse_args()

    workers = max(1, min(2, args.workers))
    REPORTS.mkdir(exist_ok=True)

    files = enumerate_files()
    if args.only:
        needle = args.only.lower()
        files = [f for f in files if needle in str(f).lower()]

    done = load_checkpoint() if args.resume else {}
    if not args.resume and CHECKPOINT.exists():
        CHECKPOINT.unlink()

    pending = [f for f in files if str(f.relative_to(ROOT)).replace("\\", "/") not in done]

    log_path = REPORTS / "full_surface_lean_audit.log"
    log = open(log_path, "a", encoding="utf-8")  # noqa: SIM115
    log.write(f"\n=== run start {time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"files={len(files)} pending={len(pending)} workers={workers} ===\n")
    log.flush()

    completed = len(done)
    total = len(files)

    def record(row: dict) -> None:
        nonlocal completed
        done[row["path"]] = row
        completed += 1
        with CHECKPOINT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        flag = row["status"]
        log.write(f"[{completed}/{total}] {flag:7s} {row['seconds']:7.2f}s "
                  f"{row['path']}{'' if flag == 'PASS' else ' :: ' + row['error']}\n")
        log.flush()

    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(compile_one, f, args.timeout): f for f in pending}
            for fut in concurrent.futures.as_completed(futures):
                record(fut.result())

    log.write(f"=== run end {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    log.close()

    results = sorted(done.values(), key=lambda r: r["path"])
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    warn_total = sum(1 for r in results if r["status"] == "PASS" and r.get("warnings", 0) > 0)
    total_seconds = round(sum(r.get("seconds", 0) for r in results), 1)

    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "surfaces": [str(s.relative_to(ROOT)).replace("\\", "/") for s in SURFACES],
        "total_files": len(files),
        "compiled": len(results),
        "counts": counts,
        "pass_with_warnings": warn_total,
        "total_seconds": total_seconds,
        "failures": [
            {
                "path": r["path"],
                "status": r["status"],
                "rc": r["rc"],
                "error": r["error"],
            }
            for r in results
            if r["status"] != "PASS"
        ],
        "warning_files": [
            {"path": r["path"], "warnings": r["warnings"]}
            for r in results
            if r["status"] == "PASS" and r.get("warnings", 0) > 0
        ],
        "results": results,
    }
    JSON_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Full-Surface Lean Compile Audit",
        "",
        f"- Generated: {report['generated']}",
        f"- Surfaces: {', '.join('`' + s + '`' for s in report['surfaces'])}",
        f"- Total files: **{report['total_files']}**",
        f"- Compiled: **{report['compiled']}**",
        f"- Counts: `{counts}`",
        f"- PASS files with compiler warnings: **{warn_total}**",
        f"- Aggregate compile time: {total_seconds}s",
        "",
        "## Failures",
        "",
    ]
    if report["failures"]:
        md += ["| Status | File | Detail |", "|---|---|---|"]
        for f in report["failures"]:
            detail = f["error"].replace("|", "\\|")
            md.append(f"| {f['status']} | `{f['path']}` | {detail} |")
    else:
        md.append("None. Every enumerated Lean file compiled with `exit 0`.")

    md += ["", "## Warnings (PASS with diagnostics)", ""]
    if report["warning_files"]:
        md += ["| File | Warnings |", "|---|---|"]
        for w in report["warning_files"]:
            md.append(f"| `{w['path']}` | {w['warnings']} |")
    else:
        md.append("None. All compiling files emitted no warnings.")

    MD_REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"total={report['total_files']} compiled={report['compiled']} counts={counts}")
    print(f"pass_with_warnings={warn_total} seconds={total_seconds}")
    for f in report["failures"]:
        print(f"{f['status']}: {f['path']} :: {f['error']}")

    ok = counts.get("FAIL", 0) == 0 and counts.get("TIMEOUT", 0) == 0 and counts.get("ERROR", 0) == 0
    if ok and report["compiled"] == report["total_files"]:
        CHECKPOINT.unlink(missing_ok=True)
    return 0 if ok and report["compiled"] == report["total_files"] else 1


if __name__ == "__main__":
    sys.exit(main())
