#!/usr/bin/env python3
"""Math 3.0 blind-spot auditor (fail-closed).

This tool audits the *audit surface* as well as the proof surface.  It is
deliberately suspicious: a green Lean compiler run is not enough if the
surrounding harness can silently swallow a failure, hard-code a verdict, or
only inspect a fraction of the corpus.

Scope
-----
Lean:
    every ``*.lean`` file under ``lean/``, ``Math30Kernel/``,
    ``Math30Interfaces/`` and (when present) the user certificate staging
    directory.  Checks for vacuous statements, trust extensions, placeholder
    tokens, and duplicate declarations.

Python:
    audit/verification scripts under ``tools/``, ``mcp/``, ``Math30Solvers/``
    and ``Math30Interfaces/``.  Checks for swallowed exceptions, discarded
    subprocess results, hard-coded PASS verdicts/timestamps, absolute paths,
    and constant-return verifier functions.

Repository:
    Makefile target references, script-style tests that pytest cannot collect,
    and Lean files that the surface audit would miss.

Exit codes
----------
0  no findings (warnings may still be present)
1  at least one finding
2  the auditor could not run (missing interpreter/path)
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
sys.path.insert(0, str(ROOT / "tools"))

from smt_lean_bridge import find_placeholders  # noqa: E402

LEAN_ROOTS = [
    ROOT / "lean",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
    ROOT / "staging" / "user_disertasi" / "lean",
]
PYTHON_ROOTS = [
    ROOT / "tools",
    ROOT / "mcp",
    ROOT / "Math30Solvers",
    ROOT / "Math30Interfaces",
]
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".lake",
    "fixtures",
    "repaired",
    "openai_math",
    "node_modules",
}
AUDIT_NAME = "math30_blindspot_audit"
AUDIT_VERSION = "1.0.0"

TRUST_TOKENS = {
    "native_decide": re.compile(r"\bnative_decide\b"),
    "axiom_decl": re.compile(r"(?m)^\s*axiom\b"),
    "constant_decl": re.compile(r"(?m)^\s*constant\b"),
    "opaque_decl": re.compile(r"(?m)^\s*opaque\b"),
    "unsafe_decl": re.compile(r"(?m)^\s*unsafe\b"),
    "implemented_by": re.compile(r"@\[\s*implemented_by\b"),
    "extern_attr": re.compile(r"@\[\s*extern\b"),
    "partial_decl": re.compile(r"(?m)^\s*partial\s+def\b"),
}

TRUE_THEOREM = re.compile(
    r"(?m)^\s*(?:theorem|lemma)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
    r"(?P<sig>[^\n]*?):\s*True\s*:="
)
REFLEXIVE_THEOREM = re.compile(
    r"(?m)^\s*(?:theorem|lemma)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
    r"[^\n]*?:\s*(?P<lhs>[A-Za-z_][A-Za-z0-9_'.]*)\s*=\s*(?P=lhs)\s*:="
)
DECL_RE = re.compile(
    r"(?m)^\s*(?:theorem|lemma|def|abbrev|structure|inductive|class)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
ISO_TIMESTAMP = re.compile(r"\b20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
ABS_WIN_PATH = re.compile(r"""(?<![A-Za-z0-9_])[rRbB]?["']([A-Za-z]:\\\\|[A-Za-z]:\\)""")
HARD_PASS = re.compile(
    r"""(?i)["'](?:overall_verdict|verdict|status)["']\s*:\s*["'](?:PASSED|PASS|SUCCESS|FULL PASS)["']"""
)


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    message: str
    severity: str = "FAIL"

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class AuditState:
    findings: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def fail(self, path: Path | str, line: int, rule: str, message: str) -> None:
        rel = str(path).replace("\\", "/")
        self.findings.append(Finding(rel, line, rule, message))

    def warn(self, path: Path | str, line: int, rule: str, message: str) -> None:
        rel = str(path).replace("\\", "/")
        self.warnings.append(Finding(rel, line, rule, message, "WARN"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def discover_lean() -> list[Path]:
    files: list[Path] = []
    for root in LEAN_ROOTS:
        if not root.is_dir():
            continue
        for current, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in EXCLUDED_DIRS and not name.startswith(".")
            ]
            for filename in filenames:
                if filename.endswith(".lean"):
                    files.append(Path(current) / filename)
    return sorted(set(files))


def discover_python() -> list[Path]:
    files: list[Path] = []
    for root in PYTHON_ROOTS:
        if not root.is_dir():
            continue
        for current, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in EXCLUDED_DIRS and not name.startswith(".")
            ]
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(Path(current) / filename)
    return sorted(set(files))


