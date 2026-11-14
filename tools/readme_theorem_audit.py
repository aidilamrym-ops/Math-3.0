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

Usage:
    python tools/readme_theorem_audit.py [--readme PATH] [--surface DIR ...]
                                         [--out-dir DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
DEFAULT_README = ROOT / "README.MD"
DEFAULT_OUT = ROOT / "reports"

DEFAULT_SURFACES = [
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
    "sorry_ax", "partial",
    # Build-system paths, not Lean declarations.
    "__pycache__", "pycache", "pyc",
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
AUTO_FACTS_RE = re.compile(
    r"<!-- AUTO-FACTS:START -->.*?<!-- AUTO-FACTS:END -->", re.DOTALL
)


def semantic_readme_digest(text: str) -> str:
    """README digest with the generated auto-facts block removed.

    The injector writes that block into README.MD, so including it would make
    every receipt stale the moment the facts are injected.  Only authored prose
    is hashed.
    """
    semantic = AUTO_FACTS_RE.sub("", text)
    # The manifest seal is also generated (repokeeper.sync_readme rewrites it),
    # so hashing it would make a fresh audit stale after every reseal.
    semantic = re.sub(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", "<sha256>", semantic)
    return hashlib.sha256(semantic.encode("utf-8")).hexdigest()


def build_index(surfaces: list[Path]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for surface in surfaces:
        if not surface.exists():
            continue
        for path in surface.rglob("*.lean"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            try:
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                rel = str(path).replace("\\", "/")
            for name in DECL_RE.findall(text):
                index.setdefault(name, []).append(rel)
    return index


def negative_tail(line: str, end: int, span: int = 180) -> bool:
    """True iff a negation marker follows the citation in the same clause.

    A line-wide check is too coarse: "the factor-4 test is false ... is
    machine-checked by `dsitni_half_threshold_refuted`" contains a negation but
    cites a real theorem *after* it.  Only the text after the closing backtick,
    up to the next sentence or clause boundary, decides whether the citation is
    a statement of non-existence.
    """
    tail = line[end:end + span].lower()
    for separator in (". ", "; ", " — "):
        index = tail.find(separator)
        if index != -1:
            tail = tail[:index]
    return any(marker in tail for marker in NEGATIVE_MARKERS)


def cite_candidates(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    names: set[str] = set()
    for line in text.splitlines():
        for match in re.finditer(r"`([^`\n]{2,80})`", line):
            tok = match.group(1).strip()
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
            if negative_tail(line, match.end()):
                continue
            names.add(tok)
    return sorted(names)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readme", default=None)
    parser.add_argument("--surface", action="append", default=None)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    readme = Path(args.readme).resolve() if args.readme else DEFAULT_README
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_OUT
    surfaces = [Path(s).resolve() for s in args.surface] if args.surface else DEFAULT_SURFACES
    out_dir.mkdir(parents=True, exist_ok=True)

    index = build_index(surfaces)
    cited = cite_candidates(readme)
    found = {n: index[n] for n in cited if n in index}
    missing = [n for n in cited if n not in index]

    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "readme": str(readme),
        "readme_semantic_sha256": semantic_readme_digest(
            readme.read_text(encoding="utf-8")
        ),
        "surfaces": [str(s) for s in surfaces],
        "cited_identifiers": len(cited),
        "resolved": len(found),
        "missing": len(missing),
        "missing_names": missing,
        "resolved_map": found,
    }
    (out_dir / "readme_theorem_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# README Theorem-Name Audit",
        "",
        f"- README: `{readme}`",
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
    (out_dir / "readme_theorem_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"cited={len(cited)} resolved={len(found)} missing={len(missing)}")
    for name in missing:
        print(f"MISSING: {name}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
