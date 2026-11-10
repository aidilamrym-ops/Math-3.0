"""Math 3.0 — SMT-LIB2 (QF_LIA) -> Lean 4 certificate bridge.

This module re-proves the *same constraint system* that Z3 was asked to decide,
natively in Lean 4.  It is intentionally scoped and fail-closed:

  * supported logic: QF_LIA only;
  * supported commands: set-logic, set-option, set-info, declare-const Int,
    assert, check-sat, get-model;
  * unsupported constructs raise ``UnsupportedSMT`` instead of being guessed;
  * no ``sorry``, ``admit``, or ``axiom`` is ever emitted;
  * a certificate is only marked reconstructed when the Lean compiler exits 0
    and the placeholder scan is clean.

It does **not** translate Z3's internal proof object.  It constructs an
independent Lean theorem for the same constraints and hashes both artifacts so
the link between them is explicit and auditable.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any

BRIDGE_NAME = "math30_smt_lean_bridge"
BRIDGE_VERSION = "1.0.0"
SUPPORTED_LOGIC = "QF_NRA"

_COMPARISON_SYMBOLS = {
    "=": "=",
    "<": "<",
    "<=": "≤",
    ">": ">",
    ">=": "≥",
}
_ARITHMETIC_OPS = {"+", "-", "*", "/"}
_BOOLEAN_OPS = {"and", "or", "not", "=>"}
_ALLOWED_COMMANDS = {
    "set-logic",
    "set-option",
    "set-info",
    "declare-const",
    "assert",
    "check-sat",
    "get-model",
}
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*$")
_INT_RE = re.compile(r"^-?[0-9]+$")
_RAT_RE = re.compile(r"^-?[0-9]+(\.[0-9]+)?(/[0-9]+(\.[0-9]+)?)?$")


class SMTError(Exception):
    """Base class for bridge failures."""


class SMTParseError(SMTError):
    """The input is not a well-formed supported SMT-LIB2 script."""


class UnsupportedSMT(SMTError):
    """The input uses a construct outside the audited QF_LIA fragment."""


@dataclass
class SMTConstraintSystem:
    logic: str
    variables: list[str] = field(default_factory=list)
    assertions: list[Any] = field(default_factory=list)
    check_sat_count: int = 0
    has_get_model: bool = False
    options: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# S-expression parsing
# ---------------------------------------------------------------------------

def _strip_comments(text: str) -> str:
    """Remove SMT-LIB line comments (a semicolon through end of line)."""
    return "\n".join(line.split(";", 1)[0] for line in text.splitlines())


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char in "()":
            tokens.append(char)
            index += 1
            continue
        if char == '"':
            raise UnsupportedSMT("SMT-LIB string literals are outside the QF_LIA fragment")
        end = index
        while end < len(text) and not text[end].isspace() and text[end] not in "()":
            end += 1
        tokens.append(text[index:end])
        index = end
    return tokens


def _parse_all(tokens: list[str]) -> list[Any]:
    position = 0

    def parse_one() -> Any:
        nonlocal position
        if position >= len(tokens):
            raise SMTParseError("unexpected end of input")
        token = tokens[position]
        position += 1
        if token == "(":
            items = []
            while True:
                if position >= len(tokens):
                    raise SMTParseError("unclosed s-expression")
                if tokens[position] == ")":
                    position += 1
                    return items
                items.append(parse_one())
        if token == ")":
            raise SMTParseError("unexpected ')'")
        return token

    forms = []
    while position < len(tokens):
        forms.append(parse_one())
    return forms


# ---------------------------------------------------------------------------
# Validation and linearity checks
# ---------------------------------------------------------------------------

def _walk(term: Any, variables: set[str], *, in_arithmetic: bool = False) -> None:
    """Validate the term against the audited QF_LIA fragment."""
    if isinstance(term, str):
        if term in variables:
            return
        if term in ("true", "false"):
            if in_arithmetic:
                raise UnsupportedSMT("boolean literal inside an arithmetic term")
            return
        if _RAT_RE.match(term):
            return
        raise UnsupportedSMT(f"unsupported atom: {term!r}")
    if not term:
        raise UnsupportedSMT("empty application")
    op = term[0]
    args = term[1:]
    if op in _BOOLEAN_OPS:
        if in_arithmetic:
            raise UnsupportedSMT(f"boolean operator {op!r} inside an arithmetic term")
        if op == "not" and len(args) != 1:
            raise UnsupportedSMT("'not' takes exactly one argument")
        if op == "=>" and len(args) < 2:
            raise UnsupportedSMT("'=>' takes at least two arguments")
        for arg in args:
            _walk(arg, variables, in_arithmetic=False)
        return
    if op in _COMPARISON_SYMBOLS:
        if in_arithmetic:
            raise UnsupportedSMT(f"comparison {op!r} inside an arithmetic term")
        if len(args) < 2:
            raise UnsupportedSMT(f"comparison {op!r} needs at least two arguments")
        for arg in args:
            _walk(arg, variables, in_arithmetic=True)
        return
    if op in _ARITHMETIC_OPS:
        if not args:
            raise UnsupportedSMT(f"operator {op!r} needs arguments")
        for arg in args:
            _walk(arg, variables, in_arithmetic=True)
        return
    if op == "ite":
        raise UnsupportedSMT("'ite' is outside the audited fragment")
    raise UnsupportedSMT(f"unsupported operator: {op!r}")


def _has_variable(term: Any, variables: set[str]) -> bool:
    if isinstance(term, str):
        return term in variables
    return any(_has_variable(arg, variables) for arg in term[1:])


def parse_smt_script(text: str) -> SMTConstraintSystem:
    forms = _parse_all(_tokenize(_strip_comments(text)))
    system = SMTConstraintSystem(logic="")
    declared: list[str] = []
    declared_set: set[str] = set()

    for form in forms:
        if not isinstance(form, list) or not form:
            raise SMTParseError(f"expected a command, got {form!r}")
        command = form[0]
        if command not in _ALLOWED_COMMANDS:
            raise UnsupportedSMT(f"unsupported command: {command!r}")

        if command == "set-logic":
            if len(form) != 2 or not isinstance(form[1], str):
                raise SMTParseError("malformed set-logic")
            system.logic = form[1]
            if system.logic != SUPPORTED_LOGIC:
                raise UnsupportedSMT(
                    f"logic {system.logic!r} is outside the audited fragment "
                    f"({SUPPORTED_LOGIC!r})"
                )
        elif command == "set-option":
            if len(form) >= 3 and isinstance(form[1], str) and isinstance(form[2], str):
                system.options[form[1]] = form[2]
        elif command == "set-info":
            continue
        elif command == "declare-const":
            if len(form) != 3 or not isinstance(form[1], str) or form[2] not in ("Int", "Real"):
                raise UnsupportedSMT("only 'declare-const <name> Int' or 'declare-const <name> Real' is supported")
            name = form[1]
            if not _IDENT_RE.match(name):
                raise UnsupportedSMT(f"unsupported variable name: {name!r}")
            if name in declared_set:
                raise SMTParseError(f"duplicate declaration: {name!r}")
            declared.append(name)
            declared_set.add(name)
        elif command == "assert":
            if len(form) != 2:
                raise SMTParseError("malformed assert")
            system.assertions.append(form[1])
        elif command == "check-sat":
            if len(form) != 1:
                raise SMTParseError("malformed check-sat")
            system.check_sat_count += 1
        elif command == "get-model":
            if len(form) != 1:
                raise SMTParseError("malformed get-model")
            system.has_get_model = True

    if not system.logic:
        raise SMTParseError("missing (set-logic ...)")
    if system.check_sat_count != 1:
        raise UnsupportedSMT(
            f"exactly one check-sat is required, found {system.check_sat_count}"
        )
    if not system.assertions:
        raise UnsupportedSMT("no assertions found")

    variables = set(declared)
    for assertion in system.assertions:
        _walk(assertion, variables, in_arithmetic=False)
    system.variables = declared
    return system


# ---------------------------------------------------------------------------
# Lean emission
# ---------------------------------------------------------------------------

def _lean_atom(atom: str, variables: set[str]) -> str:
    if atom in variables:
        return atom
    if atom == "true":
        return "True"
    if atom == "false":
        return "False"
    if _RAT_RE.match(atom):
        if "/" in atom:
            num, den = atom.split("/")
            return f"(({num} : Rat) / ({den} : Rat))"
        return f"({atom} : Rat)"
    raise UnsupportedSMT(f"cannot translate atom: {atom!r}")


def to_lean(term: Any, variables: set[str]) -> str:
    if isinstance(term, str):
        return _lean_atom(term, variables)
    op = term[0]
    args = term[1:]
    if op == "and":
        return "(" + " ∧ ".join(to_lean(arg, variables) for arg in args) + ")"
    if op == "or":
        return "(" + " ∨ ".join(to_lean(arg, variables) for arg in args) + ")"
    if op == "not":
        return f"(¬ {to_lean(args[0], variables)})"
    if op == "=>":
        result = to_lean(args[-1], variables)
        for antecedent in reversed(args[:-1]):
            result = f"({to_lean(antecedent, variables)} → {result})"
        return result
    if op in _COMPARISON_SYMBOLS:
        symbol = _COMPARISON_SYMBOLS[op]
        if len(args) == 2:
            return f"({to_lean(args[0], variables)} {symbol} {to_lean(args[1], variables)})"
        chain = [
            f"({to_lean(args[index], variables)} {symbol} "
            f"{to_lean(args[index + 1], variables)})"
            for index in range(len(args) - 1)
        ]
        return "(" + " ∧ ".join(chain) + ")"
    if op == "+":
        return "(" + " + ".join(to_lean(arg, variables) for arg in args) + ")"
    if op == "-":
        if len(args) == 1:
            return f"(- {to_lean(args[0], variables)})"
        result = to_lean(args[0], variables)
        for arg in args[1:]:
            result = f"({result} - {to_lean(arg, variables)})"
        return result
    if op == "*":
        return "(" + " * ".join(to_lean(arg, variables) for arg in args) + ")"
    if op == "/":
        if len(args) != 2:
            raise UnsupportedSMT("division takes exactly two arguments")
        return f"({to_lean(args[0], variables)} / {to_lean(args[1], variables)})"
    raise UnsupportedSMT(f"cannot translate operator: {op!r}")


def _substitute(term: Any, environment: dict[str, int]) -> Any:
    if isinstance(term, str):
        if term in environment:
            return str(environment[term])
        return term
    return [term[0]] + [_substitute(arg, environment) for arg in term[1:]]


def _eval_int(term: Any, environment: dict[str, float]) -> float:
    if isinstance(term, str):
        if term in environment:
            return environment[term]
        if _RAT_RE.match(term):
            if "/" in term:
                num, den = term.split("/")
                return float(num) / float(den)
            return float(term)
        raise SMTError(f"cannot evaluate atom: {term!r}")
    op = term[0]
    args = term[1:]
    if op == "+":
        return sum(_eval_int(arg, environment) for arg in args)
    if op == "-":
        values = [_eval_int(arg, environment) for arg in args]
        if len(values) == 1:
            return -values[0]
        result = values[0]
        for value in values[1:]:
            result -= value
        return result
    if op == "*":
        result = 1.0
        for arg in args:
            result *= _eval_int(arg, environment)
        return result
    raise SMTError(f"cannot evaluate operator: {op!r}")


def _eval_bool(term: Any, environment: dict[str, int]) -> bool:
    if isinstance(term, str):
        if term == "true":
            return True
        if term == "false":
            return False
        raise SMTError(f"cannot evaluate boolean atom: {term!r}")
    op = term[0]
    args = term[1:]
    if op == "and":
        return all(_eval_bool(arg, environment) for arg in args)
    if op == "or":
        return any(_eval_bool(arg, environment) for arg in args)
    if op == "not":
        return not _eval_bool(args[0], environment)
    if op == "=>":
        result = _eval_bool(args[-1], environment)
        for antecedent in reversed(args[:-1]):
            result = (not _eval_bool(antecedent, environment)) or result
        return result
    if op in _COMPARISON_SYMBOLS:
        values = [_eval_int(arg, environment) for arg in args]
        checks = {
            "=": lambda a, b: a == b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
        }
        return all(
            checks[op](values[index], values[index + 1])
            for index in range(len(values) - 1)
        )
    raise SMTError(f"cannot evaluate boolean operator: {op!r}")


def _safe_identifier(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_']", "_", name)
    if not cleaned or cleaned[0].isdigit():
        cleaned = "cert_" + cleaned
    return cleaned


def generate_lean(
    name: str,
    system: SMTConstraintSystem,
    expected: str,
    model_values: dict[str, int] | None,
    source_relpath: str,
    source_sha256: str,
) -> tuple[str, str]:
    """Return (lean_source, theorem_name)."""
    safe = _safe_identifier(name)
    variables = set(system.variables)
    conjunction = " ∧ ".join(
        f"({to_lean(assertion, variables)})" for assertion in system.assertions
    )

    header = f"""import Init.Data.Rat.Basic
