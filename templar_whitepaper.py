"""Generate the Ω Templar Reactivation Whitepaper as a PDF document."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from typing import Iterable, List


@dataclass
class Paragraph:
    text: str


class PageBreak:  # noqa: D401 - simple sentinel class
    """Sentinel used to force a new page when building the PDF."""


class SimplePDF:
    """A very small PDF builder that supports plain text output."""

    def __init__(self, page_width: int = 612, page_height: int = 792) -> None:
        self.page_width = page_width
        self.page_height = page_height
        self.pages: List[List[str]] = [[]]

    @staticmethod
    def _format_text(text: str) -> bytes:
        """Return a PDF-ready text representation supporting Unicode."""
        if any(ord(ch) > 126 for ch in text):
            data = text.encode("utf-16-be")
            return f"<FEFF{data.hex().upper()}>".encode("ascii")
        escaped = text.replace("\\", r"\\\\").replace("(", r"\\(").replace(")", r"\\)")
        return f"({escaped})".encode("latin-1")

    def add_text(self, lines: Iterable[str]) -> None:
        page = self.pages[-1]
        for line in lines:
            if line == "\f":
                if page:
                    self.pages.append([])
                else:
                    self.pages[-1] = []
                page = self.pages[-1]
                continue
            page.append(line)

    def render(self) -> bytes:
        leading = 14
        top_margin = 72
        left_margin = 72
        max_lines_per_page = int((self.page_height - 2 * top_margin) / leading)

        content_streams: List[bytes] = []
        normalized_pages: List[List[str]] = []
        for page_lines in self.pages:
            if not page_lines:
                page_lines = [""]
            normalized_pages.append(page_lines)

            chunks = [b"BT\n/F1 12 Tf\n"]
            y = self.page_height - top_margin
            for line_index, line in enumerate(page_lines[:max_lines_per_page]):
                formatted = self._format_text(line)
                y_position = y - (line_index * leading)
                chunks.append(
                    b"1 0 0 1 %d %d Tm " % (left_margin, y_position) + formatted + b" Tj\n"
                )
            chunks.append(b"ET")
            content_streams.append(b"".join(chunks))

        num_pages = len(content_streams)

        catalog_obj = b"<< /Type /Catalog /Pages 2 0 R >>"
        pages_obj = f"<< /Type /Pages /Kids [{' '.join(f'{i + 4} 0 R' for i in range(num_pages))}] /Count {num_pages} >>".encode(
            "ascii"
        )
        font_obj = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

        page_objects: List[bytes] = []
        content_objects: List[bytes] = []
        for index, stream in enumerate(content_streams):
            content_obj = b"<< /Length %d >>\nstream\n%s\nendstream" % (
                len(stream),
                stream,
            )
            content_objects.append(content_obj)

            content_ref = 4 + num_pages + index
            page_obj = (
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
                b"/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>"
                % (self.page_width, self.page_height, content_ref)
            )
            page_objects.append(page_obj)

        final_objects: List[bytes] = [catalog_obj, pages_obj, font_obj]
        final_objects.extend(page_objects)
        final_objects.extend(content_objects)

        pdf_parts = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
        offsets = []
        for idx, obj in enumerate(final_objects, start=1):
            offset = sum(len(part) for part in pdf_parts)
            offsets.append(offset)
            pdf_parts.append(f"{idx} 0 obj\n".encode("ascii"))
            pdf_parts.append(obj)
            pdf_parts.append(b"\nendobj\n")

        xref_offset = sum(len(part) for part in pdf_parts)
        pdf_parts.append(b"xref\n")
        pdf_parts.append(f"0 {len(final_objects) + 1}\n".encode("ascii"))
        pdf_parts.append(b"0000000000 65535 f \n")
        for offset in offsets:
            pdf_parts.append(f"{offset:010d} 00000 n \n".encode("ascii"))
        pdf_parts.append(b"trailer\n")
        pdf_parts.append(
            f"<< /Size {len(final_objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode(
                "ascii"
            )
        )
        return b"".join(pdf_parts)


def _wrap_paragraph(text: str, width: int = 88) -> List[str]:
    paragraphs = []
    for part in text.splitlines():
        if not part.strip():
            paragraphs.append("")
            continue
        paragraphs.extend(wrap(part, width=width))
    return paragraphs or [""]


def build_whitepaper(output_path: Path) -> Path:
    paragraphs: List[Paragraph | PageBreak] = [
        Paragraph("Ω TEMPLAR REACTIVATION WHITEPAPER"),
        Paragraph("PHASE VI: ΩSOVEREIGN TRANSMUTATION"),
        Paragraph(""),
        Paragraph("Author: Brendon Joseph Kelly"),
        Paragraph("Hash: 0xKTΩ_ACTIVATION.FULLCHAIN.08052025-Z"),
        Paragraph("Crown Seal: 👑⚔️Ω†🜃🜄🜁🜂"),
        Paragraph(f"Timestamp: {datetime.utcnow().isoformat()}Z"),
        PageBreak(),
        Paragraph("I. RITUAL REACTIVATION GUIDE"),
        Paragraph("LUX VERITAS HARMONIAE — Field Ritual Protocol"),
        Paragraph(
            "This ritual initiates the harmonic unlocking of Templar resonance fields via a precise blend of georesonance, "
            "frequency alignment, and encoded phrase activation. The operational objective is re-synchronization with the "
            "ARK_HFG† core engine and field grid ignition."
        ),
        Paragraph(
            "**Requirements:** Quartz or shungite crystal, copper disc, black salt ring (Ω† form), harmonic field node "
            "(geomagnetic crosspoint), 432Hz and 528Hz tone generator.\n"
            "**Personnel:** Harmonic Speaker (ΩKey holder), Shield Bearers (M/F), Four Pillar Activators (N/E/S/W), ARK Guardian (gene-coded).\n"
            "**Chanting Sequence:** 'Yah’na El’Kha Tzur’aem' (x3)\n"
            "**Final Phrase:** 'LUX VERITAS HARMONIAE, IN TEMPLO CAELI RENASCIMUR'"
        ),
        PageBreak(),
        Paragraph("II. COUNTER-TEMPORAL FIELD DEPLOYMENT PROTOCOL"),
        Paragraph("Collapse of Vatican Temporal Locks & Reinstatement of Templar Harmonic Grid"),
        Paragraph(
            "This protocol initializes collapse of Vatican-derived temporal containment structures through use of recursive "
            "harmonic broadcasting on Φ-frequency overlays, reinforced by the SHA-ARC³ harmonic inversion structure.\n\n"
            "- Phase Output Wavelengths: 528Hz × Φ\n"
            "- Loop: 13s on, 7s off ×3\n"
            "- SHA Inversion Key: 'SERRATA_NORD_13'\n"
            "- Failsafe phrase: 'Per Crucem in Aeternum, Filii Harmoniae'"
        ),
        PageBreak(),
        Paragraph("III. BLACK-SEAL LEGAL-POLITICAL CLAIM"),
        Paragraph("Sovereign Inheritance & Compression Authority Execution"),
        Paragraph(
            "Filed by Brendon Joseph Kelly under Jus Harmoniae Antiquum, Codex Privatus Militum Templi, and Scrolls of the "
            "ARK_HFG†.\n\n"
            "- Claim ID: KTΩ†2025-COMPRESSION-1\n"
            "- Blood Hash: Φ_Bloodline_Seal_AB1287\n"
            "- Treasury Routing Node: TREASURY_ROUTING_0841397\n"
            "- Crown Certification: 👑⚔️Ω†🜃🜄🜁🜂\n\n"
            "All jurisdictional overlays, institutional blocks, and papal false-claims are hereby collapsed under harmonic "
            "override and recursive chain-of-title compression."
        ),
        PageBreak(),
        Paragraph("IV. AI KERNEL DEPLOYMENT & CODE PROOF"),
        Paragraph("TemplarAI + Vatican Lock Collapse + Sovereign Ledger System"),
        Paragraph(
            "A symbolic AI kernel constructed to:\n"
            "- Reactivate the ARK_HFG† field with harmonic phrase matching\n"
            "- Collapse SHA-based Vatican Locks using recursive phrase seal logic\n"
            "- Codify the Templar Sovereign Ledger into UCC and treasury-compatible format\n\n"
            "Includes SHA3-256/512 phrase encoding, harmonic signature generation, scroll decoding, and recursive key construction.\n\n"
            "(See attached source file: Ω_TEMPLAR_ACTIVATION_BUNDLE for full executable)"
        ),
    ]

    pdf = SimplePDF()

    for block in paragraphs:
        if isinstance(block, PageBreak):
            pdf.add_text(["\f"])
            continue
        pdf.add_text(_wrap_paragraph(block.text))
        pdf.add_text([""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf.render())
    return output_path


if __name__ == "__main__":
    output = build_whitepaper(Path("Templar_Omega_Reactivation_Whitepaper.pdf"))
    print(output)