def strip_lean_comments(text: str) -> str:
    """Remove Lean comments and string literals while preserving line count."""
    out: list[str] = []
    index = 0
    depth = 0
    in_string = False
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if depth:
            if char == "/" and nxt == "-":
                depth += 1
                out.extend("\n" if c == "\n" else " " for c in "/-")
                index += 2
                continue
            if char == "-" and nxt == "/":
                depth -= 1
                out.extend("\n" if c == "\n" else " " for c in "-/")
                index += 2
                continue
            out.append("\n" if char == "\n" else " ")
            index += 1
            continue
        if in_string:
            if char == "\\" and nxt:
                out.extend([" ", "\n" if nxt == "\n" else " "])
                index += 2
                continue
            if char == '"':
                in_string = False
                out.append(" ")
                index += 1
                continue
            out.append("\n" if char == "\n" else " ")
            index += 1
            continue
        if char == "/" and nxt == "-":
            depth = 1
            out.extend("  ")
            index += 2
            continue
        if char == "-" and nxt == "-":
            while index < len(text) and text[index] != "\n":
                out.append(" ")
                index += 1
            continue
        if char == '"':
            in_string = True
            out.append(" ")
            index += 1
            continue
        out.append(char)
        index += 1
    return "".join(out)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def audit_lean_file(path: Path, state: AuditState) -> tuple[int, int]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_lean_comments(raw)

    for label, pattern in TRUST_TOKENS.items():
        for match in pattern.finditer(clean):
            state.fail(
                path,
                line_of(clean, match.start()),
                "lean-trust",
                f"trust extension / escape hatch detected: {label}",
            )

    for match in TRUE_THEOREM.finditer(clean):
        state.fail(
            path,
            line_of(clean, match.start()),
            "lean-vacuous",
            f"theorem `{match.group('name')}` has statement `True` (vacuous)",
        )

    for match in REFLEXIVE_THEOREM.finditer(clean):
        state.fail(
            path,
            line_of(clean, match.start()),
            "lean-vacuous",
            f"theorem `{match.group('name')}` proves reflexive equality `{match.group('lhs')} = {match.group('lhs')}`",
        )

    placeholders = find_placeholders(raw)
    for placeholder in placeholders:
        state.fail(
            path,
            0,
            "lean-placeholder",
            f"placeholder token: {placeholder}",
        )

    declarations = len(DECL_RE.findall(clean))
    theorems = len(re.findall(r"(?m)^\s*(?:theorem|lemma)\s+", clean))
    return declarations, theorems


def lean_qualified_theorems(clean: str) -> list[str]:
    """Resolve theorem/lemma names against their enclosing namespaces.

    `section` scopes never contribute to a declaration's name, so they are
    tracked separately from `namespace` scopes.
    """
    scopes: list[tuple[str, str]] = []
    names: list[str] = []
    for raw_line in clean.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        namespace = re.match(r"namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)", line)
        if namespace:
            scopes.append(("ns", namespace.group(1)))
            continue
        section = re.match(
            r"section(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$", line
        )
        if section:
            scopes.append(("sec", section.group(1) or ""))
            continue
        end = re.match(r"end(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$", line)
        if end:
            target = end.group(1)
            if target is None:
                if scopes:
                    scopes.pop()
            else:
                for index in range(len(scopes) - 1, -1, -1):
                    _kind, name = scopes[index]
                    if name == target or target.startswith(name + "."):
                        del scopes[index:]
                        break
            continue
        declaration = re.match(
            r"(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)", line
        )
        if declaration:
            name = declaration.group(1)
            prefix = ".".join(
                scope_name for kind, scope_name in scopes if kind == "ns" and scope_name
            )
            if prefix and not name.startswith(prefix + "."):
                names.append(prefix + "." + name)
            else:
                names.append(name)
    return names


def audit_duplicate_lean(lean_files: list[Path], state: AuditState) -> None:
    seen: dict[str, list[str]] = {}
    for path in lean_files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        clean = strip_lean_comments(raw)
        for name in lean_qualified_theorems(clean):
            seen.setdefault(name, []).append(rel(path))
    for name, paths in sorted(seen.items()):
        unique = sorted(set(paths))
        if len(unique) > 1:
            state.warn(
                unique[0],
                0,
                "lean-duplicate",
                f"theorem/lemma name `{name}` appears in {len(unique)} files: {', '.join(unique[:5])}",
            )


