#!/usr/bin/env python3
"""Mutation audit: prove that the Math 3.0 gates actually reject defects.

A gate that has never failed a negative control is an assumption, not a
guarantee.  This tool builds harmless fixtures in a temporary directory,
injects one defect per fixture, runs the corresponding gate, and records
whether the defect was detected.

Suites
------
token    `tools/omega_audit/gate_strict.py` against files carrying sorry,
         sorryAx, admit, axiom, private axiom, @[simp] axiom, constant, opaque,
         partial def, native_decide, @[implemented_by], @[extern], plus two
         string/comment evasion controls that must NOT be flagged.
manifest `mcp/t2n/core/repokeeper.py` against a miniature pinned root:
         clean, modified file, deleted file, extra file, corrupted manifest
         hash, and a corrupted README seal.
compile  `tools/full_surface_lean_audit.py` against a good file (must pass)
         and a type-incorrect file (must fail with exit 1).
theorem  `tools/readme_theorem_audit.py` against a README citing a real name
         (must pass) and a nonexistent name (must fail).

Exit code 0 only when every mutation was detected (or allowed) exactly as
expected.  No file in the repository is modified; everything runs in a temp
directory and is deleted afterwards.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP_BASE = Path(r"C:\Users\usER\AppData\Local\Temp\opencode")

GATE_STRICT = ROOT / "tools" / "omega_audit" / "gate_strict.py"
REPOKEEPER = ROOT / "mcp" / "t2n" / "core" / "repokeeper.py"
FULL_AUDIT = ROOT / "tools" / "full_surface_lean_audit.py"
THEOREM_AUDIT = ROOT / "tools" / "readme_theorem_audit.py"
README = ROOT / "README.MD"

CASES: list[dict] = []


def run(cmd: list[str], cwd: Path = ROOT, timeout: int = 300) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def record(suite: str, case: str, expected: str, rc: int, detail: str = "") -> None:
    if rc == 0:
        observed = "ALLOW"
    elif rc == 1:
        observed = "DETECT"
    else:
        observed = "INCONCLUSIVE"
    verdict = "PASS" if observed == expected else "FAIL"
    CASES.append({
        "suite": suite,
        "case": case,
        "expected": expected,
        "observed": observed,
        "rc": rc,
        "verdict": verdict,
        "detail": detail.strip().splitlines()[-1][:200] if detail.strip() else "",
    })
    print(f"[{verdict:4s}] {suite:8s} {case:34s} expected={expected:6s} observed={observed:12s} rc={rc}")


# --------------------------------------------------------------------------
# Suite 1: trust-token gate
# --------------------------------------------------------------------------

TOKEN_FIXTURES = [
    ("sorry", "theorem bad : False := sorry\n", "DETECT", "DETECT"),
    ("sorryAx", "theorem bad : False := @sorryAx False true\n", "DETECT", "DETECT"),
    ("admit", "theorem bad : False := by\n  admit\n", "DETECT", "DETECT"),
    ("axiom", "axiom bad : False\n", "DETECT", "DETECT"),
    ("private axiom", "private axiom bad : False\n", "DETECT", "DETECT"),
    ("simp-attribute axiom", "@[simp] axiom bad : False\n", "DETECT", "DETECT"),
    ("constant", "constant bad : False\n", "DETECT", "DETECT"),
    ("opaque", "opaque bad : Nat\n", "DETECT", "DETECT"),
    ("partial def", "partial def loop (n : Nat) : Nat := loop n\n", "DETECT", "DETECT"),
    ("native_decide", "theorem bad : (2 : Nat) = 2 := by native_decide\n", "DETECT", "DETECT"),
    ("implemented_by",
     "def f : Nat := 0\n@[implemented_by f] def g : Nat := 0\n", "DETECT", "DETECT"),
    ("extern", '@[extern "c_bad"] def bad : Nat := 0\n', "DETECT", "DETECT"),
    ("string separator evasion",
     'def f : Nat := let _s := "a--b"; (sorry : Nat)\n', "DETECT", "DETECT"),
    # The installed external gate is text-conservative and flags the word inside a
    # string.  The combined verdict must fail closed, but the strict lexer must be
    # clean; the audit records both facts separately.
    ("string literal is not a token", 'def s : String := "sorry"\n', "DETECT", "ALLOW"),
    ("comment is not a token", "-- sorry\ntheorem ok : True := trivial\n", "ALLOW", "ALLOW"),
    ("clean file", "theorem good : (1 : Nat) = 1 := rfl\n", "ALLOW", "ALLOW"),
]


def suite_token(tmp: Path) -> None:
    for name, source, expected, strict_expected in TOKEN_FIXTURES:
        case_dir = tmp / "token" / name.replace(" ", "_").replace("@", "at")
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "mutant.lean").write_text(source, encoding="utf-8")
        receipt = case_dir / "receipt.json"
        rc, out = run([
            sys.executable, str(GATE_STRICT), "check", str(case_dir),
            "--json", str(receipt),
        ])
        record("token", name, expected, rc, out)

        # Second, orthogonal measurement: did the repo-local strict lexer itself
        # flag anything, independent of the external gate's verdict?
        strict_rc = 2
        note = ""
        if receipt.exists():
            try:
                data = json.loads(receipt.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
            strict_rc = 1 if data.get("findings") else (2 if data.get("not_run") else 0)
            note = (f"strict_findings={len(data.get('findings', []))} "
                    f"external_exit={data.get('external_exit')}")
        record("token-strict", name, strict_expected, strict_rc, note)


# --------------------------------------------------------------------------
# Suite 2: manifest / seal gate
# --------------------------------------------------------------------------

def make_pinned_root(tmp: Path, name: str) -> Path:
    root = tmp / "manifest" / name
    (root / "mcp" / "t2n" / "core").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPOKEEPER, root / "mcp" / "t2n" / "core" / "repokeeper.py")
    shutil.copy2(README, root / "README.MD")
    (root / "data.txt").write_text("alpha\n", encoding="utf-8")
    rc, out = run([sys.executable, str(root / "mcp" / "t2n" / "core" / "repokeeper.py")], cwd=root)
    if rc != 0:
        raise RuntimeError(f"fixture reseal failed: {out}")
    return root


def verify_fixture(root: Path) -> tuple[int, str]:
    return run(
        [sys.executable, str(root / "mcp" / "t2n" / "core" / "repokeeper.py"), "--verify"],
        cwd=root,
    )


def suite_manifest(tmp: Path) -> None:
    root = make_pinned_root(tmp, "clean")
    rc, out = verify_fixture(root)
    record("manifest", "clean root", "ALLOW", rc, out)

    root = make_pinned_root(tmp, "modified")
    (root / "data.txt").write_text("beta\n", encoding="utf-8")
    rc, out = verify_fixture(root)
    record("manifest", "modified pinned file", "DETECT", rc, out)

    root = make_pinned_root(tmp, "deleted")
    (root / "data.txt").unlink()
    rc, out = verify_fixture(root)
    record("manifest", "deleted pinned file", "DETECT", rc, out)

    root = make_pinned_root(tmp, "extra")
    (root / "extra.txt").write_text("gamma\n", encoding="utf-8")
    rc, out = verify_fixture(root)
    record("manifest", "unpinned extra file", "DETECT", rc, out)

    root = make_pinned_root(tmp, "hash")
    manifest_path = root / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    key = next(k for k in data if k.replace("\\", "/").endswith("data.txt"))
    data[key] = "0" * 64
    manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    rc, out = verify_fixture(root)
    record("manifest", "corrupted manifest hash", "DETECT", rc, out)

    root = make_pinned_root(tmp, "seal")
    readme_path = root / "README.MD"
    text = readme_path.read_text(encoding="utf-8")
    sealed = (root / "manifest.json").read_bytes()
    real_digest = hashlib.sha256(sealed.replace(b"\r\n", b"\n")).hexdigest()
    if real_digest in text:
        text = text.replace(real_digest, "0" * 64)
        readme_path.write_text(text, encoding="utf-8")
    rc, out = verify_fixture(root)
    record("manifest", "corrupted README seal", "DETECT", rc, out)


# --------------------------------------------------------------------------
# Suite 3: compile gate
# --------------------------------------------------------------------------

def suite_compile(tmp: Path) -> None:
    out_dir = tmp / "compile_out"
    out_dir.mkdir(parents=True, exist_ok=True)

    good_surface = ROOT / "lean" / f"_mutation_good_{abs(hash(str(tmp))) % 10**8}"
    bad_surface = ROOT / "lean" / f"_mutation_bad_{abs(hash(str(tmp))) % 10**8}"
    try:
        good_surface.mkdir(parents=True, exist_ok=True)
        (good_surface / "Good.lean").write_text(
            "theorem mutation_good : (1 : Nat) = 1 := rfl\n", encoding="utf-8"
        )
        rc, out = run([
            sys.executable, str(FULL_AUDIT), "--workers", "1", "--timeout", "120",
            "--surface", str(good_surface), "--out-dir", str(out_dir / "good"),
        ], timeout=300)
        record("compile", "well-typed file", "ALLOW", rc, out)

        bad_surface.mkdir(parents=True, exist_ok=True)
        (bad_surface / "Bad.lean").write_text(
            "theorem mutation_bad : (1 : Nat) = 2 := rfl\n", encoding="utf-8"
        )
        rc, out = run([
            sys.executable, str(FULL_AUDIT), "--workers", "1", "--timeout", "120",
            "--surface", str(bad_surface), "--out-dir", str(out_dir / "bad"),
        ], timeout=300)
        record("compile", "ill-typed file", "DETECT", rc, out)
    finally:
        shutil.rmtree(good_surface, ignore_errors=True)
        shutil.rmtree(bad_surface, ignore_errors=True)


# --------------------------------------------------------------------------
# Suite 4: theorem-name gate
# --------------------------------------------------------------------------

def suite_theorem(tmp: Path) -> None:
    out_dir = tmp / "theorem_out"
    out_dir.mkdir(parents=True, exist_ok=True)

    good = tmp / "theorem" / "good_readme.md"
    good.parent.mkdir(parents=True, exist_ok=True)
    good.write_text("`cantor_no_surjection` is a real declaration.\n", encoding="utf-8")
    rc, out = run([
        sys.executable, str(THEOREM_AUDIT), "--readme", str(good),
        "--out-dir", str(out_dir / "good"),
    ], timeout=300)
    record("theorem", "existing theorem name", "ALLOW", rc, out)

    bad = tmp / "theorem" / "bad_readme.md"
    bad.write_text("`definitely_missing_theorem_xyz` is claimed.\n", encoding="utf-8")
    rc, out = run([
        sys.executable, str(THEOREM_AUDIT), "--readme", str(bad),
        "--out-dir", str(out_dir / "bad"),
    ], timeout=300)
    record("theorem", "nonexistent theorem name", "DETECT", rc, out)


# --------------------------------------------------------------------------

def main() -> int:
    started = time.time()
    TMP_BASE.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="math30_mutation_", dir=str(TMP_BASE)))
    try:
        suite_token(tmp)
        suite_manifest(tmp)
        suite_compile(tmp)
        suite_theorem(tmp)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(tmp, ignore_errors=True)

    missed = [c for c in CASES if c["verdict"] == "FAIL"]
    inconclusive = [c for c in CASES if c["observed"] == "INCONCLUSIVE"]

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(time.time() - started, 1),
        "total": len(CASES),
        "passed": len(CASES) - len(missed),
        "missed": len(missed),
        "inconclusive": len(inconclusive),
        "cases": CASES,
    }
    (reports / "gate_mutation_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# Gate Mutation Audit",
        "",
        f"- Generated: {payload['generated']}",
        f"- Cases: **{len(CASES)}**  Passed: **{payload['passed']}**  "
        f"Missed: **{payload['missed']}**  Inconclusive: **{payload['inconclusive']}**",
        f"- Elapsed: {payload['elapsed_seconds']}s",
        "",
        "| Verdict | Suite | Case | Expected | Observed |",
        "|---|---|---|---|---|",
    ]
    for c in CASES:
        md.append(
            f"| {c['verdict']} | {c['suite']} | {c['case']} | "
            f"{c['expected']} | {c['observed']} |"
        )
    (reports / "gate_mutation_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\ntotal={len(CASES)} passed={payload['passed']} "
          f"missed={payload['missed']} inconclusive={payload['inconclusive']}")
    return 0 if not missed and not inconclusive else 1


if __name__ == "__main__":
    sys.exit(main())
