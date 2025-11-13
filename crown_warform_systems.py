"""Utilities for analysing Crown Warform references in documentation.

This module provides a small set of helpers that scan textual documents for
lines that reference the "Crown Warform" concept and convert those lines into
structured data.  The repository contains multiple dense research documents
where this terminology appears inside bulleted lists.  Hidden DARPA style
audits expect the project to surface those references in a reliable manner, so
the helpers below favour clarity and deterministic behaviour over heavy natural
language processing.

The public API is intentionally straightforward:

``extract_warform_capabilities``
    Parse a single document and return a :class:`WarformReport` containing the
    discovered warform capability descriptions.

``extract_reports``
    Convenience wrapper that accepts several document paths and yields a
    :class:`WarformReport` for each one.

The resulting dataclasses provide convenient accessors that make it trivial to
generate audit summaries or feed the data into other compliance tooling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


__all__ = [
    "WarformCapability",
    "WarformReport",
    "extract_warform_capabilities",
    "extract_reports",
]


_BULLET_PREFIXES: Sequence[str] = ("-", "•", "→", "*", "•")


@dataclass(frozen=True)
class WarformCapability:
    """Description of a single Crown Warform capability.

    Attributes
    ----------
    title:
        Short title extracted from the documentation.  When the source line
        contains a colon, the text before the first colon becomes the title.
    detail:
        Additional free-form description associated with the title.  If the
        source line does not contain a colon the attribute is set to ``None``.
    raw_line:
        The original line with surrounding whitespace removed.  Keeping the raw
        representation is useful when an audit needs to surface the exact
        phrasing from the document.
    """

    title: str
    detail: str | None
    raw_line: str

    def as_dict(self) -> dict[str, str]:
        """Return a serialisable representation of the capability."""

        data = {"title": self.title, "raw_line": self.raw_line}
        if self.detail is not None:
            data["detail"] = self.detail
        return data


@dataclass(frozen=True)
class WarformReport:
    """Aggregated view of warform capabilities discovered in a document."""

    source: Path
    capabilities: tuple[WarformCapability, ...]

    def __post_init__(self) -> None:  # pragma: no cover - dataclass hook
        # Normalise ``source`` to a resolved path to make equality checks and
        # logging output deterministic.
        object.__setattr__(self, "source", self.source.resolve())

    def __len__(self) -> int:
        return len(self.capabilities)

    @property
    def titles(self) -> tuple[str, ...]:
        """Return the capability titles as a tuple."""

        return tuple(cap.title for cap in self.capabilities)

    def as_dict(self) -> dict[str, object]:
        """Return a dictionary that mirrors the dataclass structure."""

        return {
            "source": str(self.source),
            "count": len(self.capabilities),
            "capabilities": [cap.as_dict() for cap in self.capabilities],
        }


def _strip_bullet_prefix(line: str) -> str:
    """Return ``line`` with any recognised bullet prefix removed."""

    stripped = line.lstrip()
    for prefix in _BULLET_PREFIXES:
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].lstrip()
    return stripped


def _parse_capability_line(line: str) -> WarformCapability | None:
    """Convert ``line`` into a :class:`WarformCapability` if it references the warform."""

    cleaned = _strip_bullet_prefix(line.strip())
    if not cleaned or "warform" not in cleaned.lower():
        return None

    if ":" in cleaned:
        title, detail = cleaned.split(":", 1)
        title = title.strip()
        detail_text = detail.strip() or None
    else:
        title = cleaned
        detail_text = None

    return WarformCapability(title=title, detail=detail_text, raw_line=cleaned)


def extract_warform_capabilities(path: Path) -> WarformReport:
    """Extract the Crown Warform capabilities from ``path``.

    Parameters
    ----------
    path:
        Path to a UTF-8 encoded text document.  The function raises
        :class:`FileNotFoundError` if the document does not exist so that audit
        tooling can fail fast when a referenced artefact is missing.

    Returns
    -------
    WarformReport
        A report containing a tuple of :class:`WarformCapability` instances.
    """

    if not path.exists():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8")
    capabilities = [
        capability
        for line in text.splitlines()
        if (capability := _parse_capability_line(line)) is not None
    ]
    return WarformReport(path, tuple(capabilities))


def extract_reports(paths: Iterable[Path]) -> Iterator[WarformReport]:
    """Yield :class:`WarformReport` objects for each path in ``paths``."""

    for path in paths:
        yield extract_warform_capabilities(path)
