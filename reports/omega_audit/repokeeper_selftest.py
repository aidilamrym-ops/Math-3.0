"""Adversarial self-test for mcp/t2n/core/repokeeper.py (no repo mutation).

Run: python reports/omega_audit/repokeeper_selftest.py
Exit 0 only if every control behaves as specified.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEEPER = ROOT / "mcp" / "t2n" / "core" / "repokeeper.py"
TMP = Path(tempfile.mkdtemp(prefix="math30_repokeeper_"))
FAILS: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))
    if not condition:
        FAILS.append(name)


def make_root() -> Path:
    root = TMP / f"case_{len(FAILS)}_{len(list(TMP.iterdir()))}"
    (root / "mcp" / "t2n" / "core").mkdir(parents=True, exist_ok=True)
    shutil.copy2(KEEPER, root / "mcp" / "t2n" / "core" / "repokeeper.py")
    (root / "data.txt").write_text("alpha\n", encoding="utf-8")
    (root / "nested").mkdir()
    (root / "nested" / "README.MD").write_text("nested readme\n", encoding="utf-8")
    (root / "README.MD").write_text(
        "# Test\n\nManifest Rows: 1,000 files pinned\n\n"
        "Definitive Verified Ledger Signature (SHA-256):\n"
        "```\n" + "0" * 64 + "\n```\n\n"
        "Unrelated certificate digest: " + "a" * 64 + "\n",
        encoding="utf-8",
    )
    return root


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "mcp" / "t2n" / "core" / "repokeeper.py"), *args],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def manifest(root: Path) -> dict:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


try:
    root = make_root()
    check("unknown flag fails closed", run(root, "--verfiy").returncode == 2)
    check("typo did not create manifest", not (root / "manifest.json").exists())

    check("reseal exits 0", run(root).returncode == 0)
    data = manifest(root)
    check("keys are POSIX", all("\\" not in k for k in data), str(list(data)[:3]))
    check("nested README pinned", "nested/README.MD" in data)
    check("root README excluded", "README.MD" not in data)
    check("clean verify exits 0", run(root, "--verify").returncode == 0)

    readme = (root / "README.MD").read_text(encoding="utf-8")
    check("unrelated digest preserved", "a" * 64 in readme)
    check("seal digest updated", "0" * 64 not in readme)
    check("row count updated", "3 rows" in readme or "3 files pinned" in readme, readme.splitlines()[2])

    # Legacy Windows receipt must still verify after a POSIX rewrite. Rewriting
    # the ledger changes its digest, so the README seal must be resynchronised
    # to that legacy artifact before the verification control is meaningful.
    import hashlib
    import re

    legacy = {k.replace("/", "\\"): v for k, v in data.items()}
    legacy_path = root / "manifest.json"
    legacy_path.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
    legacy_digest = hashlib.sha256(
        legacy_path.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    readme_path = root / "README.MD"
    text = readme_path.read_text(encoding="utf-8")
    text = re.sub(
        r"(?m)^[0-9a-f]{64}$", legacy_digest, text, count=1
    )
    readme_path.write_text(text, encoding="utf-8")
    check("legacy backslash receipt verifies", run(root, "--verify").returncode == 0)

    # Tampering must be detected, and must be detected through legacy keys too.
    (root / "nested" / "README.MD").write_text("tampered\n", encoding="utf-8")
    check("tampered nested file detected", run(root, "--verify").returncode == 1)

    # Stale seal must be detected.
    run(root)
    lines = (root / "README.MD").read_text(encoding="utf-8").splitlines()
    replaced = False
    for index, line in enumerate(lines):
        context = " ".join(lines[max(0, index - 2):index]).lower()
        if (
            "sha-256" in context
            and len(line.strip()) == 64
            and all(c in "0123456789abcdef" for c in line.strip())
        ):
            lines[index] = "b" * 64
            replaced = True
    check("seal line located for tamper test", replaced)
    (root / "README.MD").write_text("\n".join(lines) + "\n", encoding="utf-8")
    check("stale seal detected", run(root, "--verify").returncode == 1)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failed control(s)")
sys.exit(0 if not FAILS else 1)
