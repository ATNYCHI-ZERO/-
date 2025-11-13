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


DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache"}


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
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            if path.name in excluded:
                # Skip exploring this directory entirely by continuing; rglob
                # has already yielded the directory so we simply ignore it.
                continue
            continue

        if any(part in excluded for part in path.parts):
            continue

        yield path


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

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Audit repository files by emitting their relative path, size, and SHA-256 hash."
        )
    )
    parser.add_argument(
        "--exclude",
        "-e",
        action="append",
        default=[],
        help=(
            "Additional directory names to exclude from the audit.  The match is performed"
            " against each path component, similar to the default exclusions."
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    excluded = set(DEFAULT_EXCLUDED_DIRS).union(args.exclude)
    records = collect_file_audit_records(repo_root, excluded_dirs=excluded)
    print("DARPA Repository Audit Summary")
    print("=" * 32)
    for record in records:
        relative_path = record.path.relative_to(repo_root)
        print(f"{relative_path}\t{record.size} bytes\tSHA256={record.sha256}")


if __name__ == "__main__":
    main()
