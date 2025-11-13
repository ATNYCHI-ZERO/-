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
import hashlib
import os


_DEFAULT_HASH_CHUNK_SIZE = 1024 * 1024  # 1 MiB


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
    root = root.resolve()
    for current_dir, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in excluded)

        for filename in sorted(filenames):
            path = Path(current_dir) / filename
            relative_parts = path.relative_to(root).parts
            if any(part in excluded for part in relative_parts):
                continue
            yield path


def _sha256_digest(path: Path, chunk_size: int = _DEFAULT_HASH_CHUNK_SIZE) -> str:
    """Stream ``path`` and return its SHA-256 digest."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_file_audit(path: Path) -> FileAuditRecord:
    """Construct a :class:`FileAuditRecord` for ``path``."""

    size = path.stat().st_size
    digest = _sha256_digest(path)
    return FileAuditRecord(path=path, size=size, sha256=digest)


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
