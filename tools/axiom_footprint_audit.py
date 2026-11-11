#!/usr/bin/env python3
"""Axiom footprint audit: what does each theorem actually rest on?

Token gates look for `sorry`, `axiom`, and friends in the *source text*.  They do
not see the axiom set that the kernel attaches to a compiled theorem.  This tool
does:

  1. parse every `theorem`/`lemma` declaration (namespace-aware) in the Lean
     corpus;
  2. build one probe file per source file: the original source plus a
     `#print axioms <fully.qualified.name>` command per declaration;
  3. compile each probe with `lake env lean` (at most two at a time);
  4. classify every axiom set against the allowlist
     `[propext, Classical.choice, Quot.sound]`.

Anything else — `sorryAx`, `Lean.trustCompiler`, or a custom axiom — is a
violation.  Probes live in a temporary directory; the repository is not touched.

Usage:
    python tools/axiom_footprint_audit.py [--workers 2] [--timeout 240]
                                          [--surface DIR ...] [--out-dir DIR]
                                          [--only PATH_SUBSTRING]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean"
DEFAULT_OUT = ROOT / "reports"
TMP_BASE = Path(r"C:\Users\usER\AppData\Local\Temp\opencode")

DEFAULT_SURFACES = [
    LEAN_ROOT / "spec_v4",
    ROOT / "Math30Kernel",
    ROOT / "Math30Interfaces",
]

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:protected|noncomputable|unsafe)\s+)*"
    r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)"
)
PRIVATE_PREFIX = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)*private\b")
NS_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)")
SEC_RE = re.compile(r"^\s*section\b")
END_RE = re.compile(r"^\s*end\b(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$")


def blank_comments(text: str) -> str:
    """Blank comments and string literals so structure parsing ignores prose."""
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


def collect_declarations(text: str) -> list[str]:
    """Return fully qualified theorem/lemma names, namespace-aware."""
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
                    kind, current = stack.pop()
                    if kind == "ns" and current == name:
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


def parse_axioms(output: str, name: str) -> tuple[list[str] | None, str]:
    """Return (axioms, status) where status is CLEAN / AXIOms / MISSING."""
    clean_line = f"'{name}' does not depend on any axioms"
    if clean_line in output:
        return [], "CLEAN"
    marker = f"'{name}' depends on axioms:"
    index = output.find(marker)
    if index == -1:
        return None, "MISSING"
    start = output.find("[", index)
    end = output.find("]", start)
    if start == -1 or end == -1:
        return None, "MISSING"
    body = output[start + 1:end]
    axioms = [part.strip() for part in body.split(",") if part.strip()]
    return axioms, "AXIOMS"


def probe_one(path: Path, tmp: Path, timeout: int) -> dict:
    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"file": str(path), "status": "UNREADABLE", "error": str(exc), "theorems": []}

    names = collect_declarations(original)
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if not names:
        return {"file": rel, "status": "NO_THEOREMS", "theorems": [], "error": ""}

    prints = "\n".join(f"#print axioms {name}" for name in names)
    probe = tmp / (re.sub(r"[^A-Za-z0-9_.-]+", "_", rel) + ".probe.lean")
    probe.write_text(original + "\n\n" + prints + "\n", encoding="utf-8")

    started = time.time()
    try:
        proc = subprocess.run(
            ["lake", "env", "lean", str(probe)],
            cwd=LEAN_ROOT,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "file": rel, "status": "TIMEOUT", "theorems": [],
            "error": f"exceeded {timeout}s", "seconds": round(time.time() - started, 2),
        }
    finally:
        probe.unlink(missing_ok=True)

    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    rows: list[dict] = []
    violations: list[dict] = []
    inconclusive: list[dict] = []

    for name in names:
        axioms, status = parse_axioms(output, name)
        row = {"name": name, "status": status, "axioms": axioms or []}
        rows.append(row)
        if status == "MISSING":
            inconclusive.append(row)
        elif status == "AXIOMS":
            illegal = [a for a in (axioms or []) if a not in ALLOWED_AXIOMS]
            if illegal:
                violations.append({"name": name, "file": rel, "axioms": axioms, "illegal": illegal})

    error = ""
    if proc.returncode != 0:
        for line in output.splitlines():
            if "error" in line:
                error = line.strip()[:300]
                break
        if not error:
            error = (output.strip().splitlines() or [""])[-1][:300]

    return {
        "file": rel,
        "status": "PROBED",
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 2),
        "theorems": rows,
        "violations": violations,
        "inconclusive": inconclusive,
        "error": error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--surface", action="append", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--only", default=None)
    args = parser.parse_args()

    workers = max(1, min(2, args.workers))
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    surfaces = [Path(s).resolve() for s in args.surface] if args.surface else DEFAULT_SURFACES

    files: list[Path] = []
    for surface in surfaces:
        if surface.exists():
            files.extend(sorted(surface.rglob("*.lean")))
    files = sorted(set(f.resolve() for f in files))
    if args.only:
        needle = args.only.lower()
        files = [f for f in files if needle in str(f).lower()]

    TMP_BASE.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="math30_axioms_", dir=str(TMP_BASE)))
    started = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(probe_one, f, tmp, args.timeout) for f in files]
            results = [fut.result() for fut in concurrent.futures.as_completed(futures)]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    results.sort(key=lambda r: r["file"])

    probed = [r for r in results if r["status"] == "PROBED"]
    theorem_rows = [t for r in probed for t in r["theorems"]]
    violations = [v for r in probed for v in r["violations"]]
    inconclusive = [v for r in probed for v in r["inconclusive"]]
    failed = [r for r in results if r["status"] in ("TIMEOUT", "UNREADABLE")]
    compile_errors = [r for r in probed if r.get("rc") not in (0, None)]

    axiom_usage: dict[str, int] = {}
    for row in theorem_rows:
        for axiom in row["axioms"]:
            axiom_usage[axiom] = axiom_usage.get(axiom, 0) + 1

    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(time.time() - started, 1),
        "files_scanned": len(files),
        "files_with_theorems": len(probed),
        "theorems_total": len(theorem_rows),
        "allowlist": sorted(ALLOWED_AXIOMS),
        "axiom_usage": dict(sorted(axiom_usage.items(), key=lambda kv: -kv[1])),
        "violations": violations,
        "inconclusive": inconclusive,
        "compile_errors": [
            {"file": r["file"], "rc": r.get("rc"), "error": r.get("error")} for r in compile_errors
        ],
        "failed": [{"file": r["file"], "status": r["status"], "error": r.get("error")} for r in failed],
        "results": results,
    }
    (out_dir / "axiom_footprint_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# Axiom Footprint Audit",
        "",
        f"- Generated: {payload['generated']}",
        f"- Files scanned: **{payload['files_scanned']}**",
        f"- Files with theorems: **{payload['files_with_theorems']}**",
        f"- Theorem/lemma declarations probed: **{payload['theorems_total']}**",
        f"- Allowlist: `{sorted(ALLOWED_AXIOMS)}`",
        f"- Violations: **{len(violations)}**",
        f"- Inconclusive: **{len(inconclusive)}**",
        f"- Probe compile errors: **{len(compile_errors)}**",
        f"- Elapsed: {payload['elapsed_seconds']}s",
        "",
        "## Axiom usage",
        "",
        "| Axiom | Theorems |",
        "|---|---|",
    ]
    for axiom, count in payload["axiom_usage"].items():
        md.append(f"| `{axiom}` | {count} |")

    md += ["", "## Violations", ""]
    if violations:
        md += ["| Theorem | File | Illegal | All axioms |", "|---|---|---|---|"]
        for v in violations:
            md.append(
                f"| `{v['name']}` | `{v['file']}` | `{v['illegal']}` | `{v['axioms']}` |"
            )
    else:
        md.append("None. Every probed theorem uses only the allowlisted axioms.")

    md += ["", "## Inconclusive", ""]
    if inconclusive:
        md += ["| Theorem | File |", "|---|---|"]
        for v in inconclusive:
            md.append(f"| `{v['name']}` | (see JSON) |")
    else:
        md.append("None. Every declaration produced a `#print axioms` answer.")

    (out_dir / "axiom_footprint_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"files={payload['files_scanned']} with_theorems={payload['files_with_theorems']} "
          f"theorems={payload['theorems_total']}")
    print(f"violations={len(violations)} inconclusive={len(inconclusive)} "
          f"compile_errors={len(compile_errors)} failed={len(failed)}")
    for v in violations:
        print(f"VIOLATION: {v['name']} :: {v['illegal']}")
    for r in compile_errors:
        print(f"COMPILE: {r['file']} :: {r.get('error')}")

    ok = not violations and not compile_errors and not failed and not inconclusive
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