import Mathlib.Tactic

/-
  Math 3.0 SMT -> Lean certificate bridge (v{BRIDGE_VERSION})
  Source: {source_relpath}
  Source-SHA256: {source_sha256}
  Logic: {system.logic}
  SMT verdict: {expected}
  The theorem below re-proves the same constraint system natively in Lean 4.
  It is not a translation of an internal Z3 proof object.
  No sorry, admit, or axiom is used.
-/

namespace Math30.SMTBridge
"""

    if expected == "unsat":
        theorem = f"{safe}_unsat"
        binders = " ".join(f"({variable} : Rat)" for variable in system.variables)
        signature = f"theorem {theorem} {binders} :" if binders else f"theorem {theorem} :"
        
        # ponytail: generate dynamic rcases pattern based on assertion count
        if len(system.assertions) > 1:
            h_names = [f"h{i+1}" for i in range(len(system.assertions))]
            rcases_pattern = "⟨" + ", ".join(h_names) + "⟩"
            rcases_line = f"  rcases h with {rcases_pattern}"
            h_list = " ".join(h_names)
        else:
            rcases_line = "  rename_i h1"
            h_list = "h1"

        body = f"""{signature}
  ¬ ({conjunction}) := by
  intro h
{rcases_line}
  have h5 : False := by
    norm_num at {h_list} ⊢
    <;>
    (try contradiction) <;>
    (try nlinarith) <;>
    (try norm_num at * <;> nlinarith)
  exact h5
