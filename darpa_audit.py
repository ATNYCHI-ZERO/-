"""Utilities for reading every file in the repository and running basic verification.

This module is intentionally lightweight: the repository only contains a handful of
text files, but the audit utility is designed to scale to larger projects.  The
primary responsibilities are:

* Traverse every file in the repository (excluding version-control metadata).
* Attempt to read each file in UTF-8, falling back to binary mode if necessary.
* Capture metadata for each file so that an external auditor can review the
  collected information.
* Optionally run an arbitrary shell command (for example, a test suite) to
  validate repository health.

The module exposes a small CLI so that it can be executed directly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Iterator, List, Optional


DEFAULT_EXCLUDES = {".git", "__pycache__"}


@dataclass
class FileAuditResult:
    """Result of reading a single file within the repository."""

    path: str
    size_bytes: int
    sha256: str
    encoding: str
    read_ok: bool


def iter_repo_files(base_path: Path, excludes: Iterable[str] = DEFAULT_EXCLUDES) -> Iterator[Path]:
    """Yield all files under *base_path* excluding paths that begin with *excludes*.

    Parameters
    ----------
    base_path:
        Directory that will be traversed.
    excludes:
        Folder names to skip entirely.
    """

    exclude_set = set(excludes)
    for path in base_path.rglob("*"):
        if any(part in exclude_set for part in path.parts):
            continue
        if path.is_file():
            yield path


def audit_file(path: Path) -> FileAuditResult:
    """Read *path* and compute its hash.

    The function tries to read the file as UTF-8 text.  If decoding fails we fall
    back to reading the raw bytes.  A SHA-256 digest is captured regardless of the
    encoding so that auditors can verify file integrity.
    """

    try:
        content = path.read_bytes()
        read_ok = True
    except OSError:
        content = b""
        read_ok = False

    encoding = "binary"
    if read_ok:
        try:
            content.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "binary"

    sha = hashlib.sha256(content).hexdigest()
    return FileAuditResult(
        path=str(path.relative_to(Path.cwd())),
        size_bytes=len(content),
        sha256=sha,
        encoding=encoding,
        read_ok=read_ok,
    )


@dataclass
class CommandResult:
    """Outcome of running a shell command."""

    command: List[str]
    return_code: int
    stdout: str
    stderr: str


def run_command(command: Optional[List[str]]) -> Optional[CommandResult]:
    """Execute *command* if provided and capture the output."""

    if not command:
        return None

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    return CommandResult(
        command=command,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def perform_audit(repo_root: Path, command: Optional[List[str]]) -> dict:
    """Collect information about every file and optionally run *command*."""

    files = [audit_file(path) for path in iter_repo_files(repo_root)]
    result = {
        "repository_root": str(repo_root),
        "file_count": len(files),
        "files": [asdict(file_result) for file_result in files],
    }

    cmd_result = run_command(command)
    if cmd_result:
        result["command"] = asdict(cmd_result)

    return result


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Audit repository files for DARPA compliance checks.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the repository to audit.",
    )
    parser.add_argument(
        "--command",
        nargs=argparse.REMAINDER,
        help="Optional command to run after auditing files (e.g., pytest).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write JSON output.  If omitted the result is printed to stdout.",
    )
    args = parser.parse_args(argv)

    audit_data = perform_audit(args.repo_root, args.command)

    if args.output:
        args.output.write_text(json.dumps(audit_data, indent=2))
    else:
        print(json.dumps(audit_data, indent=2))


if __name__ == "__main__":
    main()
