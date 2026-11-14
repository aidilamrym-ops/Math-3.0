#!/usr/bin/env python3
"""Full-surface Lean compile audit for Math 3.0.

`gate_strict.py` only scans trust tokens; it never type-checks.  This tool runs
`lake env lean` over every `.lean` file in the three claimed surfaces:

  - lean/spec_v4        (recursive)
  - Math30Kernel        (recursive, outside the lake package root)
  - Math30Interfaces    (recursive, outside the lake package root)

Scope discipline
----------------
Only a run over the complete default surface may write the canonical receipt
``full_surface_lean_audit.json``.  Filtered runs (``--only``), custom surfaces
(``--surface``) and custom receipt directories write ``*_partial.*`` receipts
instead.  Before 2026-11-11 a one-file ``--only`` run overwrote the canonical
receipt with ``total_files = 1``; the README then reported "1 full-surface Lean
file".  That failure mode is now structurally impossible: the canonical path is
selected by scope, not by whoever ran last.

A receipt is *complete* only when every enumerated file was compiled, every
outcome is ``PASS``, and the scope is the full default surface.  Consumers must
check ``is_complete``; they must not infer completeness from exit status alone.

Each file is compiled independently (no local module imports exist, so a file
cannot depend on another audited file).  Transient toolchain failures (missing
olean reads, allocator panics, lock contention) are retried once, serially, and
the retry is recorded.  Results stream to a checkpoint so an interrupted run can
be resumed; stale checkpoint rows for files that no longer exist are discarded.

Usage:
    python tools/full_surface_lean_audit.py [--workers 2] [--timeout 240]
                                            [--resume] [--only PATH_SUBSTRING]
                                            [--surface DIR ...] [--out-dir DIR]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
DEFAULT_REPORTS = ROOT / "reports"

DEFAULT_SURFACES = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]

# A failed `lake env lean` invocation is not always a failed proof.  Concurrent
# reads of a partially materialised olean cache, allocator exhaustion and file
# locking all surface as compiler failures.  They are retried once, serially;
# a genuine type error is retried needlessly but still fails, so the retry can
# only remove false negatives, never accept a false positive.
TRANSIENT_FAILURE = re.compile(
    r"failed to read file|INTERNAL PANIC|out of memory|"
    r"Resource temporarily unavailable|Cannot allocate memory",
)


def is_full_scope(surfaces: list[Path], only: str | None, out_dir: Path) -> bool:
    """True iff this invocation audits exactly the complete default surface.

    The canonical receipt is written only for such a run.  Path comparison is
    resolved and case-insensitive on Windows so `--surface lean\\spec_v4` and
    the default do not produce two different notions of "full".
    """
    if only is not None:
        return False
    if out_dir.resolve() != DEFAULT_REPORTS.resolve():
        return False
    requested = {os.path.normcase(str(p.resolve())) for p in surfaces}
    default = {os.path.normcase(str(p.resolve())) for p in DEFAULT_SURFACES}
    return requested == default


def is_transient(row: dict) -> bool:
    blob = " ".join(
        str(row.get(key) or "") for key in ("error", "stdout_tail", "stderr_tail")
    )
    return bool(TRANSIENT_FAILURE.search(blob))


def enumerate_files(surfaces: list[Path]) -> list[Path]:
    files: list[Path] = []
    for surface in surfaces:
        if not surface.exists():
            continue
        files.extend(sorted(surface.rglob("*.lean")))
    return sorted(set(f.resolve() for f in files))


def lean_relative(path: Path) -> str:
    """Path as passed to `lake env lean` (cwd = lean/)."""
    try:
        rel = path.relative_to(LEAN_ROOT)
    except ValueError:
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


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
            "path": display_path(path),
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
            "path": display_path(path),
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
            "path": display_path(path),
            "lean_path": rel,
            "rc": None,
            "status": "ERROR",
            "warnings": 0,
            "seconds": round(time.time() - started, 2),
            "error": f"{type(exc).__name__}: {exc}"[:300],
            "stdout_tail": "",
            "stderr_tail": "",
        }


def load_checkpoint(path: Path) -> dict[str, dict]:
    done: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
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
    parser.add_argument(
        "--surface", action="append", default=None,
        help="override the audited directories (repeatable)",
    )
    parser.add_argument(
        "--out-dir", default=None,
        help="directory for reports/checkpoint (default: reports/)",
    )
    args = parser.parse_args()

    workers = max(1, min(2, args.workers))
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_REPORTS
    out_dir.mkdir(parents=True, exist_ok=True)

    surfaces = [Path(s).resolve() for s in args.surface] if args.surface else DEFAULT_SURFACES
    full_scope = is_full_scope(surfaces, args.only, out_dir)
    suffix = "" if full_scope else "_partial"

    checkpoint_path = out_dir / f"_full_surface_progress{suffix}.jsonl"
    json_report = out_dir / f"full_surface_lean_audit{suffix}.json"
    md_report = out_dir / f"full_surface_lean_audit{suffix}.md"
    log_path = out_dir / f"full_surface_lean_audit{suffix}.log"

    files = enumerate_files(surfaces)
    if args.only:
        needle = args.only.lower()
        files = [f for f in files if needle in str(f).lower()]

    current_paths = {display_path(f) for f in files}
    done = load_checkpoint(checkpoint_path) if args.resume else {}
    # A checkpoint from an older tree must never contribute rows for files that
    # are not part of this run: that would inflate `compiled` above `total`.
    done = {key: row for key, row in done.items() if key in current_paths}
    if not args.resume and checkpoint_path.exists():
        checkpoint_path.unlink()

    pending = [f for f in files if display_path(f) not in done]

    log = open(log_path, "a", encoding="utf-8")  # noqa: SIM115
    log.write(f"\n=== run start {time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"scope={'full' if full_scope else 'partial'} "
              f"files={len(files)} pending={len(pending)} workers={workers} ===\n")
    log.flush()

    completed = len(done)
    total = len(files)

    def record(row: dict) -> None:
        nonlocal completed
        done[row["path"]] = row
        completed += 1
        with checkpoint_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        flag = row["status"]
        log.write(f"[{completed}/{total}] {flag:7s} {row['seconds']:7.2f}s "
                  f"{row['path']}{'' if flag == 'PASS' else ' :: ' + row['error']}\n")
        log.flush()

    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(compile_one, f, args.timeout): f for f in pending}
            for fut in concurrent.futures.as_completed(futures):
                row = fut.result()
                if row["status"] != "PASS" and is_transient(row):
                    retried = compile_one(futures[fut], args.timeout)
                    retried["retried_after_transient"] = True
                    retried["first_attempt_error"] = row.get("error", "")[:300]
                    row = retried
                record(row)

    log.write(f"=== run end {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    log.close()

    results = sorted(done.values(), key=lambda r: r["path"])
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    warn_total = sum(1 for r in results if r["status"] == "PASS" and r.get("warnings", 0) > 0)
    total_seconds = round(sum(r.get("seconds", 0) for r in results), 1)
    all_attempted = len(results) == len(files)
    all_passed = all(r["status"] == "PASS" for r in results)
    is_complete = bool(full_scope and all_attempted and all_passed)
    if is_complete:
        verdict = "PASS"
    elif not full_scope:
        verdict = "PARTIAL" if all_passed and all_attempted else "PARTIAL_FAIL"
    else:
        verdict = "INCOMPLETE" if not all_attempted else "FAIL"

    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scope": {
            "kind": "full" if full_scope else "partial",
            "only": args.only,
            "surfaces": [display_path(s) for s in surfaces],
            "canonical_receipt": full_scope,
        },
        "is_complete": is_complete,
        "verdict": verdict,
        "surfaces": [display_path(s) for s in surfaces],
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
    json_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# Full-Surface Lean Compile Audit",
        "",
        f"- Generated: {report['generated']}",
        f"- Scope: **{report['scope']['kind']}** "
        f"(canonical receipt: {str(report['scope']['canonical_receipt']).lower()})",
        f"- Verdict: **{report['verdict']}** (complete: {str(report['is_complete']).lower()})",
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

    md_report.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"scope={report['scope']['kind']} verdict={verdict} "
          f"total={report['total_files']} compiled={report['compiled']} counts={counts}")
    print(f"pass_with_warnings={warn_total} seconds={total_seconds} "
          f"complete={str(is_complete).lower()} receipt={json_report}")
    for f in report["failures"]:
        print(f"{f['status']}: {f['path']} :: {f['error']}")

    all_ok = all_attempted and all_passed
    if all_ok:
        checkpoint_path.unlink(missing_ok=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
