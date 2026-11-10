"""Fast placeholder pre-scan for the Math 3.0 Lean surface.

This is deliberately NOT a verification result. It answers exactly one
question: does any Lean source contain a placeholder or trust token after
comments and string literals are removed? It does not compile anything and
does not inspect axioms of compiled theorems. Use tools/lean_surface_audit.py
for compilation and tools/omega_audit/gate_strict.py for the full trust scan.

The previous revision of this file caught every exception with `pass` and
printed "AUDIT PASSED: ZERO KERNEL DEVIATIONS" unconditionally. That is audit
theater; it is replaced here (OMEGA-0027).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from smt_lean_bridge import find_placeholders

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOTS = ("lean", "Math30Kernel", "Math30Interfaces")
EXCLUDED_PARTS = {".git", "__pycache__", ".lake", "staging", "fixtures", "repaired"}


def discover() -> list[Path]:
    files: set[Path] = set()
    for base in LEAN_ROOTS:
        root = ROOT / base
        if not root.is_dir():
            continue
        for current, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in EXCLUDED_PARTS and not name.startswith(".")
            ]
            for name in filenames:
                if name.endswith(".lean"):
                    files.add(Path(current) / name)
    return sorted(files)


def main() -> int:
    files = discover()
    findings: list[str] = []
    unreadable: list[str] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            unreadable.append("%s: %s" % (path, error))
            continue
        tokens = find_placeholders(source)
        if tokens:
            findings.append("%s: %s" % (path.relative_to(ROOT), ", ".join(tokens)))

    print("FAST PLACEHOLDER PRE-SCAN (not a compile check)")
    print("lean files scanned: %d" % len(files))
    print("placeholder files: %d" % len(findings))
    for finding in findings:
        print("  [TOKEN] %s" % finding)
    for problem in unreadable:
        print("  [UNREADABLE] %s" % problem)

    if findings or unreadable:
        print("RESULT: FAIL (placeholder or unreadable input present)")
        return 1
    print("RESULT: CLEAN (no placeholder tokens; compilation not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
