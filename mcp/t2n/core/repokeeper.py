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
import posixpath
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
# circular. Both exclusions are root-relative: a nested README.MD elsewhere in
# the tree is a normal file and must still be pinned.
README_NAME = "README.MD"
UNPINNED_ROOT_FILES = {SELF_NAME, README_NAME}


def posix_key(path: str) -> str:
    """Ledger key with forward slashes, independent of the host separator."""
    return path.replace(os.sep, "/")


def resolve_key(root: str, key: str) -> str:
    """Resolve a ledger key on any host.

    New receipts store POSIX keys.  Legacy Windows receipts stored backslashes;
    splitting on both separators keeps those verifiable on Linux as well.
    """
    parts = [p for p in key.replace("\\", "/").split("/") if p not in ("", ".")]
    return os.path.join(root, *parts)


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
            if filename.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, filename)
            if not os.path.isfile(full):
                continue
            rel = posix_key(os.path.relpath(full, root))
            if rel in UNPINNED_ROOT_FILES:
                continue
            manifest[rel] = canonical_sha256(full)
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


ROW_PATTERNS = (
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=\s+rows\b)"), "{rows:,}"),
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=\s+files\s+pinned\b)"), "{rows:,}"),
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?=-row\b)"), "{rows:,}"),
)
DIGEST_LINE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
SEAL_CONTEXT = ("sha-256", "seal", "ledger signature", "manifest")
# Any 64-hex token is a potential certificate hash.  Only tokens on, or directly
# below, a line that identifies itself as the manifest seal may be rewritten.
# The previous implementation replaced *every* 64-hex token in README.MD, which
# would have silently destroyed unrelated certificate digests.
SEAL_LOOKBACK = 2


def manifest_digest(path: str) -> str:
    return canonical_sha256(path)


def _is_seal_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SEAL_CONTEXT)


def seal_digests(text: str) -> list[str]:
    """64-hex tokens that occur in an explicit manifest-seal context."""
    lines = text.splitlines()
    found: list[str] = []
    for index, line in enumerate(lines):
        if not DIGEST_LINE.search(line):
            continue
        context = line
        for back in range(1, SEAL_LOOKBACK + 1):
            if index - back >= 0:
                context += " " + lines[index - back]
        if _is_seal_line(context):
            found.extend(DIGEST_LINE.findall(line))
    return found


def sync_readme(root: str, rows: int) -> None:
    """Rewrite README row counts and manifest seal digest from ground truth."""
    path = os.path.join(root, README_NAME)
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    digest = manifest_digest(os.path.join(root, SELF_NAME))
    updated = text
    for pattern, template in ROW_PATTERNS:
        updated = pattern.sub(template.format(rows=rows), updated)

    lines = updated.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not DIGEST_LINE.search(line):
            continue
        context = line
        for back in range(1, SEAL_LOOKBACK + 1):
            if index - back >= 0:
                context += " " + lines[index - back]
        if _is_seal_line(context):
            lines[index] = DIGEST_LINE.sub(digest, line)
    updated = "".join(lines)

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
    if (
        f"{rows:,} rows" not in text
        and f"{rows:,}-row" not in text
        and f"{rows:,} files pinned" not in text
    ):
        problems.append(f"row count {rows:,} not stated")
    stated = seal_digests(text)
    if not stated:
        problems.append(f"seal {digest[:16]}... not stated")
    stale = sorted({value for value in stated if value != digest})
    if stale:
        problems.append(f"stale seal digest(s): {', '.join(v[:16] + '...' for v in stale)}")
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


def norm_key(key: str) -> str:
    """Canonical comparison form: POSIX separators, no `.` segments, folded case."""
    return posixpath.normpath(key.replace("\\", "/")).casefold()


def verify(root: str) -> int:
    manifest_path = os.path.join(root, SELF_NAME)
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            recorded = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: manifest.json unreadable: {type(exc).__name__}: {exc}")
        return 2
    if not isinstance(recorded, dict):
        print("FAIL: manifest.json is not a JSON object")
        return 2

    missing: list[str] = []
    mismatched: list[str] = []
    checked = 0
    for key, expected in recorded.items():
        path = resolve_key(root, key)
        if not os.path.isfile(path):
            missing.append(key)
            continue
        checked += 1
        if canonical_sha256(path) != expected:
            mismatched.append(key)

    current = scan(root)
    recorded_keys = {norm_key(k) for k in recorded}
    extra = [key for key in current if norm_key(key) not in recorded_keys]

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
    args = argv[1:]
    if args == ["--verify"]:
        return verify(root)
    if args in ([], ["--reseal"]):
        return reseal(root)
    # Unknown flags fail closed.  A typo must never silently rewrite the ledger.
    print("usage: repokeeper.py [--reseal | --verify]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
