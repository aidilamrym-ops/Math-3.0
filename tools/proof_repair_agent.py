"""Math 3.0 — compiler-guided autonomous proof repair agent.

The agent is deterministic and auditable.  It does not call an LLM and it never
inserts ``sorry``, ``admit``, or ``axiom``.  Instead it:

  1. compiles the target Lean file;
  2. parses the compiler diagnostics;
  3. proposes a bounded set of syntactic repairs (remove unavailable Mathlib
     imports, replace a failing tactic with a core tactic from a portfolio);
  4. recompiles every candidate in a temporary sandbox;
  5. accepts the first candidate for which Lean exits 0 and the placeholder
     scan is clean.

Every attempt is recorded in a JSON receipt.  If no candidate verifies, the
original file is left untouched and the verdict is ``UNREPAIRED``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smt_lean_bridge import find_placeholders, lean_version  # noqa: E402

AGENT_NAME = "math30_proof_repair_agent"
AGENT_VERSION = "1.0.0"

CORE_PORTFOLIO = [
    "decide",
    "omega",
    "simp",
    "rfl",
    "trivial",
    "assumption",
    "contradiction",
    "constructor",
]
MATHLIB_PORTFOLIO = ["norm_num", "linarith", "ring", "positivity", "norm_cast"]

_ARITHMETIC_MARKERS = ("≤", "≥", "<", ">", "+", "-", "*", "Int", "Nat", "ℕ", "ℤ", "=")
_ERROR_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s*"
    r"(?P<severity>error|warning)(?:\((?P<code>[^)]+)\))?:\s*(?P<message>.*)$",
    re.MULTILINE,
)
_TACTIC_LINE_RE = re.compile(
    r"^\s*(?P<tactic>"
    r"decide|omega|simp|rfl|trivial|assumption|contradiction|constructor|"
    r"norm_num|linarith|ring|positivity|norm_cast|"
    r"exact\b.*|apply\b.*|intro\b.*|cases\b.*|induction\b.*"
    r")\s*$"
)
_UNKNOWN_TACTIC_PATTERNS = (
    r"unknown tactic '([^']+)'",
    r"unknown identifier '([^']+)'",
    r"tactic '([^']+)' failed",
)


@dataclass
class Diagnostic:
    line: int
    column: int
    message: str
    code: str | None = None


@dataclass
class CompileResult:
    path: str
    exit_code: int | None
    stdout: str
    stderr: str
    elapsed_ms: float
    status: str

    @property
    def ok(self) -> bool:
        return self.status == "COMPILED" and self.exit_code == 0


@dataclass
class Proposal:
    text: str
    description: str


@dataclass
class SearchState:
    text: str
    history: list[str] = field(default_factory=list)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _run_lean(
    path: str,
    *,
    root: str,
    backend: str,
    timeout: int,
) -> CompileResult:
    lean = shutil.which("lean")
    lake = shutil.which("lake")
    if backend == "lake":
        if not lake:
            return CompileResult(path, None, "", "lake executable not found", 0.0, "TOOL_NOT_RUN")
        command = [lake, "env", "lean", path]
    else:
        if not lean:
            return CompileResult(path, None, "", "lean executable not found", 0.0, "TOOL_NOT_RUN")
        command = [lean, path]

    environment = os.environ.copy()
    existing = environment.get("LEAN_PATH")
    environment["LEAN_PATH"] = root + (os.pathsep + existing if existing else "")
    started = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(
            path, None, "", f"compile timeout after {timeout}s",
            round((time.perf_counter() - started) * 1000, 3), "TIMEOUT",
        )
    except OSError as error:
        return CompileResult(
            path, None, "", f"{type(error).__name__}: {error}",
            round((time.perf_counter() - started) * 1000, 3), "TOOL_NOT_RUN",
        )
    return CompileResult(
        path=path,
        exit_code=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
        elapsed_ms=round((time.perf_counter() - started) * 1000, 3),
        status="COMPILED" if result.returncode == 0 else "COMPILE_ERROR",
    )


def parse_diagnostics(stderr: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for match in _ERROR_RE.finditer(stderr):
        if match.group("severity") != "error":
            continue
        diagnostics.append(
            Diagnostic(
                line=int(match.group("line")),
                column=int(match.group("col")),
                message=match.group("message").strip(),
                code=match.group("code"),
            )
        )
    if not diagnostics and stderr.strip():
        diagnostics.append(Diagnostic(0, 0, stderr.strip().splitlines()[0][:500]))
    return diagnostics


def _strip_mathlib_imports(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not line.strip().startswith("import Mathlib")
    ]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _tactic_lines(text: str) -> list[str]:
    tactics: list[str] = []
    for line in text.splitlines():
        match = _TACTIC_LINE_RE.match(line)
        if match:
            tactic = match.group("tactic").strip()
            if tactic not in tactics:
                tactics.append(tactic)
    return tactics


def _replace_tactic_line(text: str, old: str, new: str) -> tuple[str, bool]:
    lines = text.splitlines()
    changed = False
    old_head = old.split()[0]
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if stripped == old or (parts and parts[0] == old_head):
            indent = line[: len(line) - len(line.lstrip())]
            lines[index] = indent + new
            changed = True
    result = "\n".join(lines)
    if text.endswith("\n"):
        result += "\n"
    return result, changed


def _portfolio_for(diagnostics: list[Diagnostic], include_mathlib: bool) -> list[str]:
    messages = " ".join(diagnostic.message for diagnostic in diagnostics)
    portfolio = list(CORE_PORTFOLIO)
    if any(marker in messages for marker in _ARITHMETIC_MARKERS):
        portfolio = ["omega", "decide", "simp", "rfl", "trivial", "assumption", "contradiction", "constructor"]
    if include_mathlib:
        portfolio = MATHLIB_PORTFOLIO + portfolio
    return list(dict.fromkeys(portfolio))


def propose_repairs(
    text: str,
    diagnostics: list[Diagnostic],
    portfolio: list[str],
    max_proposals: int = 24,
) -> list[Proposal]:
    messages = "\n".join(diagnostic.message for diagnostic in diagnostics)
    proposals: list[Proposal] = []

    if "Mathlib" in messages or "unknown module prefix" in messages:
        stripped = _strip_mathlib_imports(text)
        if stripped != text:
            proposals.append(Proposal(stripped, "remove unavailable Mathlib imports"))

    unknown: set[str] = set()
    for diagnostic in diagnostics:
        for pattern in _UNKNOWN_TACTIC_PATTERNS:
            unknown.update(re.findall(pattern, diagnostic.message))

    tactics = _tactic_lines(text)
    targets: list[str] = []
    for tactic in tactics:
        head = tactic.split()[0]
        if head in unknown or tactic in unknown:
            targets.append(tactic)
    if not targets and ("unsolved goals" in messages or not proposals):
        targets = tactics

    for target in targets:
        for candidate in portfolio:
            if candidate.split()[0] == target.split()[0]:
                continue
            new_text, changed = _replace_tactic_line(text, target, candidate)
            if changed and new_text != text:
                proposals.append(
                    Proposal(new_text, f"replace tactic {target!r} with {candidate!r}")
                )

    # A theorem ending in `:= by` with no tactic: insert a core tactic.
    if not tactics and "unsolved goals" in messages:
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip().endswith(":= by"):
                for candidate in portfolio:
                    candidate_lines = lines[: index + 1] + [
                        line[: len(line) - len(line.lstrip())] + "  " + candidate
                    ] + lines[index + 1 :]
                    proposals.append(
                        Proposal("\n".join(candidate_lines) + "\n", f"insert tactic {candidate!r}")
                    )

    seen: set[str] = set()
    unique: list[Proposal] = []
    for proposal in proposals:
        digest = _sha256(proposal.text)
        if digest in seen:
            continue
        seen.add(digest)
        unique.append(proposal)
        if len(unique) >= max_proposals:
            break
    return unique


def _write_sandbox(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def repair(
    *,
    file_path: str,
    root: str,
    backend: str,
    timeout: int,
    max_attempts: int,
    max_depth: int,
    include_mathlib: bool,
) -> dict[str, Any]:
    if not os.path.isfile(file_path):
        raise SystemExit(f"file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as handle:
        original_text = handle.read()

    report: dict[str, Any] = {
        "agent": AGENT_NAME,
        "agent_version": AGENT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": file_path,
        "input_sha256": _sha256(original_text),
        "backend": backend,
        "lean": lean_version(),
        "status": "UNKNOWN",
        "attempts": [],
        "winning_attempt": None,
        "output": None,
        "placeholders": [],
        "limitations": (
            "Deterministic syntactic repair over a bounded tactic portfolio. "
            "It proves nothing by itself; only Lean exit code 0 and a clean "
            "placeholder scan are treated as success."
        ),
    }

    original_placeholders = find_placeholders(original_text)
    if original_placeholders:
        report["status"] = "REFUSED_PLACEHOLDER"
        report["placeholders"] = original_placeholders
        return report

    sandbox = tempfile.mkdtemp(prefix="math30_repair_")
    report["sandbox"] = sandbox

    baseline = _run_lean(file_path, root=root, backend=backend, timeout=timeout)
    baseline_output = "\n".join(part for part in (baseline.stdout, baseline.stderr) if part)
    report["baseline"] = {
        "exit_code": baseline.exit_code,
        "status": baseline.status,
        "elapsed_ms": baseline.elapsed_ms,
        "stdout": baseline.stdout,
        "stderr": baseline.stderr,
        "diagnostics": [diagnostic.__dict__ for diagnostic in parse_diagnostics(baseline_output)],
    }
    if baseline.ok:
        report["status"] = "ALREADY_VERIFIED"
        return report
    if baseline.status == "TOOL_NOT_RUN":
        report["status"] = "TOOL_NOT_RUN"
        return report

    queue: deque[SearchState] = deque([SearchState(original_text)])
    seen = {_sha256(original_text)}
    attempt_number = 0

    while queue and attempt_number < max_attempts:
        state = queue.popleft()
        if len(state.history) > max_depth:
            continue
        attempt_number += 1

        sandbox_path = os.path.join(
            sandbox, f"attempt_{attempt_number:03d}_{_sha256(state.text)[:8]}.lean"
        )
        _write_sandbox(sandbox_path, state.text)
        placeholders = find_placeholders(state.text)
        if placeholders:
            report["attempts"].append(
                {
                    "attempt": attempt_number,
                    "history": state.history,
                    "text_sha256": _sha256(state.text),
                    "status": "REJECTED_PLACEHOLDER",
                    "placeholders": placeholders,
                }
            )
            continue

        compilation = _run_lean(sandbox_path, root=root, backend=backend, timeout=timeout)
        compile_output = "\n".join(
            part for part in (compilation.stdout, compilation.stderr) if part
        )
        diagnostics = parse_diagnostics(compile_output)
        attempt_record = {
            "attempt": attempt_number,
            "history": state.history,
            "text_sha256": _sha256(state.text),
            "exit_code": compilation.exit_code,
            "status": compilation.status,
            "elapsed_ms": compilation.elapsed_ms,
            "diagnostics": [diagnostic.__dict__ for diagnostic in diagnostics],
            "stdout": compilation.stdout,
            "stderr": compilation.stderr,
        }
        report["attempts"].append(attempt_record)

        if compilation.ok:
            report["status"] = "REPAIRED"
            report["winning_attempt"] = attempt_number
            report["output_text"] = state.text
            report["output_sha256"] = _sha256(state.text)
            report["output_history"] = state.history
            report["output_diagnostics"] = attempt_record["diagnostics"]
            return report

        if compilation.status == "TOOL_NOT_RUN":
            report["status"] = "TOOL_NOT_RUN"
            return report

        portfolio = _portfolio_for(diagnostics, include_mathlib)
        for proposal in propose_repairs(state.text, diagnostics, portfolio):
            digest = _sha256(proposal.text)
            if digest in seen:
                continue
            seen.add(digest)
            queue.append(SearchState(proposal.text, state.history + [proposal.description]))

    report["status"] = "UNREPAIRED"
    report["attempts_exhausted"] = attempt_number
    return report


def _write_output(
    report: dict[str, Any],
    *,
    file_path: str,
    out_path: str | None,
    in_place: bool,
    root: str,
) -> str | None:
    if report["status"] != "REPAIRED":
        return None
    output_text = report.pop("output_text")
    destination = file_path if in_place else (out_path or os.path.join(
        root, "lean", "repaired", os.path.basename(file_path)
    ))
    if in_place:
        backup = os.path.join(report["sandbox"], "original.lean")
        shutil.copyfile(file_path, backup)
        report["original_backup"] = backup
    os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
    with open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(output_text)
    report["output"] = destination
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Math 3.0 compiler-guided proof repair agent")
    parser.add_argument("--file", required=True, help="Lean file to repair")
    parser.add_argument("--out", default=None, help="Repaired output path (default: lean/repaired/<name>)")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input after success")
    parser.add_argument("--max-attempts", type=int, default=16)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--backend", choices=("lean", "lake"), default="lean")
    parser.add_argument("--mathlib", action="store_true", help="Include Mathlib tactics in the portfolio")
    parser.add_argument("--json", default=None, help="JSON receipt path")
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report = repair(
        file_path=os.path.abspath(args.file),
        root=root,
        backend=args.backend,
        timeout=args.timeout,
        max_attempts=args.max_attempts,
        max_depth=args.max_depth,
        include_mathlib=args.mathlib,
    )

    destination = _write_output(
        report,
        file_path=os.path.abspath(args.file),
        out_path=args.out,
        in_place=args.in_place,
        root=root,
    )

    # Independent confirmation of the written artifact.
    if destination:
        confirmation = _run_lean(destination, root=root, backend=args.backend, timeout=args.timeout)
        report["confirmation"] = {
            "path": destination,
            "exit_code": confirmation.exit_code,
            "status": confirmation.status,
            "elapsed_ms": confirmation.elapsed_ms,
            "stderr": confirmation.stderr,
            "placeholders": find_placeholders(open(destination, encoding="utf-8").read()),
        }
        if not confirmation.ok or report["confirmation"]["placeholders"]:
            report["status"] = "OUTPUT_CONFIRMATION_FAILED"

    stem = os.path.splitext(os.path.basename(args.file))[0]
    receipt_path = args.json or os.path.join(root, "reports", f"proof_repair_{stem}.json")
    os.makedirs(os.path.dirname(os.path.abspath(receipt_path)), exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
    report["receipt"] = receipt_path

    print(f"=== MATH 3.0 PROOF REPAIR AGENT v{AGENT_VERSION} ===")
    print(f"input:  {args.file}")
    print(f"status: {report['status']}")
    print(f"attempts: {len(report['attempts'])}")
    if report.get("winning_attempt"):
        print(f"winning attempt: {report['winning_attempt']}")
        print(f"history: {report.get('output_history')}")
    if report.get("output"):
        print(f"output: {report['output']}")
    if report.get("confirmation"):
        print(f"confirmation: {report['confirmation']['status']}")
    print(f"receipt: {receipt_path}")

    if report["status"] in ("REPAIRED", "ALREADY_VERIFIED"):
        return 0
    if report["status"] == "TOOL_NOT_RUN":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
