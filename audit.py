"""Utility for reading and validating repository files for audit purposes."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

EXCLUDE_DIRS = {".git", "__pycache__"}


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield file paths under *root* while skipping excluded directories."""
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(parent.name in EXCLUDE_DIRS for parent in path.parents):
            continue
        yield path


@dataclass
class FileAuditResult:
    path: str
    size_bytes: int
    sha256: str
    readable: bool


@dataclass
class AuditReport:
    root: str
    files: List[FileAuditResult]

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_bytes(self) -> int:
        return sum(result.size_bytes for result in self.files)

    def to_json(self) -> str:
        payload = {
            "root": self.root,
            "total_files": self.total_files,
            "total_bytes": self.total_bytes,
            "files": [asdict(result) for result in self.files],
        }
        return json.dumps(payload, indent=2)


def audit_repository(root: Path) -> AuditReport:
    results: List[FileAuditResult] = []
    for file_path in iter_repo_files(root):
        try:
            data = file_path.read_bytes()
            readable = True
        except (OSError, IOError):
            data = b""
            readable = False

        sha256 = hashlib.sha256(data).hexdigest()
        results.append(
            FileAuditResult(
                path=str(file_path.relative_to(root)),
                size_bytes=len(data),
                sha256=sha256,
                readable=readable,
            )
        )
    return AuditReport(root=str(root), files=results)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Perform a DARPA-style repository audit")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Root directory to audit (defaults to current working directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable summary",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    report = audit_repository(root)

    if args.json:
        print(report.to_json())
    else:
        print(f"Audit root: {report.root}")
        print(f"Total files: {report.total_files}")
        print(f"Total bytes: {report.total_bytes}")
        for result in report.files:
            status = "readable" if result.readable else "unreadable"
            print(f" - {result.path}: {result.size_bytes} bytes ({status}), sha256={result.sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
