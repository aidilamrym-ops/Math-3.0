"""Math 3.0 — whole-surface Lean audit.

Compiles every Lean source outside ``staging`` and fixtures, scans each file for
placeholder tokens, and optionally runs the compiler-guided repair agent on
failures (read-only: repaired candidates are written to ``lean/repaired`` and
the original file is never overwritten).

A ``PASSED`` verdict means: every discovered Lean file compiled with exit 0 and
no file contained ``sorry``, ``admit``, or ``axiom`` after comment/string
stripping.  Warnings are recorded but do not fail the audit.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smt_lean_bridge import find_placeholders, lean_version  # noqa: E402

AUDIT_NAME = "math30_lean_surface_audit"
AUDIT_VERSION = "1.0.0"

DEFAULT_GLOBS = ("lean", "Math30Kernel", "Math30Interfaces")
EXCLUDED_PARTS = {".git", "__pycache__", ".lake", "staging", "fixtures", "repaired"}
# Disk/memory pressure under parallel compilation produces spurious failures
# ("failed to read file *.olean.private", "INTERNAL PANIC: out of memory").
# Such a failure is retried once, serially, before it is reported.
TRANSIENT_FAILURE = re.compile(
    r"failed to read file|INTERNAL PANIC|out of memory|Resource temporarily unavailable"
)


def discover(root: str, globs: tuple[str, ...]) -> list[str]:
    files: list[str] = []
    for base in globs:
        base_path = os.path.join(root, base)
        if not os.path.isdir(base_path):
            continue
        for current, dirnames, filenames in os.walk(base_path):
            dirnames[:] = [name for name in dirnames if name not in EXCLUDED_PARTS]
            for filename in filenames:
                if filename.endswith(".lean"):
                    files.append(os.path.join(current, filename))
    return sorted(set(files))


def compile_one(path: str, root: str, timeout: int) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    placeholders = find_placeholders(source)
    started = time.perf_counter()

    # Compile through the project's pinned Lake environment. A bare `lean`
    # invocation from the repository root does not see the Mathlib search
    # path, so every file that imports Mathlib fails with an unknown module
    # prefix even though `lake env lean` compiles it (falsified 2026-11-10).
    lake = shutil.which("lake")
    lean_dir = os.path.join(root, "lean")
    if lake and os.path.isdir(lean_dir):
        command = [lake, "env", "lean", os.path.relpath(path, lean_dir)]
        compile_cwd = lean_dir
    else:
        command = ["lean", path]
        compile_cwd = root

    result = subprocess.run(
        command,
        cwd=compile_cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    compilation_output = "\n".join(
        part for part in (result.stdout.strip(), result.stderr.strip()) if part
    )
    return {
        "path": os.path.relpath(path, root).replace("\\", "/"),
        "absolute_path": path,
        "exit_code": result.returncode,
        "compiled": result.returncode == 0,
        "placeholders": placeholders,
        "elapsed_ms": elapsed_ms,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "output": compilation_output,
    }


def repair_failure(
    *,
    path: str,
    root: str,
    timeout: int,
    max_attempts: int,
) -> dict[str, Any]:
    agent = os.path.join(root, "tools", "proof_repair_agent.py")
    output = os.path.join(root, "lean", "repaired", os.path.basename(path))
    receipt = os.path.join(
        root,
        "reports",
        f"proof_repair_{os.path.splitext(os.path.basename(path))[0]}.json",
    )
    result = subprocess.run(
        [
            sys.executable,
            agent,
            "--file",
            path,
            "--out",
            output,
            "--json",
            receipt,
            "--max-attempts",
            str(max_attempts),
            "--timeout",
            str(timeout),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return {
        "path": os.path.relpath(path, root).replace("\\", "/"),
        "agent_exit_code": result.returncode,
        "candidate": os.path.relpath(output, root).replace("\\", "/")
        if os.path.isfile(output)
        else None,
        "receipt": os.path.relpath(receipt, root).replace("\\", "/")
        if os.path.isfile(receipt)
        else None,
        "agent_stdout": result.stdout.strip(),
        "agent_stderr": result.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Math 3.0 whole-surface Lean audit")
    parser.add_argument("--root", default=None)
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 4))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--repair-failures", action="store_true")
    parser.add_argument("--max-repair-attempts", type=int, default=12)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    root = os.path.abspath(args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    lean = lean_version()
    lake = shutil.which("lake")
    files = discover(root, DEFAULT_GLOBS)
    report: dict[str, Any] = {
        "audit": AUDIT_NAME,
        "audit_version": AUDIT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root": root,
        "lean": lean,
        "lake": lake,
        "jobs": args.jobs,
        "file_count": len(files),
        "compiled": 0,
        "failed": 0,
        "placeholder_files": [],
        "failures": [],
        "repairs": [],
        "verdict": "UNKNOWN",
    }

    if not lean["available"] or not lake:
        report["verdict"] = "TOOL_NOT_RUN"
        report["toolchain_error"] = (
            "Lean unavailable" if not lean["available"] else "Lake unavailable"
        )
        print(json.dumps(report, indent=2))
        return 2

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(compile_one, path, root, args.timeout): path for path in files}
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                results.append(future.result())
            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "path": os.path.relpath(path, root).replace("\\", "/"),
                        "absolute_path": path,
                        "exit_code": None,
                        "compiled": False,
                        "placeholders": find_placeholders(
                            open(path, encoding="utf-8", errors="replace").read()
                        ),
                        "elapsed_ms": args.timeout * 1000,
                        "stdout": "",
                        "stderr": f"timeout after {args.timeout}s",
                        "output": f"timeout after {args.timeout}s",
                    }
                )
            except Exception as error:  # fail closed, preserve diagnostics
                results.append(
                    {
                        "path": os.path.relpath(path, root).replace("\\", "/"),
                        "absolute_path": path,
                        "exit_code": None,
                        "compiled": False,
                        "placeholders": [],
                        "elapsed_ms": 0.0,
                        "stdout": "",
                        "stderr": f"{type(error).__name__}: {error}",
                        "output": f"{type(error).__name__}: {error}",
                    }
                )

    for index, result in enumerate(results):
        if result["compiled"] or not TRANSIENT_FAILURE.search(result.get("output") or ""):
            continue
        retried = compile_one(result["absolute_path"], root, args.timeout)
        retried["retried_after"] = result.get("output", "")[:400]
        results[index] = retried

    for result in sorted(results, key=lambda item: item["path"]):
        if result["compiled"]:
            report["compiled"] += 1
        else:
            report["failed"] += 1
            report["failures"].append(
                {
                    "path": result["path"],
                    "exit_code": result["exit_code"],
                    "elapsed_ms": result["elapsed_ms"],
                    "stderr": result["stderr"][:4000],
                    "stdout": result["stdout"][:4000],
                }
            )
        if result["placeholders"]:
            report["placeholder_files"].append(
                {"path": result["path"], "placeholders": result["placeholders"]}
            )

    if args.repair_failures:
        for failure in report["failures"]:
            absolute = os.path.join(root, failure["path"])
            report["repairs"].append(
                repair_failure(
                    path=absolute,
                    root=root,
                    timeout=args.timeout,
                    max_attempts=args.max_repair_attempts,
                )
            )

    if report["failed"] == 0 and not report["placeholder_files"]:
        report["verdict"] = "PASSED"
    else:
        report["verdict"] = "FAILED"

    receipt_path = args.json or os.path.join(root, "reports", "lean_surface_audit.json")
    os.makedirs(os.path.dirname(os.path.abspath(receipt_path)), exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)

    print("=== MATH 3.0 LEAN SURFACE AUDIT ===")
    print(f"lean: {lean.get('version')}")
    print(f"files: {len(files)}  compiled: {report['compiled']}  failed: {report['failed']}")
    print(f"placeholder files: {len(report['placeholder_files'])}")
    for failure in report["failures"][:20]:
        print(f"[FAIL] {failure['path']} (exit {failure['exit_code']})")
        first_line = (failure["stderr"] or failure["stdout"]).splitlines()
        if first_line:
            print(f"       {first_line[0][:180]}")
    if len(report["failures"]) > 20:
        print(f"       ... {len(report['failures']) - 20} more failures in the receipt")
    for repair in report["repairs"]:
        print(
            f"[REPAIR] {repair['path']} -> agent exit {repair['agent_exit_code']} "
            f"candidate={repair['candidate']}"
        )
    print(f"VERDICT: {report['verdict']}")
    print(f"receipt: {receipt_path}")

    if report["verdict"] == "PASSED":
        return 0
    return 2 if report["verdict"] == "TOOL_NOT_RUN" else 1


if __name__ == "__main__":
    sys.exit(main())
