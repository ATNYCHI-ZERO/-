"""DARPA audit utility.

This script scans the repository tree (excluding the Git directory) and
verifies that each regular file is readable.  It prints a short report
that can be used to confirm the audit ran successfully.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class AuditResult:
    path: Path
    status: str
    details: str = ""


def iter_repo_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file():
            yield path


def audit_file(path: Path) -> AuditResult:
    try:
        content = path.read_text(errors="ignore")
    except Exception as exc:  # pylint: disable=broad-except
        return AuditResult(path=path, status="ERROR", details=str(exc))

    if not content.strip():
        return AuditResult(path=path, status="EMPTY", details="File has no readable content")
    return AuditResult(path=path, status="OK")


def run_audit(root: Path) -> list[AuditResult]:
    return [audit_file(path) for path in iter_repo_files(root)]


def main() -> None:
    root = Path(__file__).resolve().parent
    results = run_audit(root)

    print("DARPA Audit Report")
    print("Root:", root)
    failures = 0
    for result in results:
        line = f"[{result.status}] {result.path.relative_to(root)}"
        if result.details:
            line += f" - {result.details}"
        print(line)
        if result.status != "OK":
            failures += 1

    if failures:
        print(f"Audit completed with {failures} issue(s).")
    else:
        print("Audit completed successfully. All files readable.")


if __name__ == "__main__":
    main()
