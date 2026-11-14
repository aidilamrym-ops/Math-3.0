#!/usr/bin/env python3
"""Strict, fail-closed anti-circularity gate for the Math 3.0 Lean surface.

Why this wrapper exists
-----------------------
The installed skill gate (``anti-circularity/scripts/gate.py``) is the gate of
record for placeholder tokens. On 2026-11-10 it was falsified with Lean files
that compile with exit 0 and still carry a trust token:

  * ``private axiom`` and ``@[simp] axiom``       -> gate reported PASS
  * ``@sorryAx False true``                       -> gate reported PASS
  * ``let _s := "a--b"; (sorry : Nat)``           -> gate reported PASS

The first two evade the line-anchored ``axiom`` pattern; ``\\bsorry\\b`` does not
match ``sorryAx``; and the gate's comment stripper treats ``--`` inside a string
literal as a line comment. The evidence is archived in
``reports/omega_audit/falsification/`` and in the anomaly ledger entries
OMEGA-0013/OMEGA-0014.

This wrapper does not silently replace the skill gate. It runs the skill gate
first, forwards its verdict verbatim, then applies a stricter lexer and a
wider trust-token policy. Both must pass. Resolution order is: explicit
``--gate``, ``ANTI_CIRCULARITY_GATE``, the repo-local vendored copy used by CI
(``tools/omega_audit/vendor/anti_circularity_gate.py``), then the installed
skill. The vendored copy is byte-identical to the gate of record; its hash is
recorded in ``reports/omega_audit/vendored_gate_provenance.json``. Exit codes
follow the skill gate:

  0  PASS
  1  FAIL
  2  TOOL NOT RUN (gate or input unavailable)

No network access. No writes outside an explicit ``--json`` path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_NOT_RUN = 2

SKIP_DIRS = {".lake", ".git", ".hg", ".svn", "node_modules", "__pycache__"}

# Declaration-level trust extensions. The patterns run on text in which
# comments and string/char literals have been blanked, so a token in prose
# cannot trigger them.
DECL_PREFIX = r"(?m)^[ \t]*(?:@\[[^\n]*\][ \t]*)*"
MODIFIERS = r"(?:(?:private|protected|noncomputable|unsafe)[ \t]+)*"

STRICT_TOKENS = (
    ("sorry", re.compile(r"\bsorry\b")),
    ("sorryAx", re.compile(r"\bsorryAx\b")),
    ("admit", re.compile(r"\badmit\b")),
    ("axiom", re.compile(DECL_PREFIX + MODIFIERS + r"axiom\b")),
    ("constant", re.compile(DECL_PREFIX + MODIFIERS + r"constant\b")),
    ("opaque", re.compile(DECL_PREFIX + r"(?:private[ \t]+)?opaque\b")),
    ("partial_def", re.compile(DECL_PREFIX + r"(?:private[ \t]+)?partial[ \t]+def\b")),
    ("native_decide", re.compile(r"\bnative_decide\b")),
    ("implemented_by", re.compile(r"@\[[^\]]*\bimplemented_by\b")),
    ("extern", re.compile(r"@\[[^\]]*\bextern\b")),
)

RAW_STRING = re.compile(r'r(#*)"')


def find_external_gate(explicit: str | None) -> Path | None:
    """Locate the skill gate without scanning the disk."""
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("ANTI_CIRCULARITY_GATE")
    if env:
        candidates.append(Path(env))
    candidates.append(
        Path(__file__).resolve().parents[2]
        / "tools"
        / "omega_audit"
        / "vendor"
        / "anti_circularity_gate.py"
    )
    home = Path.home()
    candidates.append(
        home / ".config" / "opencode" / "skills" / "anti-circularity" / "scripts" / "gate.py"
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def blank_comments_and_literals(text: str) -> str:
    """Blank Lean comments and string/char literals, preserving line count.

    Newlines are kept so a line number computed on the result still points at
    the same line in the original source. This lexer understands nested block
    comments, line comments, ordinary strings with backslash escapes, raw
    strings (``r"..."``, ``r#"..."#``), and simple character literals.
    """
    out = list(text)
    length = len(text)
    index = 0
    depth = 0

    def blank(start: int, end: int) -> None:
        for position in range(start, min(end, length)):
            if text[position] != "\n":
                out[position] = " "

    while index < length:
        if depth:
            if text.startswith("/-", index):
                depth += 1
                blank(index, index + 2)
                index += 2
                continue
            if text.startswith("-/", index):
                depth -= 1
                blank(index, index + 2)
                index += 2
                continue
            blank(index, index + 1)
            index += 1
            continue

        if text.startswith("--", index):
            end = text.find("\n", index)
            if end == -1:
                end = length
            blank(index, end)
            index = end
            continue

        if text.startswith("/-", index):
            depth = 1
            blank(index, index + 2)
            index += 2
            continue

        # Raw string: r"..." or r#"..."#. Detect at the introducing r.
        if text[index] == "r" and (index == 0 or not (text[index - 1].isalnum() or text[index - 1] in "_'")):
            raw = RAW_STRING.match(text, index)
            if raw:
                closing = '"' + raw.group(1)
                end = text.find(closing, raw.end())
                end = length if end == -1 else end + len(closing)
                blank(index, end)
                index = end
                continue

        if text[index] == '"':
            start = index
            index += 1
            while index < length:
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == '"':
                    index += 1
                    break
                index += 1
            blank(start, index)
            continue

        # Character literal. A prime in an identifier (foo') is not a literal.
        if text[index] == "'":
            if index + 2 < length and text[index + 2] == "'" and text[index + 1] not in ("'", "\\"):
                blank(index, index + 3)
                index += 3
                continue
            if index + 1 < length and text[index + 1] == "\\":
                end = text.find("'", index + 2, min(length, index + 14))
                if end != -1:
                    blank(index, end + 1)
                    index = end + 1
                    continue

        index += 1

    return "".join(out)


def collect_lean(paths: list[str]) -> tuple[list[Path], list[Path]]:
    """Return (Lean files, missing inputs). Directories are walked recursively."""
    files: list[Path] = []
    missing: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for current, dirnames, filenames in os.walk(path):
                dirnames[:] = sorted(
                    name for name in dirnames if name not in SKIP_DIRS
                )
                for name in sorted(filenames):
                    if name.lower().endswith(".lean"):
                        files.append(Path(current) / name)
        elif path.is_file():
            if path.suffix.lower() == ".lean":
                files.append(path)
        else:
            missing.append(path)
    return sorted(set(files)), missing


def line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan(paths: list[str]) -> tuple[list[str], list[str], int]:
    """Apply the strict token policy. Returns (findings, not_run, file_count)."""
    findings: list[str] = []
    not_run: list[str] = []
    files, missing = collect_lean(paths)
    not_run.extend("MISSING INPUT %s" % path for path in missing)

    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            not_run.append("UNREADABLE %s (%s)" % (path, error))
            continue
        clean = blank_comments_and_literals(raw)
        seen: set[tuple[int, str]] = set()
        for label, pattern in STRICT_TOKENS:
            for match in pattern.finditer(clean):
                line = line_at(clean, match.start())
                key = (line, label)
                if key in seen:
                    continue
                seen.add(key)
                source_line = raw.splitlines()[line - 1].strip() if line - 1 < len(raw.splitlines()) else ""
                findings.append(
                    "%s:%d: %s trust token :: %s"
                    % (path, line, label, source_line[:160])
                )

    if not files:
        not_run.append("NO_LEAN_FILES: no .lean input matched")
    return findings, not_run, len(files)


def run_external(
    gate: Path | None, command: str, paths: list[str]
) -> tuple[int | None, str, list[str]]:
    if gate is None:
        return None, "", ["EXTERNAL_GATE_NOT_FOUND: set ANTI_CIRCULARITY_GATE or --gate"]
    cmd = [sys.executable, str(gate), command] + paths
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        return None, "", ["EXTERNAL_GATE_NOT_RUN: %s" % error]
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output, []


def emit(
    command: str,
    files_scanned: int,
    external_exit: int | None,
    external_output: str,
    findings: list[str],
    not_run: list[str],
) -> int:
    if external_output:
        print(external_output.rstrip("\n"))
    print("-" * 78)
    print("MATH 3.0 STRICT GATE [%s]" % command)
    for finding in findings:
        print("  FAIL     %s" % finding)
    for item in not_run:
        print("  NOT RUN  %s" % item)
    print("  lean files scanned: %d" % files_scanned)
    print(
        "  result: FINDINGS=%d  NOT_RUN=%d  EXTERNAL_EXIT=%s"
        % (len(findings), len(not_run), external_exit)
    )

    if findings or external_exit == EXIT_FAIL:
        print("  verdict: FAIL")
        return EXIT_FAIL
    if not_run or external_exit == EXIT_NOT_RUN:
        print("  verdict: TOOL NOT RUN")
        return EXIT_NOT_RUN
    print("  verdict: PASS")
    return EXIT_PASS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gate_strict.py",
        description="Strict anti-circularity gate for Lean sources.",
    )
    parser.add_argument("command", choices=("lean", "check"), nargs="?", default="check")
    parser.add_argument("paths", nargs="+", help="files or directories to gate")
    parser.add_argument("--gate", default=None, help="path to the skill gate.py")
    parser.add_argument("--json", default=None, help="write a JSON receipt to this path")
    args = parser.parse_args(argv)

    gate = find_external_gate(args.gate)
    external_exit, external_output, external_not_run = run_external(
        gate, args.command, args.paths
    )
    findings, not_run, files_scanned = scan(args.paths)
    not_run = external_not_run + not_run

    verdict_code = emit(
        args.command,
        files_scanned,
        external_exit,
        external_output,
        findings,
        not_run,
    )
    verdict = {EXIT_PASS: "PASS", EXIT_FAIL: "FAIL", EXIT_NOT_RUN: "TOOL_NOT_RUN"}[verdict_code]

    if args.json:
        receipt = {
            "tool": "math30_strict_gate",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": args.command,
            "external_gate": str(gate) if gate else None,
            "external_exit": external_exit,
            "files_scanned": files_scanned,
            "findings": findings,
            "not_run": not_run,
            "verdict": verdict,
        }
        try:
            with open(args.json, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(receipt, handle, indent=2)
                handle.write("\n")
        except OSError as error:
            print("NOT RUN: cannot write JSON receipt: %s" % error)
            return EXIT_NOT_RUN

    return verdict_code


if __name__ == "__main__":
    raise SystemExit(main())
