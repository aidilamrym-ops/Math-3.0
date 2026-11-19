#!/usr/bin/env python3
"""Regression tests for the Unicode hypothesis lexer of the substantiveness gate.

The mutation gate must recognize divisibility (``∣`` and ``∤``), membership,
comparison and ``Nat.Coprime`` hypotheses and replace exactly one hypothesis
with ``True``. Historically the ASCII-only binder lexer silently skipped
divisibility hypotheses, so mutants survived without being compiled. These
tests pin the Unicode-aware behavior.

Usage:
  python tools/omega_audit/mutation_parser_selftest.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "omega_audit"))

import substantiveness_gate as sg  # noqa: E402

FIXTURE = """import Mathlib.Tactic

namespace ParserSelftest

theorem div_positive (n : ℕ) (hdiv : 2 ∣ n) : True := by trivial

theorem div_negative (n : ℕ) (hndiv : 2 ∤ n) : True := by trivial

theorem mem_hyp (n : ℕ) (hset : n ∈ [1, 2]) : True := by trivial

theorem coprime_hyp (a b : ℕ) (hcop : Nat.Coprime a b) : True := by trivial

theorem lt_hyp (n : ℕ) (hn : 0 < n) : True := by trivial

theorem no_hyp (n : ℕ) : True := by trivial

end ParserSelftest
"""

EXPECTED_TYPES = {
    "div_positive": ("hdiv", "2 ∣ n"),
    "div_negative": ("hndiv", "2 ∤ n"),
    "mem_hyp": ("hset", "n ∈ [1, 2]"),
    "coprime_hyp": ("hcop", "Nat.Coprime a b"),
    "lt_hyp": ("hn", "0 < n"),
}


def main() -> int:
    failures = 0
    print("=== MUTATION PARSER SELF-TEST ===")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.lean"
        path.write_text(FIXTURE, encoding="utf-8")
        decls = {d.name: d for d in sg.parse_file(path, "fixture.lean")}

        for name, (hyp, typ) in EXPECTED_TYPES.items():
            d = decls.get(name)
            if d is None:
                print(f"[FAIL] {name}: declaration not parsed")
                failures += 1
                continue
            if d.hyp_names[:1] != [hyp] or d.hyp_types[:1] != [typ]:
                print(
                    f"[FAIL] {name}: expected ({hyp} : {typ}), "
                    f"got {list(zip(d.hyp_names, d.hyp_types))}"
                )
                failures += 1
                continue
            if not sg.is_prop_hypothesis(typ, set()):
                print(f"[FAIL] {name}: `{typ}` not classified as a proposition")
                failures += 1
                continue
            if not sg.mutation_candidate(d, set()):
                print(f"[FAIL] {name}: not selected as a mutation candidate")
                failures += 1
                continue
            result = sg.mutate_first_hypothesis(path, d)
            if result is None:
                print(f"[FAIL] {name}: mutation returned None")
                failures += 1
                continue
            mutated_stmt, _payload = result
            if f"({hyp} : True)" not in mutated_stmt:
                print(f"[FAIL] {name}: mutant body lacks `({hyp} : True)`")
                print("        " + mutated_stmt.replace("\n", " ")[:160])
                failures += 1
                continue
            print(f"[OK] {name}: ({hyp} : {typ}) -> ({hyp} : True)")

        d = decls.get("no_hyp")
        if d is None:
            print("[FAIL] no_hyp: declaration not parsed")
            failures += 1
        elif sg.mutation_candidate(d, set()):
            print("[FAIL] no_hyp: hypothesis-free theorem selected for mutation")
            failures += 1
        else:
            print("[OK] no_hyp: hypothesis-free theorem skipped")

    for typ, expected in (("2 ∣ n", True), ("2 ∤ n", True), ("ℕ", False), ("Bool", False)):
        actual = sg.is_prop_hypothesis(typ, set())
        if actual != expected:
            print(f"[FAIL] is_prop_hypothesis({typ!r}) = {actual}, expected {expected}")
            failures += 1
        else:
            print(f"[OK] is_prop_hypothesis({typ!r}) = {actual}")

    print(f"SELF-TEST RESULT: {'PASS' if failures == 0 else 'FAIL'} ({failures} failures)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
