#!/usr/bin/env python3
"""One-command repository seal.

Order is strict: remove transient audit artifacts, rebuild ``manifest.json``,
then run both independent integrity verifiers against the sealed tree. No
report-generating audit runs after the reseal, because a rewritten pinned
report invalidates the manifest.

Usage:
  python tools/seal_pipeline.py            # clean, reseal, verify
  python tools/seal_pipeline.py --check    # verify an existing seal only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

TRANSIENT_PATTERNS = (
    "reports/_*.log",
    "lean/spec_v4/_mut_*.lean",
)


def clean_transients() -> None:
    removed: list[str] = []
    for pattern in TRANSIENT_PATTERNS:
        for path in sorted(ROOT.glob(pattern)):
            path.unlink()
            removed.append(path.relative_to(ROOT).as_posix())
    if removed:
        for rel in removed:
            print(f"removed transient: {rel}")
    else:
        print("no transient audit files")


def run_step(name: str, args: list[str]) -> int:
    print(f"\n[{name}] {' '.join(args)}", flush=True)
    proc = subprocess.run(args, cwd=ROOT)
    if proc.returncode != 0:
        print(f"SEAL PIPELINE: FAIL at {name} (exit {proc.returncode})")
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seal and verify the repository ledger")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the existing seal without rebuilding manifest.json",
    )
    args = parser.parse_args(argv)

    if not args.check:
        clean_transients()
        rc = run_step("reseal", [PY, "mcp/t2n/core/repokeeper.py", "--reseal"])
        if rc != 0:
            return rc

    rc = run_step("repokeeper-verify", [PY, "mcp/t2n/core/repokeeper.py", "--verify"])
    if rc != 0:
        return rc

    rc = run_step(
        "manifest-verify",
        [PY, "tools/omega_audit/manifest_verify.py"],
    )
    if rc != 0:
        return rc

    print("\nSEAL PIPELINE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