class AuditTheaterVisitor(ast.NodeVisitor):
    """Detect common ways an audit script can fake a green result."""

    def __init__(self, path: Path, source: str, state: AuditState, critical: bool) -> None:
        self.path = path
        self.source = source
        self.state = state
        self.critical = critical

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if not self._is_broad(handler):
                continue
            if self._handler_swallows(handler):
                _record(
                    self.state,
                    self.critical,
                    self.path,
                    handler.lineno,
                    "audit-swallow",
                    "broad exception handler does not re-raise or fail closed",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_broad(handler: ast.ExceptHandler) -> bool:
        if handler.type is None:
            return True
        if isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"}:
            return True
        return False

    @staticmethod
    def _target_name(target: ast.AST) -> str | None:
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Attribute):
            return target.attr
        if isinstance(target, ast.Subscript):
            slice_node = target.slice
            if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                return slice_node.value
        return None

    @staticmethod
    def _failure_value(node: ast.AST | None) -> bool:
        if isinstance(node, ast.Constant):
            value = node.value
            if value is False:
                return True
            if isinstance(value, str) and value.upper() in {
                "FAIL", "FAILED", "FAILED_CONTAINED", "ERROR", "TIMEOUT",
                "TOOL_NOT_RUN", "INVALID", "UNKNOWN",
            }:
                return True
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    key_lower = key.value.lower()
                    if key_lower in {
                        "status", "verdict", "result", "outcome",
                        "compiled", "passed", "verified", "success", "ok",
                    } and AuditTheaterVisitor._failure_value(value):
                        return True
        return False

    @staticmethod
    def _handler_swallows(handler: ast.ExceptHandler) -> bool:
        for stmt in handler.body:
            if isinstance(stmt, ast.Raise):
                return False
            for node in ast.walk(stmt):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr in {"exit", "fail", "abort"}:
                        return False
                    if isinstance(func, ast.Name) and func.id in {"exit", "fail", "abort"}:
                        return False
                    if isinstance(func, ast.Attribute) and func.attr in {"append", "add", "write"}:
                        if any(AuditTheaterVisitor._failure_value(arg) for arg in node.args):
                            return False
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        name = AuditTheaterVisitor._target_name(target)
                        if not name:
                            continue
                        name_lower = name.lower()
                        value = node.value
                        if any(word in name_lower for word in ("fail", "error", "alarm", "abort", "invalid")):
                            if isinstance(value, ast.Constant) and (
                                value.value is True
                                or (isinstance(value.value, str) and AuditTheaterVisitor._failure_value(value))
                            ):
                                return False
                        if any(
                            word in name_lower
                            for word in ("ok", "pass", "valid", "verified", "success", "compiled", "clean")
                        ):
                            if AuditTheaterVisitor._failure_value(value):
                                return False
                        if any(word in name_lower for word in ("status", "verdict", "result", "outcome")):
                            if AuditTheaterVisitor._failure_value(value):
                                return False
                if isinstance(node, ast.Return) and AuditTheaterVisitor._failure_value(node.value):
                    return False
                if isinstance(node, ast.Dict) and AuditTheaterVisitor._failure_value(node):
                    return False
        return True

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_subprocess_run(node):
            if isinstance(node.parent, ast.Expr):  # type: ignore[attr-defined]
                _record(
                    self.state,
                    self.critical,
                    self.path,
                    node.lineno,
                    "audit-discard",
                    "subprocess.run result is discarded; return code is not checked",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_subprocess_run(node: ast.Call) -> bool:
        if isinstance(node.func, ast.Attribute):
            return (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr == "run"
            )
        return False


def _attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent  # type: ignore[attr-defined]


AUDIT_ROLE = re.compile(
    r"(audit|verify|suite|check|validator|gate|hunter|keeper|tribunal|regression|reporter)",
    re.IGNORECASE,
)


def _is_audit_critical(path: Path) -> bool:
    return bool(AUDIT_ROLE.search(path.stem))


def _record(state: AuditState, critical: bool, path: Path, line: int, rule: str, message: str) -> None:
    if critical:
        state.fail(path, line, rule, message)
    else:
        state.warn(path, line, rule, message)


def audit_python_file(path: Path, state: AuditState) -> dict[str, int]:
    source = path.read_text(encoding="utf-8", errors="replace")
    critical = _is_audit_critical(path)
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        state.fail(path, exc.lineno or 0, "python-syntax", f"SyntaxError: {exc.msg}")
        return {"functions": 0, "constant_returns": 0}

    _attach_parents(tree)
    AuditTheaterVisitor(path, source, state, critical).visit(tree)

    for match in ISO_TIMESTAMP.finditer(source):
        _record(
            state,
            critical,
            path,
            line_of(source, match.start()),
            "audit-stale-timestamp",
            f"hard-coded timestamp `{match.group(0)}` (use runtime UTC time)",
        )

    for match in ABS_WIN_PATH.finditer(source):
        _record(
            state,
            False,
            path,
            line_of(source, match.start()),
            "audit-portability",
            "absolute Windows path makes the audit non-portable",
        )

    constant_returns = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not re.search(r"(verify|audit|check|validate|gate|probe)", node.name):
            continue
        returns = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
        constant_values = [
            child.value.value
            for child in returns
            if isinstance(child.value, ast.Constant)
        ]
        if returns and len(constant_values) == len(returns) and set(constant_values) == {True}:
            constant_returns += 1
            state.fail(
                path,
                node.lineno,
                "audit-constant-return",
                f"`{node.name}` only ever returns constant True",
            )

    for match in HARD_PASS.finditer(source):
        _record(
            state,
            False,
            path,
            line_of(source, match.start()),
            "audit-hardcoded-verdict",
            "hard-coded PASS/SUCCESS verdict literal found",
        )

    functions = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree)
    )
    return {"functions": functions, "constant_returns": constant_returns}


