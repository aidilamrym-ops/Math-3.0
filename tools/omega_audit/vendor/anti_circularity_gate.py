#!/usr/bin/env python3
"""Anti-circularity gates for formal-verification artifacts.

Three gates, each answering one question that prose alone cannot answer:

  lean    Do the Lean sources still contain placeholder proofs?
  claim   Is a stated solver verdict backed by a query and a run log?
  audit   Do the SMT-LIB2 scripts actually prove what they claim?

Exit codes, shared by every subcommand:

  0  PASS          no gate reported a problem
  1  FAIL          at least one gate reported a problem
  2  TOOL NOT RUN  a required tool or input was unavailable, or the solver
                   returned UNKNOWN / the file could not be parsed

UNKNOWN is never rewritten as success. Nothing in this module invents a
solver result: every verdict printed by the audit gate comes from a tool
that actually ran, and its output is forwarded verbatim.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_NOT_RUN = 2

# Extensions each gate accepts. Anything else is silently not applicable,
# so that `gate.py lean REPORT.md` does not report REPORT.md as missing.
LEAN_EXTS = {".lean"}
CLAIM_EXTS = {".lean", ".smt2", ".md", ".txt"}
AUDIT_EXTS = {".smt2"}

# AGENTS.md section 2.6: every placeholder must be reported by line number.
#
# The axiom pattern must anchor on SAME-LINE indentation only. `^\s*` under
# re.MULTILINE lets `\s*` run across newlines, so re.search() returns the start
# of the whitespace run rather than the declaration: because strip_lean_comments
# turns doc comments into spaces, that run can begin several lines above the
# axiom and the reported line number is wrong. `[ \t]*` keeps the match on the
# axiom's own line.
PLACEHOLDERS: Sequence[Tuple[str, str]] = (
    (r"\bsorry\b", "sorry"),
    (r"\badmit\b", "admit"),
    (r"^[ \t]*axiom\b", "axiom"),
    (r"\bAbort\b", "Abort"),
)

# AGENTS.md section 5: a comment asserting a verdict with no run log is a
# claim, not a result.
VERDICT_CLAIM = re.compile(r"MACHINE[\s_-]+RESULT", re.IGNORECASE)
SOLVER_VERDICT_LINE = re.compile(r"^\s*(sat|unsat|unknown)\s*$",
                                 re.IGNORECASE | re.MULTILINE)

# The auditor's own summary line, e.g.
#   summary: GENUINE=3  SINGLE_AXIOM=1  CIRCULAR=6  SAT=2  UNPARSEABLE=7
SUMMARY_LINE = re.compile(r"^summary:\s*(.*)$", re.MULTILINE)
SUMMARY_COUNT = re.compile(r"(\w+)=(\d+)")

# Verdicts that were reached but are NOT results: exit 1.
NON_RESULT_VERDICTS = ("CIRCULAR", "VACUOUS", "SAT", "CLAIM_IRRELEVANT",
                       "SINGLE_AXIOM")
# Verdicts that were never reached at all: exit 2.
NO_VERDICT_VERDICTS = ("UNKNOWN", "UNPARSEABLE")

AUDITOR_FILENAME = "smt_circularity_auditor.py"
AUDITOR_KNOWN_PATHS = (
    Path("auditor") / AUDITOR_FILENAME,
    Path(AUDITOR_FILENAME),
)


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def read_text(path: Path) -> Optional[str]:
    """Return the file content, or None if it cannot be decoded or read."""
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def strip_lean_comments(text: str) -> str:
    """Blank out Lean comments while preserving length and newline positions.

    Preserving newlines means a line number computed on the returned string
    still points at the same line in the original file, so reported positions
    stay trustworthy.

    Known limitation: string literals are not parsed, so a ``--`` inside a
    string would start a line comment here. None of the placeholder patterns
    depend on string contents, so this does not affect any verdict.
    """
    out: List[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        if depth == 0:
            if text.startswith("--", i):
                while i < n and text[i] != "\n":
                    out.append(" ")
                    i += 1
                continue
            if text.startswith("/-", i):
                depth += 1
                out.append("  ")
                i += 2
                continue
            out.append(text[i])
            i += 1
        else:
            if text.startswith("/-", i):
                depth += 1
                out.append("  ")
                i += 2
                continue
            if text.startswith("-/", i):
                depth -= 1
                out.append("  ")
                i += 2
                continue
            out.append("\n" if text[i] == "\n" else " ")
            i += 1
    return "".join(out)


def line_at(text: str, index: int) -> int:
    """1-based line number of ``index``."""
    return text.count("\n", 0, index) + 1


# Directories that never hold the project's own source: the Lean package cache
# (.lake), VCS metadata, and vendored/bytecode trees. Walking them reports the
# third-party dependencies' placeholders as if they were the project's own,
# which is exactly the false-positive class that makes a gate untrustworthy.
# An explicitly named file or directory is always scanned: the caller asked
# for it by name.
SKIP_DIRS = frozenset({".lake", ".git", ".hg", ".svn", "node_modules",
                       "__pycache__"})


def expand_paths(paths: Sequence[str],
                 exts: Optional[set]
                 ) -> Tuple[List[Path], List[Path], List[Path]]:
    """Split inputs into applicable files, nonexistent inputs, skipped dirs.

    Directories are walked recursively with SKIP_DIRS pruned, so the scan is
    reported rather than silently truncated. Existing files whose extension is
    not handled by the current gate are dropped silently: they are out of
    scope, not missing.
    """
    files: List[Path] = []
    missing: List[Path] = []
    skipped: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            found: List[Path] = []
            for root, dirnames, filenames in os.walk(p):
                dirnames.sort()
                filenames.sort()
                keep = []
                for name in dirnames:
                    if name in SKIP_DIRS:
                        skipped.append(Path(root) / name)
                    else:
                        keep.append(name)
                dirnames[:] = keep
                for name in filenames:
                    child = Path(root) / name
                    if exts is None or child.suffix.lower() in exts:
                        found.append(child)
            files.extend(found)
        elif p.is_file():
            if exts is None or p.suffix.lower() in exts:
                files.append(p)
        else:
            missing.append(p)
    return files, missing, skipped


# --------------------------------------------------------------------------
# gate 1 -- placeholder scan
# --------------------------------------------------------------------------

def gate_lean(paths: Sequence[str]
              ) -> Tuple[List[str], List[str], List[Path]]:
    failures: List[str] = []
    notrun: List[str] = []
    files, missing, skipped = expand_paths(paths, LEAN_EXTS)
    notrun.extend("MISSING INPUT %s" % p for p in missing)

    for f in files:
        raw = read_text(f)
        if raw is None:
            notrun.append("UNREADABLE %s" % f)
            continue
        scanned = strip_lean_comments(raw)
        for pattern, label in PLACEHOLDERS:
            for m in re.finditer(pattern, scanned, re.MULTILINE):
                failures.append("%s:%d: %s placeholder"
                                % (f, line_at(scanned, m.start()), label))

    if not files:
        notrun.append("NO_LEAN_FILES: no .lean input matched")
    return failures, notrun, skipped


# --------------------------------------------------------------------------
# gate 2 -- comment-only claims
# --------------------------------------------------------------------------

def find_run_log(path: Path) -> Optional[Path]:
    """Locate a sidecar run log sitting next to the claiming file."""
    stem = path.name
    for known in (".txt", ".md", ".smt2", ".lean"):
        if stem.lower().endswith(known):
            stem = stem[: -len(known)]
            break
    for ext in (".log", ".out", ".json"):
        for candidate in (path.with_name(stem + ext), path.with_suffix(ext)):
            if candidate.is_file():
                return candidate
    for candidate in sorted(path.parent.glob(stem + ".*")):
        if candidate.is_file() and candidate.suffix.lower() in (".log", ".out"):
            return candidate
    return None


def gate_claim(paths: Sequence[str]
               ) -> Tuple[List[str], List[str], List[Path]]:
    failures: List[str] = []
    notrun: List[str] = []
    files, missing, skipped = expand_paths(paths, CLAIM_EXTS)
    notrun.extend("MISSING INPUT %s" % p for p in missing)

    for f in files:
        raw = read_text(f)
        if raw is None:
            notrun.append("UNREADABLE %s" % f)
            continue
        if not VERDICT_CLAIM.search(raw):
            continue  # nothing is being claimed, so nothing to check

        if "(assert" in raw and "(check-sat)" not in raw:
            failures.append(
                "%s: COMMENT_ONLY_CLAIM -- states a solver verdict but "
                "contains no (check-sat)" % f)
            continue

        log = find_run_log(f)
        if log is None:
            failures.append(
                "%s: NO_RUN_LOG -- 'MACHINE RESULT' claim has no sidecar "
                "run log" % f)
            continue
        log_text = read_text(log)
        if log_text is None or not SOLVER_VERDICT_LINE.search(log_text):
            failures.append(
                "%s: NO_RUN_LOG -- sidecar %s carries no solver verdict line"
                % (f, log.name))

    if not files:
        notrun.append("NO_CLAIM_FILES: no claim-bearing input matched")
    return failures, notrun, skipped


# --------------------------------------------------------------------------
# gate 3 -- the circularity auditor
# --------------------------------------------------------------------------

def find_auditor(explicit: Optional[str]) -> Optional[Path]:
    """Locate the circularity auditor without scanning the whole disk."""
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None
    env = os.environ.get("ANTI_CIRCULARITY_AUDITOR")
    if env:
        p = Path(env)
        if p.is_file():
            return p
    bases = (Path.cwd(), Path.home())
    for base in bases:
        for rel in AUDITOR_KNOWN_PATHS:
            for candidate in ((base / rel).resolve(), (base / rel)):
                if candidate.is_file():
                    return candidate
    return None


def gate_audit(paths: Sequence[str],
               auditor: Optional[str] = None,
               python: Optional[str] = None,
               json_out: Optional[str] = None
               ) -> Tuple[List[str], List[str], str]:
    """Run the circularity auditor and classify its summary line."""
    failures: List[str] = []
    notrun: List[str] = []
    output = ""

    target = find_auditor(auditor)
    if target is None:
        notrun.append(
            "AUDITOR_NOT_FOUND: set --auditor or ANTI_CIRCULARITY_AUDITOR")
        return failures, notrun, output

    interpreter = python or os.environ.get("ANTI_CIRCULARITY_PYTHON") or sys.executable
    cmd = [interpreter, str(target)] + [str(p) for p in paths]
    if json_out:
        cmd += ["--json", str(json_out)]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError as exc:
        notrun.append("AUDITOR_NOT_RUN: %s" % exc)
        return failures, notrun, output

    output = (proc.stdout or "") + (proc.stderr or "")

    if proc.returncode != 0:
        notrun.append("AUDITOR_NOT_RUN: exit=%d" % proc.returncode)
        return failures, notrun, output

    match = SUMMARY_LINE.search(output)
    if not match:
        notrun.append("AUDITOR_NOT_RUN: no summary line in auditor output")
        return failures, notrun, output

    counts = {k: int(v) for k, v in SUMMARY_COUNT.findall(match.group(1))}

    for verdict in NON_RESULT_VERDICTS:
        n = counts.get(verdict, 0)
        if n:
            failures.append("AUDIT %s=%d -- reached, but not a result"
                            % (verdict, n))
    for verdict in NO_VERDICT_VERDICTS:
        n = counts.get(verdict, 0)
        if n:
            notrun.append("AUDIT %s=%d -- no verdict was reached" % (verdict, n))

    return failures, notrun, output


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def emit(subcommand: str, failures: Sequence[str], notrun: Sequence[str],
         output: str = "", skipped: Sequence[object] = ()) -> int:
    if output:
        print(output.rstrip("\n"))
    print("-" * 78)
    print("ANTI-CIRCULARITY GATE [%s]" % subcommand)
    for item in failures:
        print("  FAIL     %s" % item)
    for item in notrun:
        print("  NOT RUN  %s" % item)
    for item in skipped:
        print("  SKIP     %s (dependency/VCS dir, out of scope)" % item)
    print("  result: FAIL=%d  NOT_RUN=%d  SKIP=%d"
          % (len(failures), len(notrun), len(skipped)))

    if failures:
        print("  verdict: FAIL")
        return EXIT_FAIL
    if notrun:
        print("  verdict: TOOL NOT RUN")
        return EXIT_NOT_RUN
    print("  verdict: PASS")
    return EXIT_PASS


def run(command: str, args: argparse.Namespace) -> int:
    failures: List[str] = []
    notrun: List[str] = []
    skipped: List[object] = []
    output = ""

    if command in ("lean", "check"):
        f, n, s = gate_lean(args.paths)
        failures += f
        notrun += n
        skipped += s

    if command in ("claim", "check"):
        f, n, s = gate_claim(args.paths)
        failures += f
        notrun += n
        skipped += s

    if command in ("audit", "check"):
        if command == "audit":
            audit_paths = list(args.paths)
        else:
            # `check` audits SMT-LIB2 scripts only; documents are audited
            # explicitly through the `audit` subcommand.
            audit_paths = [str(p) for p in expand_paths(args.paths, AUDIT_EXTS)[0]]
        if audit_paths:
            f, n, output = gate_audit(audit_paths, auditor=args.auditor,
                                      python=args.python, json_out=args.json)
            failures += f
            notrun += n

    # `check` walks each directory once per sub-gate, so the same skipped dir
    # is reported twice; report it once.
    unique_skipped = sorted({str(p) for p in skipped})
    return emit(command, failures, notrun, output, unique_skipped)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="gate.py",
        description="Anti-circularity gates for formal-verification artifacts.")
    ap.add_argument("command", choices=("lean", "claim", "audit", "check"))
    ap.add_argument("paths", nargs="+",
                    help="files or directories to gate")
    ap.add_argument("--auditor", default=None,
                    help="path to smt_circularity_auditor.py")
    ap.add_argument("--python", default=None,
                    help="interpreter used to run the auditor; it must have "
                         "the z3 package installed")
    ap.add_argument("--json", default=None,
                    help="write the auditor JSON report to this path")
    args = ap.parse_args(argv)
    return run(args.command, args)


if __name__ == "__main__":
    raise SystemExit(main())
