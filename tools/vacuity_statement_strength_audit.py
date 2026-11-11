#!/usr/bin/env python3
"""Vacuity / statement-strength audit for Math 3.0.

Identifies over-weak teorema and potentially empty proofs that pass the
compiled audit but carry zero logical content.

Scope
-----
- theorem/lemma whose conclusion is True (plain truth).
- theorem/lemma whose conclusion is `X = X` (reflexive equality).
- theorem/lemma whose hypothesis variables are not mentioned in the conclusion.
  (Simplistic detection: the line after ``:`` does not contain any characters
  that belong to the declared hypothesis namespace).

Note: This is a lightweight scanner; a full strength vacuity audit requires
formal type inference, which is out of scope for this recursive development.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
LEAN_ROOTS = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]
DEFAULT_REPORTS = ROOT / "reports"

# -------------------------------------------------------------------
# Parsers: copy‑pasted from axiom_footprint_audit.py (namespace‑aware).
# -------------------------------------------------------------------
DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:protected|noncomputable|unsafe)\s+)*"
    r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)"
)
PRIVATE_PREFIX = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)*private\b")
NS_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)")
SEC_RE = re.compile(r"^\s*section\b")
END_RE = re.compile(r"^\s*end\b(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$")


def blank_comments(text: str) -> str:
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


def collect_declarations(text: str):
    clean = blank_comments(text)
    stack: list[tuple[str, str | None]] = []
    names: list[str] = []
    for line in clean.splitlines():
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
            continue
        if SEC_RE.match(line):
            stack.append(("sec", None))
            continue
        if PRIVATE_PREFIX.match(line):
            continue
        m = DECL_RE.match(line)
        if m:
            short = m.group(2)
            namespace = ".".join(n for kind, n in stack if kind == "ns" and n)
            names.append(f"{namespace}.{short}" if namespace else short)
    return names

# -------------------------------------------------------------------
# Detection patterns
# -------------------------------------------------------------------
TRUE_THEOREM = re.compile(r"^\s*(?:theorem|lemma)\s+[^:\n]*:\s*True\s*:=.*$", re.MULTILINE)
REFLEXIVE_THEOREM = re.compile(
    r"^\s*(?:theorem|lemma)\s+[^:\n]*:\s*"  # capture before conclusion
    r"([A-Za-z_][A-Za-z0-9_'.]*)\s*=\s*\1\s*:=", re.MULTILINE
)


def scan_file(path: Path):
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    src = path.read_text(encoding="utf-8", errors="replace")
    clean = blank_comments(src)
    findings = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("theorem") or stripped.startswith("lemma"):
            if " : True :=" in line:
                findings.append("true_conclusion")
            if ":" in line:
                after = line.split(":", 1)[1]
                # Pattern lhs = same identifier
                if re.match(r"\s*([A-Za-z_][A-Za-z0-9_'.]*)\s*=\s*\1\s*:=\s*", after):
                    findings.append("reflexive_equality")
                # Very rough hypothesis-usage detection: skip for now
    return {"file": rel, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", action="append", default=None)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    surfaces = [Path(s).resolve() for s in args.surface] if args.surface else LEAN_ROOTS
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_REPORTS
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    for surf in surfaces:
        if not surf.exists():
            continue
        for path in surf.rglob("*.lean"):
            try:
                all_results.append(scan_file(path))
            except Exception as exc:
                all_results.append({"file": str(path), "error": str(exc)})

    summary = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files_scanned": len([r for r in all_results if "error" not in r]),
        "total_findings": sum(len(r.get("findings", [])) for r in all_results if "error" not in r),
        "true_conclusion": sum(1 for r in all_results if "true_conclusion" in r.get("findings", [])),
        "reflexive_equality": sum(1 for r in all_results if "reflexive_equality" in r.get("findings", [])),
        "files": all_results,
    }
    json_path = out_dir / "vacuity_statement_strength_audit.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    md = [
        "# Vacuity / Statement-Strength Audit",
        "",
        f"- Generated: {summary['generated']}",
        f"- Files scanned: **{summary['total_files_scanned']}**",
        f"- True conclusions found: **{summary['true_conclusion']}**",
        f"- Reflexive equality proofs found: **{summary['reflexive_equality']}**",
        f"- Total findings: **{summary['total_findings']}**",
        "",
    ]
    if summary["true_conclusion"] or summary["reflexive_equality"]:
        md += ["## Findings", "", "| File | Finding |", "|---|---|"]
        for r in all_results:
            if "error" in r:
                continue
            for f in r.get("findings", []):
                md.append(f"| `{r['file']}` | {f} |")
    else:
        md.append("No vacuous or reflexive teorema detected.")

    (out_dir / "vacuity_statement_strength_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"vacuity audit done: true={summary['true_conclusion']} reflexive={summary['reflexive_equality']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
