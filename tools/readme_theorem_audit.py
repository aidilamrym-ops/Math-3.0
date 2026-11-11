#!/usr/bin/env python3
"""Audit theorem/definition names cited by README.MD.

The compile audit proves that cited *files* type-check.  It does not prove that a
name the README mentions (`spectral_gravity_stable`, `cantor_no_surjection`, ...)
actually exists in that file's source.  This tool closes that gap cheaply:

  1. extract backticked snake_case identifiers from README.MD;
  2. index every `theorem|lemma|def|abbrev|structure|inductive|class` name in the
     Lean corpus;
  3. report cited identifiers that have no declaration anywhere.

No Lean process is started; this is pure text analysis.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
README = ROOT / "README.MD"
REPORTS = ROOT / "reports"

SURFACES = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|partial\s+)*"
    r"(?:theorem|lemma|def|abbrev|structure|inductive|class|instance)\s+"
    r"([A-Za-z_][A-Za-z0-9_'.]*)",
    re.MULTILINE,
)

# Names from README prose that are not Lean declarations.
IGNORE = {
    "true", "false", "sorry", "admit", "exit", "manifest", "json", "lean", "mathlib",
    "python", "lake", "lean4", "z3", "qf_lia", "qf_nra", "unsat", "sat", "sha",
    "gpl", "cc", "by", "orcid", "doi", "github", "make", "gate", "tools",
    # Tactics, attributes and trust tokens cited as scanned terms, not declarations.
    "norm_num", "interval_cases", "native_decide", "implemented_by", "decide",
    "simp", "simp_all", "omega", "ring", "linarith", "nlinarith", "rfl", "exact",
    "apply", "rw", "aesop", "positivity", "fin_cases", "constructor", "induction",
    "cases", "unfold", "extern", "opaque", "axiom", "constant", "partial_def",
    "sorry_ax", "admit", "partial",
}

# Phrasings that mark an identifier as deliberately non-existent.
NEGATIVE_MARKERS = (
    "do not exist",
    "does not exist",
    "not exist in the module",
    "no longer exists",
    "was removed",
    "were removed",
    "is false",
    "are false",
    "is refuted",
    "are refuted",
    "not proved",
    "not proven",
)

CODE_SUFFIXES = (".lean", ".py", ".json", ".md", ".txt", ".smt2", ".toml", ".sh", ".yml", ".yaml")


def index_declarations() -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for surface in SURFACES:
        if not surface.exists():
            continue
        for path in surface.rglob("*.lean"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            for name in DECL_RE.findall(text):
                index.setdefault(name, []).append(rel)
    return index


def cite_candidates() -> list[str]:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()
    names: set[str] = set()
    for line in lines:
        lowered = line.lower()
        negative = any(marker in lowered for marker in NEGATIVE_MARKERS)
        for tok in re.findall(r"`([^`\n]{2,80})`", line):
            tok = tok.strip()
            if tok.lower().endswith(CODE_SUFFIXES):
                continue
            if "/" in tok or "\\" in tok or " " in tok:
                continue
            # Lean-ish identifier: snake_case or dotted, at least one underscore or
            # a dotted namespace, and no markdown/HTML noise.
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", tok):
                continue
            if tok.lower() in IGNORE:
                continue
            if not ("_" in tok or "." in tok):
                continue
            if negative:
                continue
            names.add(tok)
    return sorted(names)


def main() -> int:
    index = index_declarations()
    cited = cite_candidates()
    found = {n: index[n] for n in cited if n in index}
    missing = [n for n in cited if n not in index]

    report = {
        "cited_identifiers": len(cited),
        "resolved": len(found),
        "missing": len(missing),
        "missing_names": missing,
        "resolved_map": found,
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "readme_theorem_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# README Theorem-Name Audit",
        "",
        f"- Lean declarations indexed: **{sum(len(v) for v in index.values())}** "
        f"(unique names: {len(index)})",
        f"- Backticked identifiers cited by README: **{len(cited)}**",
        f"- Resolved to a declaration: **{len(found)}**",
        f"- Unresolved: **{len(missing)}**",
        "",
    ]
    if missing:
        md += ["## Unresolved identifiers", "", "| Identifier | Note |", "|---|---|"]
        for name in missing:
            md.append(f"| `{name}` | no `theorem`/`lemma`/`def` declaration found |")
    else:
        md.append("Every cited identifier resolves to a Lean declaration.")
    (REPORTS / "readme_theorem_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"cited={len(cited)} resolved={len(found)} missing={len(missing)}")
    for name in missing:
        print(f"MISSING: {name}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