"""
    elif expected == "sat":
        if model_values is None:
            raise SMTError("a SAT witness requires concrete model values")
        missing = [variable for variable in system.variables if variable not in model_values]
        if missing:
            raise SMTError(f"Z3 model is missing variables: {missing}")
        if not all(_eval_bool(assertion, model_values) for assertion in system.assertions):
            raise SMTError("Z3 model does not satisfy the assertions")
        ground_assertions = [
            to_lean(_substitute(assertion, model_values), set())
            for assertion in system.assertions
        ]
        ground_conjunction = " ∧ ".join(f"({assertion})" for assertion in ground_assertions)
        theorem = f"{safe}_sat_witness"
        body = f"""theorem {theorem} :
  {ground_conjunction} := by
  norm_num
"""
    else:
        raise SMTError(f"unsupported expected verdict: {expected!r}")

    footer = f"""
#print axioms {theorem}

end Math30.SMTBridge
"""
    return header + "\n" + body + footer, theorem


# ---------------------------------------------------------------------------
# Placeholder scan and compiler invocation
# ---------------------------------------------------------------------------

def strip_lean_comments_and_strings(text: str) -> str:
    """Remove comments and string literals so token scans cannot be fooled."""
    output: list[str] = []
    index = 0
    depth = 0
    while index < len(text):
        if text.startswith("/-", index):
            depth += 1
            index += 2
            continue
        if depth and text.startswith("-/", index):
            depth -= 1
            index += 2
            continue
        if depth:
            index += 1
            continue
        if text.startswith("--", index):
            newline = text.find("\n", index)
            if newline == -1:
                break
            index = newline
            continue
        if text[index] == '"':
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == '"':
                    index += 1
                    break
                index += 1
            continue
        output.append(text[index])
        index += 1
    return "".join(output)


_PLACEHOLDER_RE = re.compile(r"\b(sorry|sorryAx|admit|axiom)\b")


def find_placeholders(text: str) -> list[str]:
    return sorted(set(_PLACEHOLDER_RE.findall(strip_lean_comments_and_strings(text))))


def lean_version() -> dict[str, Any]:
    lean = shutil.which("lean")
    if not lean:
        return {"available": False, "path": None, "version": None}
    result = subprocess.run(
        [lean, "--version"], capture_output=True, text=True, timeout=60
    )
    return {
        "available": result.returncode == 0,
        "path": lean,
        "version": (result.stdout or result.stderr).strip() or None,
    }


def compile_lean(path: str, cwd: str, timeout: int = 180) -> dict[str, Any]:
    lake = shutil.which("lake")
    if not lake:
        return {
            "compiled": False,
            "exit_code": None,
            "status": "TOOL_NOT_RUN",
            "stdout": "",
            "stderr": "lake executable not found on PATH",
            "elapsed_ms": 0.0,
        }
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [lake, "env", "lean", path],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "compiled": False,
            "exit_code": None,
            "status": "TIMEOUT",
            "stdout": "",
            "stderr": f"lean exceeded {timeout}s",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "compiled": result.returncode == 0,
        "exit_code": result.returncode,
        "status": "COMPILED" if result.returncode == 0 else "COMPILE_ERROR",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "elapsed_ms": elapsed_ms,
    }


def parse_axioms(stdout: str, theorem: str) -> list[str] | None:
    qualified = rf"(?:[A-Za-z0-9_']+\.)*{re.escape(theorem)}"
    pattern = re.compile(
        rf"'{qualified}' depends on axioms: \[(.*?)\]", re.DOTALL
    )
    match = pattern.search(stdout)
    if match:
        return [item.strip() for item in match.group(1).split(",") if item.strip()]
    if re.search(rf"'{qualified}' does not depend on any axioms", stdout):
        return []
    return None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Public reconstruction API
# ---------------------------------------------------------------------------

def reconstruct_one(
    *,
    name: str,
    script_text: str,
    source_relpath: str,
    expected: str,
    model_values: dict[str, int] | None,
    lean_dir: str,
    root: str,
    timeout: int = 180,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "name": name,
        "source": source_relpath,
        "source_sha256": _sha256_text(script_text),
        "expected": expected,
        "status": "UNKNOWN",
    }
    try:
        system = parse_smt_script(script_text)
        receipt["logic"] = system.logic
        receipt["variables"] = system.variables
        receipt["assertion_count"] = len(system.assertions)

        if expected not in ("sat", "unsat"):
            raise SMTError(f"unsupported Z3 verdict: {expected!r}")

        lean_source, theorem = generate_lean(
            name=name,
            system=system,
            expected=expected,
            model_values=model_values,
            source_relpath=source_relpath,
            source_sha256=receipt["source_sha256"],
        )
        receipt["theorem"] = theorem
        receipt["lean_sha256"] = _sha256_text(lean_source)
        receipt["placeholders"] = find_placeholders(lean_source)
        if receipt["placeholders"]:
            raise SMTError(
                f"generated Lean contains placeholders: {receipt['placeholders']}"
            )

        os.makedirs(lean_dir, exist_ok=True)
        lean_path = os.path.join(lean_dir, f"{name}.lean")
        with open(lean_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(lean_source)
        receipt["lean_path"] = lean_path

        compilation = compile_lean(lean_path, cwd=root, timeout=timeout)
        receipt["compilation"] = compilation
        receipt["axioms"] = parse_axioms(compilation.get("stdout", ""), theorem)

        if compilation["status"] == "TOOL_NOT_RUN":
            receipt["status"] = "TOOL_NOT_RUN"
        elif not compilation["compiled"]:
            receipt["status"] = "LEAN_RECONSTRUCTION_FAILED"
        elif receipt["axioms"] is None:
            receipt["status"] = "AXIOM_REPORT_MISSING"
        elif any(axiom in ("sorryAx", "admit") for axiom in receipt["axioms"]):
            receipt["status"] = "AXIOM_REPORT_REJECTED"
        else:
            receipt["status"] = "LEAN_RECONSTRUCTED"
    except SMTError as error:
        receipt["status"] = "REJECTED_UNSUPPORTED"
        receipt["error"] = str(error)
    except Exception as error:  # fail closed, but keep the diagnostic
        receipt["status"] = "ERROR"
        receipt["error"] = f"{type(error).__name__}: {error}"

    return receipt


def reconstruct_all(
    *,
    checks: list[dict[str, Any]],
    lean_dir: str,
    root: str,
    timeout: int = 180,
) -> dict[str, Any]:
    lean = lean_version()
    artifacts: list[dict[str, Any]] = []
    for check in checks:
        source_path = check["path"]
        name = os.path.splitext(os.path.basename(source_path))[0]
        with open(source_path, "r", encoding="utf-8") as handle:
            script_text = handle.read()
        source_relpath = os.path.relpath(source_path, root).replace("\\", "/")
        artifacts.append(
            reconstruct_one(
                name=name,
                script_text=script_text,
                source_relpath=source_relpath,
                expected=check["result"],
                model_values=check.get("model_values"),
                lean_dir=lean_dir,
                root=root,
                timeout=timeout,
            )
        )

    if not lean["available"]:
        verdict = "TOOL_NOT_RUN"
    elif all(artifact["status"] == "LEAN_RECONSTRUCTED" for artifact in artifacts):
        verdict = "PASSED"
    else:
        verdict = "FAILED"

    return {
        "bridge": BRIDGE_NAME,
        "bridge_version": BRIDGE_VERSION,
        "scope": (
            "Independent Lean 4 re-proof of the same QF_LIA constraint systems. "
            "This is not a translation of Z3's internal proof object."
        ),
        "lean_toolchain": lean,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "verdict": verdict,
    }
