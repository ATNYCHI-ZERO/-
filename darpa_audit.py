"""Utilities for auditing repository files.

This module exposes helpers that read every non-ignored file inside the
repository and surface basic metadata such as the file size and SHA-256 hash.
The helpers are intentionally lightweight so that they can be executed in
restricted environments (such as an automated DARPA-style audit) without
external dependencies.

The command line interface now supports JSON output and caller supplied
exclusion lists so that downstream tooling can ingest the audit results without
having to reimplement repository traversal logic.  The implementation remains
pure standard library code to satisfy constrained execution environments.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set
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

    resolved_root = root.resolve()
    excluded: Set[str] = {d for d in excluded_dirs}

    yield from _iter_repository_files(resolved_root, excluded)


def _iter_repository_files(current: Path, excluded: Set[str]) -> Iterable[Path]:
    """Internal helper that performs the recursive directory walk."""

    for entry in sorted(current.iterdir()):
        if entry.name in excluded:
            continue

        if entry.is_dir():
            # Symlinked directories can easily introduce cycles; skip them to
            # keep the audit deterministic and self-contained.
            if entry.is_symlink():
                continue

            yield from _iter_repository_files(entry, excluded)
            continue

        if entry.is_file():
            yield entry


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

    records.sort(key=lambda record: record.path)
    return records


def _relative_path(path: Path, root: Path) -> Path:
    """Return ``path`` relative to ``root`` when possible."""

    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(root)
    except ValueError:
        return resolved_path


def format_audit_records(
    records: Sequence[FileAuditRecord],
    *,
    root: Path,
    output_format: str = "text",
) -> str:
    """Format ``records`` for presentation in the requested ``output_format``."""

    normalized_root = root.resolve()

    if output_format == "json":
        payload = [
            {
                "path": str(_relative_path(record.path, normalized_root)),
                "size": record.size,
                "sha256": record.sha256,
            }
            for record in records
        ]
        return json.dumps(payload, indent=2)

    if output_format != "text":
        raise ValueError(f"Unsupported output format: {output_format!r}")

    lines = [
        "DARPA Repository Audit Summary",
        "=" * 32,
    ]
    for record in records:
        relative_path = _relative_path(record.path, normalized_root)
        lines.append(
            f"{relative_path}\t{record.size} bytes\tSHA256={record.sha256}"
        )

    return "\n".join(lines)


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct the command line interface parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root to audit (defaults to the module directory).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="DIR",
        help=(
            "Additional directory name to exclude during traversal. "
            "May be provided multiple times."
        ),
    )
    parser.add_argument(
        "--format",
        choices={"text", "json"},
        default="text",
        help="Output format for the audit summary (default: text).",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Execute an audit over the repository containing this module."""

    parser = build_cli_parser()
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    excluded_dirs = DEFAULT_EXCLUDED_DIRS | {Path(d).name for d in args.exclude}
    records = collect_file_audit_records(repo_root, excluded_dirs=excluded_dirs)
    output = format_audit_records(records, root=repo_root, output_format=args.format)
    print(output)


if __name__ == "__main__":
    main()
