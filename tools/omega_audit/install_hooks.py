#!/usr/bin/env python3
"""Install the versioned Math 3.0 git hooks.

Copies tools/hooks/pre-commit and tools/hooks/pre-push into the repository's
actual hooks directory (worktree-aware, via `git rev-parse --git-path hooks`),
and marks them executable where the platform supports it.

Usage:
  python tools/omega_audit/install_hooks.py
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "hooks"
NAMES = ("pre-commit", "pre-push")


def hooks_directory() -> Path:
    proc = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode == 0 and proc.stdout.strip():
        path = Path(proc.stdout.strip())
        return path if path.is_absolute() else (ROOT / path).resolve()
    return ROOT / ".git" / "hooks"


def normalized_bytes(source: Path) -> bytes:
    """Hook payload with LF endings and no BOM.

    The working tree is checked out with CRLF under ``core.autocrlf=true`` on
    Windows, but git executes hooks with ``sh``, whose parser rejects a CR
    before the line terminator. Normalizing at install time keeps the installed
    hook identical to the blob committed in the index.
    """
    data = source.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def main() -> int:
    destination = hooks_directory()
    if not destination.is_dir():
        print("FATAL: hooks directory not found: %s" % destination)
        return 1

    installed: list[str] = []
    for name in NAMES:
        source = SOURCE / name
        if not source.is_file():
            print("FATAL: missing versioned hook: %s" % source)
            return 1
        payload = normalized_bytes(source)
        if not payload.startswith(b"#!/bin/sh\n"):
            print("FATAL: hook does not start with a LF-terminated sh shebang: %s" % source)
            return 1
        target = destination / name
        target.write_bytes(payload)
        mode = target.stat().st_mode
        target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        if b"\r" in target.read_bytes():
            print("FATAL: installed hook still contains CR bytes: %s" % target)
            return 1
        installed.append(str(target))

    print("HOOKS INSTALLED")
    for path in installed:
        print("  %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
