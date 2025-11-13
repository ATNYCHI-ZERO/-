#!/usr/bin/env python3
"""DARPA audit utility for verifying repository files are readable.

This tool walks the repository tree, skipping common virtual environment
and VCS directories, and records a SHA-256 digest for each file.  The
report is written to ``darpa_audit_report.json`` in the repository root
and printed to stdout so auditors can confirm the inventory.
"""Utilities for auditing repository files.

This module exposes helpers that read every non-ignored file inside the
repository and surface basic metadata such as the file size and SHA-256 hash.
The helpers are intentionally lightweight so that they can be executed in
restricted environments (such as an automated DARPA-style audit) without
external dependencies.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sys
from typing import Iterable, List
import hashlib

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
}


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield all files under *root* excluding skipped directories."""

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def hash_file(path: Path) -> str:
    """Return the SHA-256 digest for *path* as a hex string."""

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(root: Path) -> List[dict]:
    """Construct the audit report data structure for the repository."""

    report_entries: List[dict] = []
    for file_path in sorted(iter_repo_files(root)):
        report_entries.append(
            {
                "path": str(file_path.relative_to(root)),
                "sha256": hash_file(file_path),
                "size_bytes": file_path.stat().st_size,
            }
        )
    return report_entries


def write_report(root: Path, report_data: List[dict], *, output: Path) -> None:
    """Write *report_data* to *output* in JSON format."""

    payload = {
        "generated_at": _dt.datetime.utcnow().isoformat() + "Z",
        "repository_root": str(root),
        "file_count": len(report_data),
        "files": report_data,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")



def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("darpa_audit_report.json"),
        help="Where to write the audit report (default: %(default)s)",
    )
    return parser.parse_args(list(argv))



def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parent
    report = build_report(repo_root)
    write_report(repo_root, report, output=args.output)
    print(
        f"DARPA audit report generated for {len(report)} file(s).\n"
        f"Report saved to {args.output}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main(sys.argv[1:]))
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Iterable, List


DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__"}


@dataclass(frozen=True)
class FileAuditRecord:
    """Represents a successfully audited repository file."""

    path: Path
    size: int
    sha256: str


def iter_repository_files(
    root: Path,
    excluded_dirs: Iterable[os.PathLike[str] | str] = DEFAULT_EXCLUDED_DIRS,
) -> Iterable[Path]:
    """Yield all files under ``root`` excluding the specified directories."""

    excluded = {os.fspath(d) for d in excluded_dirs}
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


def _stream_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute the SHA-256 digest for ``path`` without loading it entirely."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_file_audit(path: Path) -> FileAuditRecord:
    """Construct a :class:`FileAuditRecord` for ``path`` using streaming IO."""

    size = path.stat().st_size
    digest = _stream_sha256(path)
    return FileAuditRecord(path=path, size=size, sha256=digest)


def collect_file_audit_records(
    root: Path,
    excluded_dirs: Iterable[os.PathLike[str] | str] = DEFAULT_EXCLUDED_DIRS,
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
