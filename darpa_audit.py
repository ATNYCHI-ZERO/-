#!/usr/bin/env python3
"""Lightweight repository audit helpers.

The functions exposed by this module are intentionally small and dependency
free so they can be executed in constrained environments (for example a DARPA
style audit runner).  They walk the repository tree, skipping common tooling
artifacts, and compute SHA-256 digests for each discovered file.  The module
also provides a tiny CLI that emits the inventory as JSON.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Sequence, Set

# Directories that should be ignored when crawling the repository.
DEFAULT_EXCLUDED_DIRS: Set[str] = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
}

_CHUNK_SIZE = 1024 * 1024  # 1 MiB


@dataclass(frozen=True)
class FileAuditRecord:
    """Snapshot describing a single audited file."""

    path: Path
    size: int
    sha256: str


def iter_repository_files(
    root: Path, excluded_dirs: Iterable[str] | None = None
) -> Iterable[Path]:
    """Yield files underneath ``root`` while skipping ``excluded_dirs``.

    The returned iterator yields paths in sorted order so the output is stable
    across runs, simplifying downstream comparisons and tests.
    """

    if excluded_dirs is None:
        excluded = DEFAULT_EXCLUDED_DIRS
    else:
        excluded = set(excluded_dirs)

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in excluded for part in path.parts):
            continue
        yield path


def _stream_sha256(path: Path, chunk_size: int = _CHUNK_SIZE) -> str:
    """Compute the SHA-256 digest for ``path`` without loading it entirely."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_file_audit(path: Path) -> FileAuditRecord:
    """Construct a :class:`FileAuditRecord` describing ``path``."""

    return FileAuditRecord(
        path=path,
        size=path.stat().st_size,
        sha256=_stream_sha256(path),
    )


def collect_file_audit_records(
    root: Path, excluded_dirs: Iterable[str] | None = None
) -> List[FileAuditRecord]:
    """Collect audit records for every qualifying file in ``root``."""

    records: List[FileAuditRecord] = []
    for file_path in iter_repository_files(root, excluded_dirs=excluded_dirs):
        records.append(build_file_audit(file_path))
    return records


def _build_report_payload(
    root: Path, records: Sequence[FileAuditRecord]
) -> dict:
    """Convert ``records`` into a JSON serialisable payload."""

    return {
        "generated_at": _dt.datetime.utcnow().isoformat() + "Z",
        "repository_root": str(root),
        "file_count": len(records),
        "files": [
            {
                "path": str(record.path.relative_to(root)),
                "size_bytes": record.size,
                "sha256": record.sha256,
            }
            for record in records
        ],
    }


def _write_report(payload: dict, output: Path) -> None:
    """Persist the audit ``payload`` to ``output`` in JSON format."""

    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("darpa_audit_report.json"),
        help="Where to write the generated report (default: %(default)s)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root to audit (default: module directory)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry-point for the command line interface."""

    args = _parse_args(argv)
    records = collect_file_audit_records(args.root)
    payload = _build_report_payload(args.root, records)
    _write_report(payload, args.output)
    print(json.dumps([asdict(record) for record in records], indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
