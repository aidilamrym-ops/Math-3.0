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
import shutil
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
        target = destination / name
        shutil.copyfile(source, target)
        mode = target.stat().st_mode
        target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        installed.append(str(target))

    print("HOOKS INSTALLED")
    for path in installed:
        print("  %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
