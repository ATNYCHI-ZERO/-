"""Utilities for auditing repository files.

This module exposes helpers that read every non-ignored file inside the
repository and surface basic metadata such as the file size and SHA-256 hash.
The helpers are intentionally lightweight so that they can be executed in
restricted environments (such as an automated DARPA-style audit) without
external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import os
import hashlib


DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__"}


@dataclass(frozen=True)
class FileAuditRecord:
    """Represents a successfully audited repository file."""

    path: Path
    size: int
    sha256: str


def iter_repository_files(
    root: Path, excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS
) -> Iterable[Path]:
    """Yield all files under ``root`` excluding the specified directories."""

    excluded = {d for d in excluded_dirs}
    for current_root, dirnames, filenames in os.walk(root):
        # Mutate ``dirnames`` in-place so ``os.walk`` will skip excluded
        # directories entirely instead of traversing into them and their
        # descendants.  This mirrors the behaviour callers expect from the
        # public API and avoids scanning large directories such as ``.git``.
        dirnames[:] = [name for name in dirnames if name not in excluded]

        current_path = Path(current_root)
        for filename in sorted(filenames):
            candidate = current_path / filename
            yield candidate


def build_file_audit(path: Path) -> FileAuditRecord:
    """Construct a :class:`FileAuditRecord` for ``path``."""

    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    return FileAuditRecord(path=path, size=len(data), sha256=digest)


def collect_file_audit_records(
    root: Path, excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS
) -> List[FileAuditRecord]:
    """Collect audit records for each relevant file in ``root``."""

    records: List[FileAuditRecord] = []
    for file_path in iter_repository_files(root, excluded_dirs=excluded_dirs):
        records.append(build_file_audit(file_path))
    return records


def main() -> None:
    """Execute an audit over the repository containing this module."""

    repo_root = Path(__file__).resolve().parent
    records = collect_file_audit_records(repo_root)
    print("DARPA Repository Audit Summary")
    print("=" * 32)
    for record in records:
        relative_path = record.path.relative_to(repo_root)
        print(f"{relative_path}\t{record.size} bytes\tSHA256={record.sha256}")


if __name__ == "__main__":
    main()
