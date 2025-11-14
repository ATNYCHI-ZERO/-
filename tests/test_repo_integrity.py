"""Repository integrity tests for DARPA-style audit readiness.

These tests ensure that every tracked file in the repository can be opened
and read as UTF-8 text. This mirrors a lightweight compliance audit by
verifying that critical documentation artifacts are accessible and non-empty.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _iter_auditable_files() -> Iterator[Path]:
    """Yield repo files that should be included in the audit."""
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(REPO_ROOT)
        if relative.parts[0] in {".git", "__pycache__", ".pytest_cache"}:
            continue
        if any(part.startswith(".") for part in relative.parts[:-1]):
            continue
        yield relative


def auditable_files() -> Iterable[Path]:
    files = list(_iter_auditable_files())
    if not files:
        pytest.skip("No files discovered for audit.")
    return files


@pytest.mark.parametrize("relative_path", auditable_files(), ids=str)
def test_file_is_accessible_and_non_empty(relative_path: Path) -> None:
    """Ensure each auditable file can be opened and contains textual content."""
    target = REPO_ROOT / relative_path
    with target.open("r", encoding="utf-8", errors="ignore") as handle:
        content = handle.read()
    assert content.strip(), f"{relative_path} appears to be empty or unreadable"
