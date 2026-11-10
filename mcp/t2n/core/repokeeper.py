#!/usr/bin/env python3
"""
Math 3.0 repository ledger keeper.

Two modes:

  python mcp/t2n/core/repokeeper.py            # reseal: rebuild manifest.json
  python mcp/t2n/core/repokeeper.py --verify   # verify: fail-closed comparison

Canonical digest: SHA-256 over file bytes with CRLF collapsed to LF. This is
the historical Math 3.0 sealing convention and is kept for continuity.

Scope: the ledger is a filesystem snapshot of the repository, excluding only
  * VCS metadata, Python bytecode and build caches:
    .git, __pycache__, *.pyc, any .lake directory
  * staging datasets:                staging/
  * solver scratch output:           mcp/out/
  * the ledger itself:               manifest.json
  * the seal statement:              README.MD  (holds manifest digest; checked
                                                semantically by --verify)
`lean/.lake` holds ~6.7 GB of generated Mathlib/toolchain build artifacts that
are not tracked by git. Pinning them made every fresh clone fail verification
and inflated the manifest to 25 MB, so build caches are excluded. The exclusion
rules match path components exactly; they are never substring matches.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time

EXCLUDED_DIR_NAMES = {".git", "__pycache__", "staging", ".lake"}
EXCLUDED_REL_PREFIXES = {
    os.path.normcase(os.path.join("mcp", "out")),
}
SELF_NAME = "manifest.json"
# README carries the seal digest of manifest.json, so pinning it would be
# circular. It is excluded here and checked semantically in verify() instead.
README_NAME = "README.MD"
UNPINNED_NAMES = {SELF_NAME, README_NAME}


def repo_root() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


def canonical_sha256(filepath: str, chunk: int = 1 << 20) -> str:
    """SHA-256 with CRLF collapsed to LF, streamed to bound memory use."""
    hasher = hashlib.sha256()
    carry = b""
    with open(filepath, "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            block = carry + block
            carry = b""
            if block.endswith(b"\r"):
                carry = b"\r"
                block = block[:-1]
            hasher.update(block.replace(b"\r\n", b"\n"))
    if carry:
        hasher.update(carry)
    return hasher.hexdigest()


def is_excluded_dir(path: str, root: str) -> bool:
    name = os.path.basename(path)
    if name in EXCLUDED_DIR_NAMES:
        return True
    rel = os.path.normcase(os.path.relpath(path, root))
    return any(rel == prefix or rel.startswith(prefix + os.sep) for prefix in EXCLUDED_REL_PREFIXES)


def scan(root: str) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if not is_excluded_dir(os.path.join(dirpath, name), root)
        ]
        for filename in filenames:
            if filename in UNPINNED_NAMES or filename.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, filename)
            if not os.path.isfile(full):
                continue
            manifest[os.path.relpath(full, root)] = canonical_sha256(full)
    return manifest


def atomic_write_json(path: str, payload: dict[str, str]) -> None:
    directory = os.path.dirname(path)
    fd, temp_path = tempfile.mkstemp(prefix=".manifest.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


README_NAME = "README.MD"
ROW_PATTERNS = (
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=\s+rows\b)"), "{rows:,}"),
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=\s+files\s+pinned\b)"), "{rows:,}"),
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=-row\b)"), "{rows:,}"),
)
DIGEST_LINE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")


def manifest_digest(path: str) -> str:
    return canonical_sha256(path)


def sync_readme(root: str, rows: int) -> None:
    """Rewrite README row counts and seal digest from ground truth."""
    path = os.path.join(root, README_NAME)
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    digest = manifest_digest(os.path.join(root, SELF_NAME))
    updated = text
    for pattern, template in ROW_PATTERNS:
        updated = pattern.sub(template.format(rows=rows), updated)
    updated = DIGEST_LINE.sub(digest, updated)
    if updated != text:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
        print(f"README synced: {rows:,} rows, seal {digest[:16]}...")


def check_readme(root: str, rows: int) -> list[str]:
    """Return README seal mismatches; empty list means consistent."""
    path = os.path.join(root, README_NAME)
    if not os.path.isfile(path):
        return [f"{README_NAME} missing"]
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    digest = manifest_digest(os.path.join(root, SELF_NAME))
    problems: list[str] = []
    if f"{rows:,} rows" not in text and f"{rows:,}-row" not in text:
        problems.append(f"row count {rows:,} not stated")
    if digest not in text:
        problems.append(f"seal {digest[:16]}... not stated")
    return problems


def reseal(root: str) -> int:
    started = time.perf_counter()
    manifest = scan(root)
    atomic_write_json(os.path.join(root, SELF_NAME), manifest)
    print(
        f"SEALED: manifest.json rewritten with {len(manifest)} rows "
        f"in {time.perf_counter() - started:.1f}s"
    )
    sync_readme(root, len(manifest))
    return 0


def verify(root: str) -> int:
    manifest_path = os.path.join(root, SELF_NAME)
    with open(manifest_path, "r", encoding="utf-8") as handle:
        recorded = json.load(handle)
    if not isinstance(recorded, dict):
        print("FAIL: manifest.json is not a JSON object")
        return 2

    missing: list[str] = []
    mismatched: list[str] = []
    checked = 0
    for key, expected in recorded.items():
        path = os.path.join(root, key)
        if not os.path.isfile(path):
            missing.append(key)
            continue
        checked += 1
        if canonical_sha256(path) != expected:
            mismatched.append(key)

    current = scan(root)
    recorded_keys = {os.path.normcase(os.path.normpath(k)) for k in recorded}
    extra = [
        key
        for key in current
        if os.path.normcase(os.path.normpath(key)) not in recorded_keys
    ]

    print(f"checked:   {checked}")
    print(f"missing:   {len(missing)}")
    print(f"mismatch:  {len(mismatched)}")
    print(f"unpinned:  {len(extra)}")
    for label, items in (("MISSING", missing), ("MISMATCH", mismatched), ("UNPINNED", extra)):
        for item in items[:20]:
            print(f"  {label}: {item}")
    readme_problems = check_readme(root, len(recorded))
    print(f"readme:    {'OK' if not readme_problems else 'STALE'}")
    for problem in readme_problems:
        print(f"  README: {problem}")
    ok = not (missing or mismatched or extra or readme_problems)
    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    root = repo_root()
    if not os.path.isdir(root):
        print("FATAL: repository root not found")
        return 2
    if "--verify" in argv[1:]:
        return verify(root)
    return reseal(root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
