"""Utilities for validating repository documentation during DARPA audits.

This module currently provides a simple function that reads the project
README and returns basic metadata that can be inspected or logged.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DocumentMetadata:
    """Basic statistics about a text document.

    Attributes
    ----------
    path:
        Location of the document on disk.
    line_count:
        Total number of non-empty lines in the document.
    headings:
        Sequence of detected markdown headings (``#`` prefixes).
    """

    path: Path
    line_count: int
    headings: tuple[str, ...]


def extract_document_metadata(path: Path) -> DocumentMetadata:
    """Return basic metadata for the markdown file located at *path*.

    Parameters
    ----------
    path:
        Markdown document to inspect.

    Returns
    -------
    DocumentMetadata
        Collected statistics for the provided document.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    ValueError
        If the target document is empty.
    """

    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]

    if not non_empty:
        raise ValueError(f"Document {path} is empty")

    headings = tuple(
        line.lstrip("# ")
        for line in lines
        if line.startswith("#")
    )

    return DocumentMetadata(path=path, line_count=len(non_empty), headings=headings)


def format_metadata_report(metadata: DocumentMetadata) -> str:
    """Format *metadata* into a human-readable string summary."""

    heading_list = ", ".join(metadata.headings) or "<none>"
    return (
        f"Document: {metadata.path}\n"
        f"Non-empty lines: {metadata.line_count}\n"
        f"Headings: {heading_list}"
    )


def iter_audit_documents(paths: Iterable[Path]) -> Iterable[DocumentMetadata]:
    """Yield :class:`DocumentMetadata` entries for every markdown file in *paths*."""

    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        yield extract_document_metadata(path)


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent
    metadata_items = list(iter_audit_documents(repo_root.iterdir()))

    if not metadata_items:
        raise SystemExit("No markdown files discovered for auditing.")

    for metadata in metadata_items:
        print(format_metadata_report(metadata))
