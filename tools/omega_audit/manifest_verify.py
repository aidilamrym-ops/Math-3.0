#!/usr/bin/env python3
"""
Omega audit :: manifest_verify.py

Deterministic integrity verifier for manifest.json.

The repository's sealer (mcp/t2n/core/repokeeper.py) defines the canonical
digest as SHA-256 over file bytes with CRLF collapsed to LF. This verifier
uses exactly that canonicalization so a mismatch here is a real ledger
mismatch, not a line-ending artifact.

Checks, in order:
  1. JSON parses and is a flat mapping {relative_path: sha256_hex}.
  2. Keys are unique after path normalization.
  3. Every recorded file exists on disk.
  4. Every recorded digest matches the canonical file digest, sequentially.
  5. Every non-excluded file on disk is recorded in the manifest.
     Exclusions mirror the sealer: .git, __pycache__, mcp/out, staging, any
     .lake build cache, manifest.json, README.MD, *.pyc. README.MD is excluded
     because it states the manifest digest (pinning it would be circular).
  6. Reports canonical SHA-256 of manifest.json so the README seal can be
     compared against ground truth.

No parallelism. No network access. Writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "manifest.json")

EXCLUDED_DIR_NAMES = {".git", "__pycache__", "staging", ".lake"}
EXCLUDED_DIR_PREFIXES = {
    os.path.normcase(os.path.join(ROOT, "mcp", "out")),
}
SELF_EXCLUDE = {
    os.path.normcase(MANIFEST),
    os.path.normcase(os.path.join(ROOT, "README.MD")),
}


def canonical_sha256(path: str) -> str:
    """SHA-256 with CRLF collapsed to LF (repo sealing convention)."""
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def main() -> int:
    t0 = time.time()
    with open(MANIFEST, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    if not isinstance(manifest, dict):
        print("FATAL: manifest is not a JSON object")
        return 2

    entries = len(manifest)
    print(f"[1] manifest parsed: {entries} entries")

    normalized = {}
    dupes = []
    for key, digest in manifest.items():
        nk = os.path.normcase(os.path.normpath(key))
        if nk in normalized:
            dupes.append(key)
        normalized[nk] = (key, digest)
    print(f"[2] unique normalized keys: {len(normalized)} (duplicates: {len(dupes)})")

    missing = []
    mismatched = []
    bad_digest_format = []
    checked = 0

    print("[3/4] verifying existence and canonical SHA-256 for every recorded path...")
    for i, (key, digest) in enumerate(manifest.items(), start=1):
        if not isinstance(digest, str) or len(digest) != 64:
            bad_digest_format.append(key)
            continue
        path = os.path.join(ROOT, key.replace("\\", os.sep))
        if not os.path.isfile(path):
            missing.append(key)
            continue
        actual = canonical_sha256(path)
        checked += 1
        if actual != digest.lower():
            mismatched.append((key, digest, actual))
        if i % 20000 == 0:
            print(f"    ... {i} paths examined")
            sys.stdout.flush()

    print(f"[4] hashes checked: {checked}; mismatched: {len(mismatched)}")

    recorded = {os.path.normcase(os.path.normpath(k)) for k in manifest}
    extra = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        norm_dir = os.path.normcase(dirpath)
        if any(norm_dir.startswith(p) for p in EXCLUDED_DIR_PREFIXES):
            continue
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, name)
            if os.path.normcase(full) in SELF_EXCLUDE:
                continue
            key = os.path.normcase(os.path.normpath(rel(full)))
            if key in recorded:
                continue
            extra.append(rel(full))

    print(f"[5] files on disk not recorded in manifest: {len(extra)}")
    for path in sorted(extra)[:60]:
        print(f"    EXTRA {path}")

    with open(MANIFEST, "rb") as fh:
        manifest_raw_sha = hashlib.sha256(fh.read()).hexdigest()
    manifest_canon_sha = canonical_sha256(MANIFEST)
    print(f"[6] manifest.json SHA-256 (raw)       = {manifest_raw_sha}")
    print(f"    manifest.json SHA-256 (CRLF->LF)   = {manifest_canon_sha}")

    readme_path = os.path.join(ROOT, "README.MD")
    readme_problems = []
    try:
        with open(readme_path, "r", encoding="utf-8") as fh:
            readme_text = fh.read()
    except OSError as error:
        readme_text = ""
        readme_problems.append(f"unreadable: {error}")
    if manifest_canon_sha not in readme_text:
        readme_problems.append("seal digest not stated in README.MD")
    if f"{entries:,} rows" not in readme_text and f"{entries:,}-row" not in readme_text:
        readme_problems.append(f"row count {entries:,} not stated in README.MD")
    print(f"[7] README.MD seal: {'OK' if not readme_problems else 'STALE'}")
    for problem in readme_problems:
        print(f"    README {problem}")
    print(f"    elapsed: {time.time() - t0:.1f}s")

    if bad_digest_format:
        print(f"\nBAD DIGEST FORMAT ({len(bad_digest_format)}):")
        for key in bad_digest_format[:20]:
            print(f"    {key}")
    if missing:
        print(f"\nMISSING ({len(missing)}):")
        for key in missing[:60]:
            print(f"    {key}")
    if mismatched:
        print(f"\nMISMATCHED ({len(mismatched)}):")
        for key, want, got in mismatched[:60]:
            print(f"    {key}\n      recorded {want}\n      actual   {got}")

    # Fail closed on every class of ledger defect. An unpinned file is a
    # completeness failure: it can change without any digest signal, which is
    # exactly the property the ledger is supposed to provide.
    ok = not (
        dupes
        or missing
        or mismatched
        or bad_digest_format
        or extra
        or readme_problems
    )
    print(
        f"\nSUMMARY: recorded={entries} duplicate_keys={len(dupes)} "
        f"missing={len(missing)} mismatched={len(mismatched)} "
        f"bad_digest={len(bad_digest_format)} unpinned={len(extra)} "
        f"readme_stale={len(readme_problems)}"
    )
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
