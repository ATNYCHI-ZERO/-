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
import argparse
import hashlib
import json


DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__"}


@dataclass(frozen=True)
class FileAuditRecord:
    """Represents a successfully audited repository file."""

    path: Path
    size: int
    sha256: str


def iter_repository_files(
    root: Path,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
    *,
    include_hidden: bool = False,
) -> Iterable[Path]:
    """Yield all files under ``root`` excluding the specified directories.

    Parameters
    ----------
    root:
        Repository root to traverse.
    excluded_dirs:
        Iterable of directory names that should never be audited.  The values
        are compared against each component of a path, so providing ``.git``
        ignores the entire Git metadata tree regardless of location.
    include_hidden:
        When ``True`` hidden files and directories (components that start with a
        dot) are included in the audit.  By default, dot-prefixed files are
        skipped to mimic traditional DARPA audit sweeps that focus on tracked
        artifacts.
    """

    root = root.resolve()
    excluded = {d for d in excluded_dirs}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue

        if any(part in excluded for part in path.parts):
            continue

        if not include_hidden and _contains_hidden_component(path, root):
            continue

        yield path


def _contains_hidden_component(path: Path, root: Path) -> bool:
    """Return ``True`` when ``path`` contains a hidden component."""

    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        relative_parts = path.parts

    return any(part.startswith(".") for part in relative_parts)


def build_file_audit(path: Path) -> FileAuditRecord:
    """Construct a :class:`FileAuditRecord` for ``path``."""

    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    return FileAuditRecord(path=path, size=len(data), sha256=digest)


def collect_file_audit_records(
    root: Path,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
    *,
    include_hidden: bool = False,
) -> List[FileAuditRecord]:
    """Collect audit records for each relevant file in ``root``."""

    records: List[FileAuditRecord] = []
    for file_path in iter_repository_files(
        root, excluded_dirs=excluded_dirs, include_hidden=include_hidden
    ):
        records.append(build_file_audit(file_path))
    return records


def _format_records_text(records: List[FileAuditRecord], repo_root: Path) -> str:
    """Return a human readable summary for ``records``."""

    lines = ["DARPA Repository Audit Summary", "=" * 32]
    for record in records:
        relative_path = record.path.relative_to(repo_root)
        lines.append(
            f"{relative_path}\t{record.size} bytes\tSHA256={record.sha256}"
        )

    total_bytes = sum(record.size for record in records)
    lines.append("-" * 32)
    lines.append(f"Total files audited: {len(records)}")
    lines.append(f"Total size: {total_bytes} bytes")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    """Return parsed command-line arguments for the module CLI."""

    parser = argparse.ArgumentParser(description="Run a DARPA-style file audit")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root to audit (defaults to the script directory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Emit human readable text or JSON output",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include dot-prefixed files and directories in the audit",
    )
    return parser.parse_args()


def main() -> None:
    """Execute an audit over the repository containing this module."""

    args = _parse_args()
    repo_root = args.root.resolve()
    records = collect_file_audit_records(
        repo_root, include_hidden=args.include_hidden
    )

    if args.format == "json":
        payload = [
            {
                "path": str(record.path.relative_to(repo_root)),
                "size": record.size,
                "sha256": record.sha256,
            }
            for record in records
        ]
        print(json.dumps(payload, indent=2))
    else:
        print(_format_records_text(records, repo_root))


if __name__ == "__main__":
    main()
