#!/usr/bin/env python3
"""Repository audit utilities.

This script performs a lightweight integrity sweep intended to emulate the
baseline checks that might precede a formal compliance or security audit.
The logic walks the working tree, validates that each tracked artifact is
readable, and records basic diagnostics such as the byte size and SHA-256
hash.  The resulting report can be fed into higher-assurance tooling or
archived as part of an audit trail.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parent
EXCLUDE_DIRS = {".git", "__pycache__"}


@dataclass
class FileReport:
    """Snapshot describing an audited file."""

    path: str
    size: int
    sha256: str
    mode: str


def iter_repository_files(base_dir: Path) -> Iterable[Path]:
    """Yield all regular files underneath *base_dir* excluding ignored dirs."""

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                # Skip hidden dotfiles that are typically tooling artifacts.
                continue
            yield Path(root) / name


def file_report(path: Path) -> FileReport:
    """Generate the :class:`FileReport` for *path*."""

    stat_result = path.stat()
    if not stat.S_ISREG(stat_result.st_mode):
        raise ValueError(f"Audit encountered non-regular file: {path}")

    with path.open("rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()

    return FileReport(
        path=str(path.relative_to(ROOT)),
        size=stat_result.st_size,
        sha256=digest,
        mode=stat.filemode(stat_result.st_mode),
    )


def generate_report(files: Iterable[Path]) -> List[FileReport]:
    """Collect :class:`FileReport` entries for every file in *files*."""

    return [file_report(path) for path in sorted(files)]


def main() -> None:
    files = list(iter_repository_files(ROOT))
    if not files:
        raise SystemExit("No auditable files found in repository.")

    report = generate_report(files)
    print(json.dumps([asdict(entry) for entry in report], indent=2))


if __name__ == "__main__":
    main()
