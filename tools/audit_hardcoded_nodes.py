#!/usr/bin/env python3
"""
tools/audit_hardcoded_nodes.py

Corpus-wide anti-hardcode auditor (fail-closed).

Scope:
    1. Python solver/generator sources -- AST scan for constant returns.
    2. All *.lean certificates -- scan for seal patterns, placeholders, and
       absence of computational tactics.

Exit codes:
    0  clean pass
    1  at least one finding (fail-closed shutdown)
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "staging" / "user_disertasi" / "lean" / "certificates"

PY_TARGETS = [
    "mcp/t2n/core/user_disertasi_gatekeeper.py",
    "mcp/t2n/solvers/prime_hologram_solver.py",
    "mcp/t2n/solvers/prime_hologram_apex.py",
    "mcp/t2n/solvers/p_vs_np_sieve.py",
    "mcp/t2n/solvers/beal_lattice_solver.py",
    "mcp/t2n/solvers/yudeng_singularity_sieve.py",
    "mcp/t2n/rh_core/rh_krypton_solver.py",
    "tools/user_parameter_injector.py",
]

LEAN_FORBIDDEN = [
    (re.compile(r"\bsorry\b"), "placeholder: sorry"),
    (re.compile(r"\badmit\b"), "placeholder: admit"),
    (re.compile(r"(?m)^\s*axiom\b"), "axiom declaration"),
    (re.compile(r"def\s+\w+\s*:\s*Bool\s*:=\s*true"), "static Bool := true seal"),
    (re.compile(r"theorem\s+\w+\s*:\s*True\b"), "True-only theorem"),
    (re.compile(r"\bby\s+trivial\b"), "trivial tactic"),
]

LEAN_COMPUTE = re.compile(r"by\s+(decide|omega|rfl|refine)|:=\s*rfl")
LEAN_THEOREM = re.compile(r"(?m)^theorem\s+\w+")


class HardcodedReturnAuditor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.findings = []
        self.current_func = None

    def visit_FunctionDef(self, node):
        old = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = old

    def visit_Return(self, node):
        if isinstance(node.value, ast.Constant):
            self.findings.append(
                (self.filename, self.current_func, f"Constant return: {node.value.value!r}")
            )
        elif isinstance(node.value, (ast.Tuple, ast.List)):
            if all(isinstance(elt, ast.Constant) for elt in node.value.elts):
                vals = [elt.value for elt in node.value.elts]
                self.findings.append(
                    (self.filename, self.current_func, f"Static collection return: {vals}")
                )
        self.generic_visit(node)


def audit_python(path):
    findings = []
    if not path.exists():
        return findings
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        findings.append((str(path), "<module>", f"SyntaxError: {exc}"))
        return findings
    auditor = HardcodedReturnAuditor(str(path))
    auditor.visit(tree)
    return auditor.findings


def audit_lean(path):
    findings = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern, label in LEAN_FORBIDDEN:
        for match in pattern.finditer(text):
            line = text[: match.start()].count("\n") + 1
            findings.append((path.name, f"line {line}", label))
    if not LEAN_COMPUTE.search(text):
        findings.append((path.name, "<file>", "no decide/omega/rfl/refine tactic"))
    if len(LEAN_THEOREM.findall(text)) < 2:
        findings.append((path.name, "<file>", "fewer than two theorem declarations"))
    return findings


def main():
    print("[HARDENED AUDITOR] Python AST scan + Lean corpus scan")
    findings = []

    for rel in PY_TARGETS:
        findings.extend(audit_python(ROOT / rel))

    lean_files = sorted(LEAN_DIR.glob("*.lean"))
    for path in lean_files:
        findings.extend(audit_lean(path))

    print(f"[HARDENED AUDITOR] python targets: {len(PY_TARGETS)}")
    print(f"[HARDENED AUDITOR] lean certificates: {len(lean_files)}")

    if findings:
        print(f"[AUDIT ALERT] {len(findings)} finding(s):")
        for f in findings:
            print(f"  File: {f[0]} | Location: {f[1]} | Detail: {f[2]}")
        sys.exit(1)

    print("[AUDIT SUCCESS] No static seals, placeholders, or constant returns detected.")
    sys.exit(0)


if __name__ == "__main__":
    main()
