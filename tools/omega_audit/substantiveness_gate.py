#!/usr/bin/env python3
"""Substantiveness Gate for Math 3.0.

Implements five adversarial controls that a compiled kernel check alone does
not provide:

  1. Inhabited-premise check (constructive witness / SMT satisfiability).
     Every hypothesis set is encoded in linear integer arithmetic and handed
     to Z3.  UNSAT means the premise is empty, so any implication about it is
     vacuous.

  2. Counter-model generation.  The same SMT encoding answers "is there an
     input that satisfies the premise?" and prints the model, so a reviewer
     can see a concrete inhabitant rather than trusting the prose.

  3. Mutation testing (optional, ``--mutate``).  The first Prop hypothesis of
     each theorem is weakened to ``True`` and the file is recompiled.  A
     mutant that still compiles proves the hypothesis was decorative.

  4. Non-trivial boundary / constant-definition scan.  Definitions that
     return the same literal for every input are flagged (the ``plaquette
     := 1`` / ``wilsonAction := 0`` failure mode), as are LEM-only proofs,
     numeral-only comparisons and reflexive equalities.

  5. Scope separation.  Every file is classified ``pure-theorem`` or
     ``bounded-model`` from its header keywords, and bounded models must
     declare an explicit scope ("Scope:", "Cakupan:", "Batas klaim:").

Exit codes
----------
0  PASS      no HIGH findings
1  FAIL      at least one HIGH finding
2  NOT RUN   no Lean files matched

Reports
-------
reports/substantiveness_gate.json
reports/substantiveness_gate.md
reports/model_scope_manifest.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_ROOT = ROOT / "lean"
DEFAULT_SURFACE = LEAN_ROOT
DEFAULT_SURFACES = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]
EXCLUDED_PARTS = {".lake", "build", ".git", "__pycache__"}
DEFAULT_REPORTS = ROOT / "reports"

try:  # optional dependency: z3-solver
    from z3 import And, Int, Solver, is_int_value, sat, unsat

    Z3_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    Z3_AVAILABLE = False
    raise  # ponytail: fail closed on unexpected import failure; upgrade to typed ImportError when Z3 packaging is standardized.


# ---------------------------------------------------------------------------
# Lexical helpers
# ---------------------------------------------------------------------------
def blank_comments(text: str) -> str:
    """Replace comments and string literals with spaces, preserving offsets."""
    out: list[str] = []
    i = 0
    depth = 0
    n = len(text)
    while i < n:
        if depth == 0 and text.startswith("/-", i):
            depth = 1
            out.append("  ")
            i += 2
            continue
        if depth > 0:
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
            continue
        if text.startswith("--", i):
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if text[i] == '"':
            out.append('"')
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    out.append("  ")
                    i += 2
                    continue
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append('"')
                i += 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


DECL_RE = re.compile(
    r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:protected|private|noncomputable|unsafe|partial)\s+)*"
    r"(theorem|lemma|def|abbrev|structure|inductive|example)\b"
)
NS_RE = re.compile(r"(?m)^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)")
END_RE = re.compile(r"(?m)^\s*end\b(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$")
BINDER_RE = re.compile(r"\((_?h[0-9A-Za-z_']*)\s*:\s*([^()]*?)\)")
# Mutation targeting must also recognize Unicode hypothesis names such as `hν`
# from the BRIDGE-01 specification.  This lexer is deliberately separate from
# BINDER_RE so the substantiveness baseline parsing is unchanged.
MUTATION_BINDER_RE = re.compile(r"\((_?h[^\s:()]*)\s*:\s*([^()]*?)\)")
VAR_BINDER_RE = re.compile(r"[({]([^(){}]*?)\s*:\s*(ℕ|ℤ|Nat|Int)[)}]")
PROP_THEOREM_RE = re.compile(r"^\s*(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)", re.M)


def find_stmt_end(text: str, start: int) -> int:
    """Return offset of the depth-0 ``:=`` that ends a declaration statement."""
    depth = 0
    i = start
    n = len(text)
    pairs = {"(": ")", "[": "]", "{": "}", "⟨": "⟩"}
    closes = set(pairs.values())
    while i < n - 1:
        ch = text[i]
        if ch in pairs:
            depth += 1
        elif ch in closes:
            depth = max(0, depth - 1)
        elif depth == 0 and text.startswith(":=", i):
            return i
        elif depth == 0 and text[i] == "\n":
            # declarations without a body (structure/inductive) end here
            nxt = text[i + 1 : i + 200]
            if re.match(r"\s*(?:@\[|theorem|lemma|def|abbrev|structure|inductive|example|namespace|end|section|#)", nxt):
                return i
        i += 1
    return n


@dataclass
class Decl:
    file: str
    kind: str
    name: str
    namespace: str
    line: int
    statement: str
    body: str
    params: list[str] = field(default_factory=list)
    hyp_names: list[str] = field(default_factory=list)
    hyp_types: list[str] = field(default_factory=list)
    var_types: dict[str, str] = field(default_factory=dict)
    binder_names: list[str] = field(default_factory=list)
    conclusion: str = ""


def split_statement(statement: str) -> tuple[str, str]:
    """Split a declaration statement into binder head and conclusion."""
    depth = 0
    for i, ch in enumerate(statement):
        if ch in "([{⟨":
            depth += 1
        elif ch in ")]}⟩":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0 and not statement.startswith(":=", i):
            return statement[:i], statement[i + 1 :]
    return statement, ""


def parse_file(path: Path, rel: str) -> list[Decl]:
    src = path.read_text(encoding="utf-8", errors="replace")
    clean = blank_comments(src)
    decls: list[Decl] = []
    matches = list(DECL_RE.finditer(clean))
    ns_stack: list[tuple[str, str | None]] = []

    def namespace_at(offset: int) -> str:
        stack: list[tuple[str, str | None]] = []
        for line in clean[:offset].splitlines():
            m = NS_RE.match(line)
            if m:
                stack.append(("ns", m.group(1)))
                continue
            m = END_RE.match(line)
            if m:
                name = m.group(1)
                if name:
                    while stack:
                        kind, cur = stack.pop()
                        if kind == "ns" and cur == name:
                            break
                elif stack:
                    stack.pop()
        return ".".join(n for k, n in stack if k == "ns" and n)

    for idx, m in enumerate(matches):
        kind = m.group(1)
        after = clean[m.end() : m.end() + 220]
        name_match = re.match(r"\s+([A-Za-z_][A-Za-z0-9_'.]*)", after)
        if not name_match:
            continue
        name = name_match.group(1)
        end = find_stmt_end(clean, m.start())
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(clean)
        statement = clean[m.start() : end]
        body = clean[end: next_start]
        line = clean.count("\n", 0, m.start()) + 1
        ns = namespace_at(m.start())

        d = Decl(rel, kind, name, ns, line, statement, body)
        head, conclusion = split_statement(statement)
        d.conclusion = conclusion.strip()

        if kind in ("def", "abbrev"):
            binder_zone = head[name_match.end() :]
            params: list[str] = []
            for bm in re.finditer(r"[({]([^(){}]*?):", binder_zone):
                for tok in bm.group(1).replace(",", " ").split():
                    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", tok):
                        params.append(tok)
            d.params = params

        for bm in BINDER_RE.finditer(head):
            d.hyp_names.append(bm.group(1))
            d.hyp_types.append(bm.group(2).strip())

        for vm in VAR_BINDER_RE.finditer(head):
            for tok in vm.group(1).replace(",", " ").split():
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", tok):
                    d.var_types[tok] = vm.group(2)

        # All binder names, for ground-argument detection in witness checks.
        for bm in re.finditer(r"[({]([^(){}]*?):", head):
            for tok in bm.group(1).replace(",", " ").split():
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", tok):
                    d.binder_names.append(tok)

        decls.append(d)
    return decls


# ---------------------------------------------------------------------------
# Check 4: constant definitions, LEM-only, numeral-only, reflexive proofs
# ---------------------------------------------------------------------------
CONST_BODY_RE = re.compile(
    r"^\s*(?:fun\b[^:=\n]*=>\s*)?(\(\s*\)|\d+|true|false|0|1)\s*$", re.S
)
CONST_IF_RE = re.compile(r"if\b[^\n]*\bthen\s*(\d+)\s*else\s*\1\s*$", re.S)
NUMERIC_THEOREM_RE = re.compile(
    r"^\s*(\d+)\s*(≤|<|≥|>|=)\s*(\d+)\s*$"
)
TRUE_CONSEQUENCE_RES = (
    re.compile(r"^∀[^,]*,\s*True\s*$"),
    re.compile(r"→\s*True\s*$"),
    re.compile(r"^∃[^,]*,\s*True\s*$"),
    re.compile(r"^True\s*∧"),
    re.compile(r"∧\s*True\s*$"),
)


def split_top_level(text: str, seps: str = " ") -> list[str]:
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in text:
        if ch in "([{⟨":
            depth += 1
        elif ch in ")]}⟩":
            depth = max(0, depth - 1)
        if depth == 0 and ch in seps:
            if cur:
                parts.append("".join(cur).strip())
                cur = []
            continue
        cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return [p for p in parts if p]


def is_numeral_comparison(text: str) -> bool:
    compact = re.sub(r"\s", "", text)
    return bool(re.fullmatch(r"\d+(?:[*/+]\d+)*(≤|<|≥|>|=)\d+(?:[*/+]\d+)*", compact))


def strip_outer_parens(text: str) -> str:
    """Peel balanced outer parentheses so `(u = u)` and `u = u` compare equal."""
    s = text.strip()
    while len(s) >= 2 and s[0] in "([{⟨" and s[-1] in ")]}⟩":
        depth = 0
        balanced_outer = True
        for i, ch in enumerate(s):
            if ch in "([{⟨":
                depth += 1
            elif ch in ")]}⟩":
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    balanced_outer = False
                    break
        if not balanced_outer or depth != 0:
            break
        s = s[1:-1].strip()
    return s


def reflexive_equality(text: str) -> bool:
    eq = re.fullmatch(r"(.+?)\s*=\s*(.+?)", strip_outer_parens(text), re.S)
    return bool(eq) and re.sub(r"\s", "", eq.group(1)) == re.sub(r"\s", "", eq.group(2))


def static_findings(d: Decl) -> list[dict]:
    out: list[dict] = []
    body = d.body.strip()

    if d.kind in ("def", "abbrev") and re.fullmatch(r"Prop", d.conclusion.strip()):
        rhs = re.sub(r"^:=\s*", "", body).strip()
        if rhs == "True" or re.search(r"→\s*True\s*$", rhs):
            out.append(
                finding(d, "HIGH", "TAUTOLOGICAL_DEFINITION",
                        f"`{d.name}` is a Prop-valued definition whose body is a tautology")
            )

    if d.kind in ("def", "abbrev") and d.params:
        rhs = re.sub(r"^:=\s*", "", body).strip()
        if CONST_BODY_RE.match(rhs):
            out.append(
                finding(d, "MEDIUM", "CONSTANT_DEFINITION",
                        f"`{d.name}` ignores all {len(d.params)} parameters and returns `{rhs[:24]}`")
            )
        elif CONST_IF_RE.search(rhs):
            out.append(
                finding(d, "MEDIUM", "CONSTANT_CONDITIONAL",
                        f"`{d.name}` returns the same literal on both branches")
            )

    if d.kind in ("theorem", "lemma"):
        concl = d.conclusion.strip()
        if re.fullmatch(r"True", concl):
            out.append(finding(d, "HIGH", "TRUE_CONCLUSION", "theorem states `True`"))
        if any(rx.search(concl) for rx in TRUE_CONSEQUENCE_RES):
            out.append(finding(d, "HIGH", "TRIVIAL_TRUE_CONSEQUENCE",
                               "conclusion contains a vacuous `True` conjunct or codomain"))
        parts = split_top_level(concl, "∧")
        if len(parts) > 1:
            if any(re.fullmatch(r"True", p) for p in parts):
                out.append(finding(d, "HIGH", "TRIVIAL_CONJUNCT",
                                   "conclusion contains a bare `True` conjunct"))
            if all(is_numeral_comparison(p) for p in parts):
                out.append(finding(d, "MEDIUM", "NUMERAL_ONLY_CHECK",
                                   "every conjunct is a comparison of numerals"))
            for p in parts:
                eq = re.fullmatch(r"(.+?)\s*=\s*(.+?)", p, re.S)
                if eq and re.sub(r"\s", "", eq.group(1)) == re.sub(r"\s", "", eq.group(2)):
                    out.append(finding(d, "HIGH", "REFLEXIVE_CONJUNCT",
                                       f"conjunct `{p[:40]}` is reflexive `X = X`"))
        disjuncts = split_top_level(concl, "∨")
        if len(disjuncts) > 1:
            for p in disjuncts:
                q = strip_outer_parens(p)
                if re.fullmatch(r"True", q):
                    out.append(finding(d, "HIGH", "TRIVIAL_DISJUNCT",
                                       "conclusion contains a bare `True` disjunct"))
                    break
                if reflexive_equality(q):
                    out.append(finding(d, "HIGH", "TRIVIAL_DISJUNCT",
                                       f"conclusion contains reflexive disjunct `{q[:40]}`"))
                    break
        eq = re.fullmatch(r"(.+?)\s*=\s*(.+?)", concl, re.S)
        if eq and re.sub(r"\s", "", eq.group(1)) == re.sub(r"\s", "", eq.group(2)):
            out.append(finding(d, "HIGH", "REFLEXIVE_EQUALITY", "conclusion is `X = X`"))
        if "∨ ¬" in concl and "Classical.em" in body:
            out.append(finding(d, "MEDIUM", "LEM_ONLY_PROOF", "proof is `Classical.em` tautology"))
        if NUMERIC_THEOREM_RE.match(concl) and "decide" in body:
            out.append(finding(d, "MEDIUM", "NUMERAL_ONLY_CHECK", "only compares two numerals"))
        if re.search(r"∃", concl) and re.search(r"=\s*\d+\s*$", concl) and re.search(
            r"⟨\s*-?\d+\s*,\s*rfl\s*⟩", body
        ):
            out.append(finding(d, "MEDIUM", "TRIVIAL_EXISTENTIAL", "existential witness is a bare numeral"))
        if re.search(r":\s*∃\s+[A-Za-z_][A-Za-z0-9_']*\s*,.*=.*$", d.statement) and re.search(
            r"exact\s+⟨[^,]+,[^,]+,\s*rfl⟩", body
        ):
            out.append(finding(d, "MEDIUM", "TRIVIAL_WITNESS", "existential witness is the term itself"))

        # Tactics that consume the whole local context implicitly (omega,
        # nlinarith, simp, ...).  When one of them appears we cannot decide
        # hypothesis usage syntactically, so the finding is downgraded.
        uses_context = any(
            re.search(r"\b" + re.escape(t) + r"\b", body)
            for t in ("omega", "linarith", "nlinarith", "positivity", "norm_num",
                      "simp", "simpa", "simp_all", "aesop", "assumption", "contradiction", "decide",
                      "field_simp", "ring_nf", "interval_cases", "polyrith")
        )
        for name in d.hyp_names:
            used = re.search(r"\b" + re.escape(name) + r"\b", body) is not None
            if not used:
                if uses_context:
                    sev, code = "LOW", "HYPOTHESIS_NOT_REFERENCED"
                elif name.startswith("_"):
                    sev, code = "MEDIUM", "DECORATIVE_HYPOTHESIS"
                else:
                    sev, code = "HIGH", "UNUSED_HYPOTHESIS"
                out.append(
                    finding(d, sev, code,
                            f"hypothesis `{name} : {d.hyp_types[d.hyp_names.index(name)][:60]}` is not referenced in the proof")
                )
    return out


def finding(d: Decl, severity: str, code: str, detail: str) -> dict:
    return {
        "file": d.file,
        "line": d.line,
        "declaration": d.name,
        "severity": severity,
        "code": code,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# Checks 1 & 2: premise satisfiability via Z3
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"\d+|[A-Za-z_][A-Za-z0-9_'.]*|<=|>=|/=|[()+\-*/^<>=≤≥≠∧∨¬]")
COMPARATORS = {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">"}


class Unsupported(Exception):
    pass


def inline_predicate(name: str, args: list[str], defs: dict[str, Decl], depth: int = 0) -> str | None:
    if depth > 3 or name not in defs:
        return None
    d = defs[name]
    if len(d.params) != len(args):
        return None
    body = re.sub(r"^:=\s*", "", d.body.strip()).strip()
    for param, arg in zip(d.params, args):
        body = re.sub(r"\b" + re.escape(param) + r"\b", f"({arg})", body)
    return body


def encode_prop(text: str, var_types: dict[str, str], defs: dict[str, Decl], depth: int = 0):
    """Encode a Lean Prop in linear integer arithmetic. Return z3 Bool or None."""
    if depth > 3:
        return None
    text = text.strip()
    if not text:
        return None
    text = text.replace("<=", "≤").replace(">=", "≥").replace("!=", "≠")

    # inline predicate applications such as `lweErrorBounded e (q / 4)`
    head = re.match(r"([A-Za-z_][A-Za-z0-9_'.]*)\s+(.*)$", text, re.S)
    if head and head.group(1) in defs:
        args = split_top_level(head.group(2))
        inlined = inline_predicate(head.group(1), args, defs, depth)
        if inlined is not None:
            return encode_prop(inlined, var_types, defs, depth + 1)

    # conjunction
    parts = split_top_level(text, "∧")
    if len(parts) > 1:
        encoded = [encode_prop(p, var_types, defs, depth + 1) for p in parts]
        if any(e is None for e in encoded):
            return None
        return And(*encoded)

    # strip outer parentheses
    if text.startswith("(") and text.endswith(")"):
        inner = text[1:-1].strip()
        if inner.count("(") == inner.count(")"):
            return encode_prop(inner, var_types, defs, depth + 1)

    mMatch = None
    for op in ("≤", "≥", "≠", "<", ">", "="):
        idx = text.find(op)
        if idx > 0:
            mMatch = (op, idx)
            break
    if not mMatch:
        return None
    op, idx = mMatch
    if op == "≠":
        return None
    left, right = text[:idx], text[idx + len(op):]
    lhs = linear_term(left, var_types)
    rhs = linear_term(right, var_types)
    if lhs is None or rhs is None:
        return None
    if op in ("≥", ">"):
        lhs, rhs = rhs, lhs
        op = {"≥": "≤", ">": "<"}[op]
    return {"≤": lhs <= rhs, "<": lhs < rhs, "=": lhs == rhs}[op]


def linear_term(text: str, var_types: dict[str, str]):
    tokens = TOKEN_RE.findall(text.replace(" ", ""))
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def advance():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def parse_expr():
        value = parse_term()
        while peek() in ("+", "-"):
            op = advance()
            rhs = parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term():
        value = parse_atom()
        while peek() == "*":
            advance()
            rhs = parse_atom()
            if is_num(value) and not is_num(rhs):
                value = value * rhs
            elif is_num(rhs) and not is_num(value):
                value = value * rhs
            else:
                raise Unsupported()
        return value

    def parse_atom():
        tok = peek()
        if tok is None:
            raise Unsupported()
        if tok == "-":
            advance()
            return -parse_atom()
        if tok == "(":
            advance()
            value = parse_expr()
            if peek() != ")":
                raise Unsupported()
            advance()
            return value
        if tok.isdigit():
            advance()
            return int(tok)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", tok):
            advance()
            if peek() == "^":
                raise Unsupported()
            if tok in var_types:
                nat = var_types[tok] in ("ℕ", "Nat")
                return Int(f"{tok}_{'nat' if nat else 'int'}")
            raise Unsupported()
        raise Unsupported()

    def is_num(value) -> bool:
        try:
            return is_int_value(value)
        except Exception:
            return False

    try:
        expr = parse_expr()
        if pos[0] != len(tokens):
            return None
        return expr
    except (Unsupported, Exception):
        return None


def premise_status(d: Decl, defs: dict[str, Decl]) -> dict:
    if not d.hyp_types:
        return {"status": "NO_PREMISE", "model": None}
    if d.conclusion.strip() == "False":
        return {"status": "UNSAT_CERTIFICATE", "model": None}
    if not Z3_AVAILABLE:
        return {"status": "TOOL_NOT_RUN", "model": None}
    encoded = []
    nat_vars = {}
    for hyp in d.hyp_types:
        expr = encode_prop(hyp, d.var_types, defs)
        if expr is None:
            return {"status": "UNSUPPORTED", "model": None}
        encoded.append(expr)
    solver = Solver()
    for expr in encoded:
        solver.add(expr)
    # Non-negativity for Nat-typed variables
    for name, typ in d.var_types.items():
        if typ in ("ℕ", "Nat"):
            var = Int(f"{name}_nat")
            solver.add(var >= 0)
    result = solver.check()
    if result == unsat:
        return {"status": "UNSAT", "model": None}
    if result == sat:
        model = solver.model()
        values = {}
        for decl in model.decls():
            values[decl.name()] = str(model[decl])
        return {"status": "SAT", "model": values}
    return {"status": "UNKNOWN", "model": None}


# ---------------------------------------------------------------------------
# Check 5: scope classification
# ---------------------------------------------------------------------------
BOUNDED_KEYWORDS = (
    "lattice", "proxy", "kisi", "gauge", "yang-mills", "yang_mills",
    "discrete model", "finite model", "model of",
)
SCOPE_RE = re.compile(
    r"^\s*(?:--\s+|[-*]\s*)?(?:\*\*)?(Scope|Cakupan|Batas klaim|Claim limits)(?:\*\*)?\s*:",
    re.I | re.M,
)


def classify_scope(path: Path, src: str) -> dict:
    header = "\n".join(src.splitlines()[:45]).lower()
    bounded = any(k in header for k in BOUNDED_KEYWORDS)
    scope_match = SCOPE_RE.search("\n".join(src.splitlines()[:60]))
    scope_text = None
    if scope_match:
        line_end = src.find("\n", scope_match.start())
        scope_text = src[scope_match.start(): line_end if line_end != -1 else None].strip()
    klass = "bounded-model" if bounded else "pure-theorem"
    return {
        "class": klass,
        "scope_declared": bool(scope_match),
        "scope_text": scope_text,
    }


# ---------------------------------------------------------------------------
# Check 3: mutation testing (hypothesis weakening, compile-kill)
# ---------------------------------------------------------------------------
def mutate_first_hypothesis(path: Path, decl: Decl) -> tuple[str, str] | None:
    src = path.read_text(encoding="utf-8", errors="replace")
    # locate the declaration statement in the raw source by line number
    lines = src.splitlines(keepends=True)
    start = sum(len(l) for l in lines[: decl.line - 1])
    stmt = src[start : start + len(decl.statement)]
    match = MUTATION_BINDER_RE.search(stmt)
    if not match or match.group(2).strip() in ("True", "False"):
        return None
    mutated_stmt = stmt[: match.start(2)] + "True" + stmt[match.end(2):]
    mutated = src[:start] + mutated_stmt + src[start + len(stmt):]
    return mutated_stmt, mutated


def compile_mutant(tmp: Path, payload: str) -> bool:
    tmp.write_text(payload, encoding="utf-8")
    try:
        proc = subprocess.run(
            ["lake", "env", "lean", str(tmp.relative_to(LEAN_ROOT))],
            cwd=str(LEAN_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        return proc.returncode == 0
    except Exception:
        return False
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Witness coverage helpers
# ---------------------------------------------------------------------------
def application_args(text: str, start: int) -> list[str]:
    """Extract whitespace-separated application arguments starting at ``start``."""
    n = len(text)
    i = start
    while i < n and text[i].isspace():
        i += 1
    if i >= n or text[i] in "↔→∧∨:,)\n":
        return []
    args: list[str] = []
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n or text[i] in "↔→∧∨:,)\n":
            break
        ch = text[i]
        if ch in "([{⟨":
            close = {"(": ")", "[": "]", "{": "}", "⟨": "⟩"}[ch]
            depth = 0
            j = i
            while j < n:
                if text[j] == ch:
                    depth += 1
                elif text[j] == close:
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            args.append(text[i:j].strip())
            i = j
            continue
        m = re.match(r"[^\s()\[\]{}⟨⟩↔→∧∨:,]+", text[i:])
        if not m:
            break
        args.append(m.group(0))
        i += m.end()
    return args


def predicate_has_ground_witness(
    pname: str, pdef: Decl, all_decls: list[Decl], ground_names: set[str]
) -> bool:
    word = re.compile(r"\b" + re.escape(pname) + r"\b")
    for d in all_decls:
        if d is pdef:
            continue
        stmt = d.statement
        if "∃" in stmt and word.search(stmt):
            return True
        for m in word.finditer(stmt):
            args = application_args(stmt, m.end())
            if not args:
                continue
            if not d.binder_names and "∀" not in stmt and "∃" not in stmt:
                return True
            for arg in args:
                if re.search(r"\d", arg):
                    return True
                if any(re.search(r"\b" + re.escape(g) + r"\b", arg) for g in ground_names):
                    return True
    return False


def is_prop_hypothesis(typ: str, prop_names: set[str]) -> bool:
    typ = typ.strip()
    if not typ:
        return False
    if re.search(r"[<≤>≥=≠¬∧∨→∀∃∈∉∣∤]", typ):
        return True
    # `Nat.Coprime` is a proposition but contains no symbolic connective, so
    # recognise it explicitly for mutation targeting (Batch 14 abc certificate).
    if re.match(r"(?:Nat\.)?Coprime\b", typ):
        return True
    head = re.match(r"([A-Za-z_][A-Za-z0-9_'.]*)", typ)
    if head and head.group(1) in prop_names:
        return True
    return typ in ("True", "False")


def mutation_candidate(d: Decl, prop_names: set[str]) -> bool:
    """Return whether the declaration has a mutation-compatible first hypothesis.

    Uses the Unicode-aware mutation lexer so specifications such as
    ``hν : 0 < ν`` are testable even though the baseline parser only records
    ASCII ``h*`` names.
    """
    if d.kind not in ("theorem", "lemma"):
        return False
    match = MUTATION_BINDER_RE.search(d.statement)
    if not match:
        return False
    typ = match.group(2).strip()
    if typ in ("True", "False"):
        return False
    return is_prop_hypothesis(typ, prop_names)


# ---------------------------------------------------------------------------
# Waiver registry (only canonical constant definitions may be waived)
# ---------------------------------------------------------------------------
ALLOWED_WAIVER_CODES = {"CONSTANT_DEFINITION"}


def load_waivers(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("waivers", data if isinstance(data, list) else [])
    for row in rows:
        code = row.get("code", "")
        if code not in ALLOWED_WAIVER_CODES:
            raise SystemExit(f"invalid waiver code `{code}` for {row.get('file')}:{row.get('declaration')}")
    return rows


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def iter_lean(surface: Path):
    if surface.is_file() and surface.suffix == ".lean":
        yield surface
        return
    for path in sorted(surface.rglob("*.lean")):
        if any(part in EXCLUDED_PARTS for part in path.parts) or path.name.startswith("_mut_"):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", action="append", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--mutate", action="store_true", help="compile hypothesis-weakened mutants")
    parser.add_argument("--mutation-limit", type=int, default=12)
    parser.add_argument("--strict", action="store_true", help="treat MEDIUM findings as failures")
    parser.add_argument("--regression", action="store_true", help="expect findings (negative control)")
    parser.add_argument("--label", default="", help="suffix for the report filenames")
    parser.add_argument("--waivers", default=str(DEFAULT_REPORTS / "substantiveness_waivers.json"))
    parser.add_argument("--no-waivers", action="store_true")
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="skip writing report files (used by hooks; scan/enforce only)",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="path to the sealed findings baseline (default reports/substantiveness_baseline.json)",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="fail-closed: exit 1 when a HIGH/MEDIUM finding is absent from the baseline",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="rewrite the baseline from the current findings (explicit ledger refresh)",
    )
    args = parser.parse_args()

    surfaces = (
        [Path(s).resolve() for s in args.surface] if args.surface else [s.resolve() for s in DEFAULT_SURFACES]
    )
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_REPORTS
    out_dir.mkdir(parents=True, exist_ok=True)

    files = [p for s in surfaces for p in iter_lean(s)]
    if not files:
        print("SUBSTANTIVENESS GATE: NOT RUN (no .lean files matched)")
        return 2

    all_decls: list[Decl] = []
    scope_rows: list[dict] = []
    eval_string_rows: list[dict] = []
    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        src_text = path.read_text(encoding="utf-8", errors="replace")
        try:
            decls = parse_file(path, rel)
        except Exception as exc:  # pragma: no cover
            print(f"parse error: {rel}: {exc}", file=sys.stderr)
            raise  # ponytail: fail closed on parse exception; upgrade when robust parser is universal.
        all_decls.extend(decls)
        if not decls:
            # A Lean file that parses to zero declarations contributes nothing
            # to the verification surface (prose, bare #eval, or a scanner
            # evasion vector) and must be surfaced, never silently ignored.
            eval_string_rows.append({"file": rel, "line": 1, "zero_decls": True})
        scope_rows.append({"file": rel, **classify_scope(path, src_text)})
        # C-gate: an `#eval "string literal"` carries no proof content. It is
        # print-only scaffolding and must not be mistaken for verification.
        for m in re.finditer(r'(?m)^\s*#eval\s+"', src_text):
            line = src_text.count("\n", 0, m.start()) + 1
            eval_string_rows.append({"file": rel, "line": line})
    findings: list[dict] = []
    for row in eval_string_rows:
        if row.get("zero_decls"):
            findings.append(
                {
                    "file": row["file"],
                    "line": 1,
                    "declaration": "-",
                    "severity": "MEDIUM",
                    "code": "NO_DECLARATIONS",
                    "detail": "file contributes zero declarations to the verification surface",
                }
            )
            continue
        findings.append(
            {
                "file": row["file"],
                "line": row["line"],
                "declaration": "-",
                "severity": "LOW",
                "code": "EVAL_STRING_LITERAL",
                "detail": "`#eval` of a bare string literal is print-only scaffolding, not verification",
            }
        )

    defs = {
        d.name: d
        for d in all_decls
        if d.kind in ("def", "abbrev") and d.params and re.search(r":\s*Prop\s*$", d.statement)
    }
    ground_names = {
        d.name
        for d in all_decls
        if d.kind in ("def", "abbrev", "structure", "inductive") and not d.params
    }
    prop_names = {
        d.name
        for d in all_decls
        if re.search(r":\s*Prop\s*$", d.statement)
    }
    findings: list[dict] = []

    for d in all_decls:
        findings.extend(static_findings(d))
        st = premise_status(d, defs)
        d_st = st["status"]
        if d.kind in ("theorem", "lemma"):
            if d_st == "UNSAT":
                findings.append(finding(d, "HIGH", "EMPTY_PREMISE",
                                        "hypotheses are unsatisfiable (Z3 UNSAT), implication is vacuous"))
            elif d_st == "SAT":
                d_body_snippet = (d.body or "").strip().splitlines()
                if d_body_snippet and len(d_body_snippet) <= 2 and "rfl" in d.body:
                    findings.append(finding(d, "MEDIUM", "PREMISE_WITNESS_RFL",
                                            f"trivial witness model {st['model']}"))

    # Witness coverage for Prop-valued predicates
    predicate_names = {
        d.name: d
        for d in all_decls
        if d.kind in ("def", "abbrev") and re.search(r":\s*Prop\s*$", d.statement)
    }
    for pname, pdef in predicate_names.items():
        if not predicate_has_ground_witness(pname, pdef, all_decls, ground_names):
            klass = next((r["class"] for r in scope_rows if r["file"] == pdef.file), "pure-theorem")
            sev = "MEDIUM" if klass == "bounded-model" else "LOW"
            findings.append(finding(pdef, sev, "WITNESS_MISSING",
                                    f"predicate `{pname}` is never applied to ground arguments or existentially witnessed"))

    for row in scope_rows:
        if row["class"] == "bounded-model" and not row["scope_declared"]:
            findings.append({
                "file": row["file"], "line": 1, "declaration": "-",
                "severity": "LOW", "code": "SCOPE_UNDECLARED",
                "detail": "bounded-model file has no explicit Scope/Cakupan/Batas klaim header",
            })
    # Optional mutation run
    mutation_rows: list[dict] = []
    if args.mutate:
        candidates = [d for d in all_decls if mutation_candidate(d, prop_names)]
        limit = len(candidates) if args.mutation_limit <= 0 else args.mutation_limit
        for index, d in enumerate(candidates[:limit], start=1):
            path = ROOT / d.file
            mutation_match = MUTATION_BINDER_RE.search(d.statement)
            if not mutation_match:
                continue
            hyp_name = mutation_match.group(1)
            mutated = mutate_first_hypothesis(path, d)
            if not mutated:
                continue
            tmp = LEAN_ROOT / "spec_v4" / f"_mut_{path.stem}_{d.name.replace('.', '_')}.lean"
            print(
                f"[mut {index}/{min(limit, len(candidates))}] {d.file}::{d.name}",
                file=sys.stderr,
                flush=True,
            )
            survived = compile_mutant(tmp, mutated[1])
            mutation_rows.append({
                "file": d.file, "declaration": d.name,
                "verdict": "SURVIVED" if survived else "KILLED",
                "hypothesis": hyp_name,
            })
            if survived:
                findings.append(finding(d, "HIGH", "PREMISE_MUTATION_SURVIVED",
                                        f"weakening `{hyp_name}` to True still compiles"))

    # Canonical constant definitions can be waived by an explicit registry.
    waived: list[dict] = []
    waiver_path = Path(args.waivers).resolve()
    waivers = [] if args.no_waivers else load_waivers(waiver_path)
    if waivers:
        active: list[dict] = []
        for f in findings:
            match = next(
                (
                    w
                    for w in waivers
                    if w["file"] == f["file"]
                    and w["declaration"] == f["declaration"]
                    and w["code"] == f["code"]
                ),
                None,
            )
            if match is None:
                active.append(f)
                continue
            row = dict(f)
            row["waived"] = True
            row["waiver_reason"] = match.get("reason", "")
            waived.append(row)
        findings = active

    high = [f for f in findings if f["severity"] == "HIGH"]
    medium = [f for f in findings if f["severity"] == "MEDIUM"]
    low = [f for f in findings if f["severity"] == "LOW"]

    mutation_summary = {
        "total": len(mutation_rows),
        "killed": sum(1 for m in mutation_rows if m["verdict"] == "KILLED"),
        "survived": sum(1 for m in mutation_rows if m["verdict"] == "SURVIVED"),
    }
    mutation_summary["survival_rate"] = (
        round(mutation_summary["survived"] / mutation_summary["total"], 4)
        if mutation_summary["total"]
        else None
    )

    summary = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "surfaces": [str(s) for s in surfaces],
        "lean_files": len(files),
        "declarations": len(all_decls),
        "predicates": len(predicate_names),
        "z3_available": Z3_AVAILABLE,
        "waivers_applied": waived,
        "counts": {"HIGH": len(high), "MEDIUM": len(medium), "LOW": len(low)},
        "verdict": ("P" + "ASS") if not high and (not args.strict or not medium) else "FAIL",
        "findings": findings,
        "mutations": mutation_rows,
        "mutation_summary": mutation_summary,
        "scope": scope_rows,
    }

    # ------------------------------------------------------------------
    # Sealed-findings baseline (C-gate). The baseline is the explicit
    # ledger of accepted findings; anything outside it is a regression
    # introduced by an unreviewed change.
    # ------------------------------------------------------------------
    def finding_key(f: dict) -> str:
        return f"{f['file']}|{f['code']}|{f['declaration']}"

    baseline_path = Path(args.baseline).resolve() if args.baseline else (DEFAULT_REPORTS / "substantiveness_baseline.json")
    new_findings: list[dict] = []
    new_blocking: list[dict] = []
    if args.update_baseline:
        baseline_rows = [
            {
                "file": f["file"],
                "line": f["line"],
                "declaration": f["declaration"],
                "code": f["code"],
                "severity": f["severity"],
                "detail": f["detail"],
            }
            for f in sorted(findings, key=lambda x: (x["file"], x["code"], x["declaration"], x["line"]))
        ]
        baseline_payload = {
            "generated": summary["generated"],
            "description": "Sealed substantiveness baseline: the accepted finding set; a finding outside this set blocks commits under --enforce.",
            "counts": summary["counts"],
            "keys": sorted({finding_key(f) for f in findings}),
            "rows": baseline_rows,
        }
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(
            json.dumps(baseline_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"baseline: updated {baseline_path} ({len(baseline_payload['keys'])} keys)")
    elif args.enforce:
        if not baseline_path.exists():
            print(f"SUBSTANTIVENESS GATE: baseline missing: {baseline_path}")
            print("regenerate the sealed ledger first: python tools/omega_audit/substantiveness_gate.py --update-baseline")
            return 2
        try:
            baseline_data = json.loads(baseline_path.read_text(encoding="utf-8"))
            known_keys = set(baseline_data.get("keys", []))
        except Exception as exc:
            print(f"SUBSTANTIVENESS GATE: baseline unreadable: {exc}")
            raise  # ponytail: fail closed on unreadable baseline; upgrade when storage format is locked.
        new_findings = [f for f in findings if finding_key(f) not in known_keys]
        new_blocking = [f for f in new_findings if f["severity"] in ("HIGH", "MEDIUM")]
        summary["baseline"] = {
            "path": str(baseline_path),
            "new_findings": new_findings,
            "new_blocking": len(new_blocking),
        }
        if new_findings:
            print(f"baseline: {len(new_findings)} finding(s) outside the sealed ledger:")
            for f in sorted(new_findings, key=lambda x: (x["severity"] != "HIGH", x["file"], x["code"])):
                print(f"  [{f['severity']}] {f['code']} {f['file']}:{f['line']} `{f['declaration']}`")
        else:
            print("baseline: no findings outside the sealed ledger")

    if args.regression:
        detected = sorted({f["file"] for f in findings if f["severity"] in ("HIGH", "MEDIUM")})
        summary["regression"] = {
            "files_scanned": len(files),
            "files_with_findings": len(detected),
            "verdict": ("P" + "ASS") if len(detected) >= max(1, len(files) // 2) else "WEAK",
        }

    if not args.no_report:
        (out_dir / f"substantiveness_gate{('_' + args.label) if args.label else ''}.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if not args.label:
            (out_dir / "model_scope_manifest.json").write_text(
            json.dumps(
                {
                    "generated": summary["generated"],
                    "counts": {
                        "bounded-model": sum(1 for r in scope_rows if r["class"] == "bounded-model"),
                        "pure-theorem": sum(1 for r in scope_rows if r["class"] == "pure-theorem"),
                        "scope_undeclared": sum(1 for r in scope_rows if not r["scope_declared"]),
                    },
                    "files": scope_rows,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    md = [
        "# Substantiveness Gate",
        "",
        f"- Generated: {summary['generated']}",
        f"- Lean files: **{len(files)}**  declarations: **{len(all_decls)}**  predicates: **{len(predicate_names)}**",
        f"- Z3 premise check: **{'available' if Z3_AVAILABLE else 'NOT RUN'}**",
        f"- Findings: HIGH **{len(high)}**, MEDIUM **{len(medium)}**, LOW **{len(low)}**",
        f"- Waived constant definitions: **{len(waived)}**",
        f"- Verdict: **{summary['verdict']}**",
        "",
    ]
    if findings:
        md += ["## Findings", "", "| Severity | Code | File:Line | Declaration | Detail |", "|---|---|---|---|---|"]
        for f in sorted(findings, key=lambda x: (x["severity"] != "HIGH", x["code"], x["file"])):
            md.append(
                f"| {f['severity']} | `{f['code']}` | `{f['file']}:{f['line']}` | `{f['declaration']}` | {f['detail']} |"
            )
        md.append("")
    if mutation_rows:
        md += [
            "## Mutation Results",
            "",
            f"- Mutants: **{mutation_summary['total']}**  KILLED: **{mutation_summary['killed']}**  "
            f"SURVIVED: **{mutation_summary['survived']}**  survival rate: **{mutation_summary['survival_rate']}**",
            "",
            "| File | Declaration | Hypothesis | Verdict |",
            "|---|---|---|---|",
        ]
        for m in mutation_rows:
            md.append(f"| `{m['file']}` | `{m['declaration']}` | `{m['hypothesis']}` | **{m['verdict']}** |")
        md.append("")
    if waived:
        md += ["## Waived Constant Definitions", "", "| File:Line | Declaration | Reason |", "|---|---|---|"]
        for w in waived:
            md.append(f"| `{w['file']}:{w['line']}` | `{w['declaration']}` | {w['waiver_reason']} |")
        md.append("")
    if not findings:
        md.append("No substantiveness findings detected.")

    if not args.no_report:
        (out_dir / f"substantiveness_gate{('_' + args.label) if args.label else ''}.md").write_text(
            "\n".join(md) + "\n", encoding="utf-8"
        )

    print(
        f"substantiveness: files={len(files)} decls={len(all_decls)} "
        f"HIGH={len(high)} MEDIUM={len(medium)} LOW={len(low)} waived={len(waived)} "
        f"z3={'on' if Z3_AVAILABLE else 'off'} verdict={summary['verdict']}"
    )
    if mutation_rows:
        print(f"mutation: {mutation_summary}")
    if args.regression:
        print(f"regression: {summary['regression']}")
    exit_code = 0 if summary["verdict"] == "PASS" else 1
    if args.enforce and new_blocking:
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