def audit_test_surface(state: AuditState) -> None:
    for path in sorted((ROOT / "Math30Solvers").glob("test_*.py")):
        source = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"(?m)^\s*def\s+test_", source):
            state.warn(
                path,
                0,
                "test-not-collected",
                "script-style test has no `def test_*`; pytest will not collect it",
            )


def audit_makefile(state: AuditState) -> None:
    path = ROOT / "Makefile.txt"
    if not path.is_file():
        state.fail(path, 0, "makefile-missing", "Makefile.txt is missing")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if "python3" in text:
        state.warn(
            path,
            0,
            "makefile-python3",
            "Makefile hard-codes `python3`; this workspace uses the configured `python`",
        )
    for match in re.finditer(r"(?m)^\s*(?:python3|python)\s+([^\s#]+\.py)", text):
        target = match.group(1).replace("\\", "/")
        candidates = [ROOT / target, ROOT / "tools" / target]
        if not any(candidate.is_file() for candidate in candidates):
            state.fail(
                path,
                line_of(text, match.start()),
                "makefile-missing-target",
                f"Makefile references missing script `{target}`",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Math 3.0 blind-spot audit")
    parser.add_argument("--json", default=str(REPORTS / "blindspot_audit.json"))
    parser.add_argument("--fail-on-warnings", action="store_true")
    args = parser.parse_args()

    if not ROOT.is_dir():
        print(f"FATAL: workspace root not found: {ROOT}", file=sys.stderr)
        return 2

    state = AuditState()
    lean_files = discover_lean()
    python_files = discover_python()

    if not lean_files:
        state.fail(ROOT, 0, "surface-empty", "no Lean files discovered")
    if not python_files:
        state.fail(ROOT, 0, "surface-empty", "no Python files discovered")

    declarations = 0
    theorems = 0
    for path in lean_files:
        d, t = audit_lean_file(path, state)
        declarations += d
        theorems += t

    audit_duplicate_lean(lean_files, state)
    constant_returns = 0
    functions = 0
    for path in python_files:
        stats = audit_python_file(path, state)
        functions += stats["functions"]
        constant_returns += stats["constant_returns"]

    audit_test_surface(state)
    audit_makefile(state)

    state.stats = {
        "lean_files": len(lean_files),
        "lean_declarations": declarations,
        "lean_theorems": theorems,
        "python_files": len(python_files),
        "python_functions": functions,
        "python_constant_returns": constant_returns,
        "finding_count": len(state.findings),
        "warning_count": len(state.warnings),
    }

    verdict = "FAILED" if state.findings else ("PASSED_WITH_WARNINGS" if state.warnings else "PASSED")
    if args.fail_on_warnings and state.warnings:
        verdict = "FAILED"

    report = {
        "audit": AUDIT_NAME,
        "audit_version": AUDIT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "stats": state.stats,
        "findings": [finding.as_dict() for finding in state.findings],
        "warnings": [warning.as_dict() for warning in state.warnings],
        "verdict": verdict,
    }

    output = Path(args.json)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("=== MATH 3.0 BLIND-SPOT AUDIT ===")
    print(
        f"lean: {state.stats['lean_files']} files / {declarations} declarations / {theorems} theorems"
    )
    print(f"python: {len(python_files)} files / {functions} functions")
    print(f"findings: {len(state.findings)}  warnings: {len(state.warnings)}")
    for finding in state.findings[:30]:
        print(f"  FAIL [{finding.rule}] {finding.path}:{finding.line} {finding.message}")
    if len(state.findings) > 30:
        print(f"  ... {len(state.findings) - 30} more findings")
    for warning in state.warnings[:10]:
        print(f"  WARN [{warning.rule}] {warning.path}:{warning.line} {warning.message}")
    print(f"VERDICT: {verdict}")
    print(f"receipt: {output}")

    if state.findings:
        return 1
    if args.fail_on_warnings and state.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
