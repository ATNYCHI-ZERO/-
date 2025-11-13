#!/usr/bin/env python3
"""Simple DARPA audit placeholder script.

This script walks the repository tree and attempts to read every file
in text or binary mode to ensure that the files are accessible.  It can be
extended to add additional domain-specific checks.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Iterable


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield file paths under *root* ignoring common VCS and cache folders."""
    ignored_dirs = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        # Modify dirnames in-place to prevent walking ignored directories
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        for name in filenames:
            yield Path(dirpath, name)


def checksum(path: Path) -> str:
    """Return the SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def audit_repository(root: Path) -> int:
    """Audit files under *root*.

    Returns the number of files processed.
    """
    count = 0
    this_file = Path(__file__).resolve()
    for path in iter_repo_files(root):
        # Skip the audit script itself if the walk picks it up.
        if path.resolve() == this_file:
            continue
        checksum_value = checksum(path)
        print(f"AUDIT OK: {path.relative_to(root)} | sha256={checksum_value}")
        count += 1
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run DARPA-style audit checks")
    parser.add_argument(
        "root",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Repository root to audit (defaults to current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 2

    file_count = audit_repository(root)
    print(f"Audit complete. Processed {file_count} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
