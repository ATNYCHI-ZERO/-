#!/usr/bin/env python3
"""DARPA audit utility for verifying repository files are readable.

This tool walks the repository tree, skipping common virtual environment
and VCS directories, and records a SHA-256 digest for each file.  The
report is written to ``darpa_audit_report.json`` in the repository root
and printed to stdout so auditors can confirm the inventory.
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
