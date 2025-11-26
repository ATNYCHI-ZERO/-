"""Utilities for auditing repository files for accessibility and metadata.

This lightweight audit runner is intended to support DARPA-style review
processes where every file in the repository must be enumerated, opened, and
validated for basic integrity.  It produces a structured report that can be
exported as JSON or displayed in a human-readable summary.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parent


@dataclass
class FileAuditResult:
    """Record describing a single file that was audited."""

    path: Path
    size_bytes: int
    sha256: str

    @classmethod
    def from_path(cls, path: Path) -> "FileAuditResult":
        data = path.read_bytes()
        return cls(path=path.relative_to(REPO_ROOT), size_bytes=len(data), sha256=sha256(data).hexdigest())


@dataclass
class AuditReport:
    """Summary of the audit run."""

    files: List[FileAuditResult]

    def to_json(self) -> str:
        return json.dumps({"files": [asdict(result) for result in self.files]}, indent=2)

    def to_text(self) -> str:
        lines = ["AUDIT REPORT", "============", f"Files audited: {len(self.files)}", ""]
        for result in self.files:
            lines.append(f"- {result.path} (size={result.size_bytes} bytes, sha256={result.sha256})")
        return "\n".join(lines)


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield repository files in a stable, deterministic order.

    The function walks the ``root`` tree, skipping hidden files and directories
    (other than ``.gitignore``) and returns paths sorted lexicographically.  A
    stable ordering makes it easier to diff audit results across runs and
    improves test reliability.
    """

    candidates = sorted(root.rglob("*"))
    for path in candidates:
        if not path.is_file():
            continue
        if any(part.startswith(".") and part != ".gitignore" for part in path.relative_to(root).parts):
            # Skip hidden files (such as .git metadata) except for explicit exceptions.
            continue
        yield path


def run_audit(root: Path = REPO_ROOT) -> AuditReport:
    files = [FileAuditResult.from_path(path) for path in iter_repo_files(root)]
    return AuditReport(files=files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple DARPA-style repository audit.")
    parser.add_argument("--json", action="store_true", help="Emit the audit report as JSON instead of text.")
    return parser.parse_args()


def main() -> None:
    report = run_audit()
    if parse_args().json:
        print(report.to_json())
    else:
        print(report.to_text())


if __name__ == "__main__":
    main()
