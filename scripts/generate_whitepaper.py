"""Generate a PDF white paper refuting the false claim that 2 + 2 = 5.

This script uses ReportLab to render a simple PDF document that summarizes the
logical fallacies found in a popular erroneous proof that attempts to show
``2 + 2 = 5``.  The script mirrors the narrative supplied in the project brief
and can be used during audits to demonstrate the provenance of the accompanying
analysis.

Running the script will create ``WhitePaper_2plus2_Not5.pdf`` in the repository
root (or a custom output path supplied via the command line).  The PDF is
rendered using standard ReportLab primitives so no external templates are
required.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ImportError as exc:  # pragma: no cover - this is a runtime convenience guard
    raise SystemExit(
        "ReportLab is required to generate the PDF. Install it with 'pip install reportlab'."
    ) from exc


def _register_cjk_font() -> None:
    """Ensure that a Unicode-capable font is registered for CJK glyph support."""

    font_name = "HeiseiMin-W3"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        except Exception:  # pragma: no cover - defensive, depends on runtime font availability
            # If the font cannot be registered (e.g., missing from the runtime), we
            # silently proceed because the document text only uses ASCII glyphs.
            pass


def build_story(timestamp: str, hash_seal: str) -> list:
    """Create the platypus story that will be rendered into the PDF."""

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("White Paper: Refutation of the False Mathematical Claim that 2 + 2 = 5", styles["Title"]))
    story.append(Spacer(1, 12))

    intro = (
        "This white paper addresses and refutes the claim made in a handwritten image "
        "that attempts to prove the false statement: 2 + 2 = 5. The arguments in the "
        "image use logically invalid steps, algebraic fallacies, and contradictions "
        "to mislead the reader. This document presents a rigorous dissection of each "
        "method used and provides the logical basis for rejecting the claim within "
        "standard arithmetic."
    )
    story.append(Paragraph(intro, styles["BodyText"]))
    story.append(Spacer(1, 12))

    method1 = (
        "<strong>Method 1 Analysis:</strong><br/>"
        "The first method assumes values: x₁ = 16, x₂ = 4, y₁ = 20, y₂ = 5. It forms the equation "
        "x₁ + x₂ = y₁ + y₂. Substituting, we get 16 + 4 = 20, and 20 ≠ 25. The method then asserts “20 = 25,” "
        "which is mathematically false.<br/>From this contradiction, it derives 10 + 10 = 25, then divides both sides by 5 "
        "to get 2 + 2 = 5. However, starting from a falsehood (20 = 25) and manipulating it yields invalid results."
    )
    story.append(Paragraph(method1, styles["BodyText"]))
    story.append(Spacer(1, 12))

    method2 = (
        "<strong>Method 2 Analysis:</strong><br/>"
        "The second method assumes that (4 - 2)(1 + 1) = (2 + 3), which evaluates as 2 × 2 = 4 on the left-hand "
        "side, and 5 on the right-hand side. This gives 4 ≠ 5, yet it is claimed that because 4 = 2 + 2, we now "
        "have 2 + 2 = 5. This is a complete logical non-sequitur."
    )
    story.append(Paragraph(method2, styles["BodyText"]))
    story.append(Spacer(1, 12))

    logic = (
        "<strong>Logical Violations:</strong><br/>"
        "1. <em>False Premise Propagation</em>: Using false equalities like 20 = 25 or 4 = 5 invalidates all downstream reasoning.<br/>"
        "2. <em>Non Sequitur</em>: Deriving a conclusion that does not follow from the premises.<br/>"
        "3. <em>Violation of Peano Arithmetic</em>: Standard arithmetic over the natural numbers defines 2 + 2 = 4 axiomatically."
    )
    story.append(Paragraph(logic, styles["BodyText"]))
    story.append(Spacer(1, 12))

    conclusion = (
        "<strong>Conclusion:</strong><br/>"
        "The claim that 2 + 2 = 5 is categorically false. No manipulation of arithmetic that begins with invalid assumptions "
        "or logical fallacies can be accepted. This document reaffirms that under all valid logical and mathematical systems "
        "of classical arithmetic, 2 + 2 = 4.<br/><br/>"
        f"<strong>Hashstamp:</strong> {hash_seal}<br/>"
        f"<strong>Timestamp:</strong> {timestamp}<br/>"
        "<strong>Crown Seal:</strong> ✅"
    )
    story.append(Paragraph(conclusion, styles["BodyText"]))

    return story


def generate_whitepaper(output_path: Path) -> Path:
    """Render the PDF white paper to ``output_path`` and return the resolved path."""

    _register_cjk_font()

    timestamp = datetime.utcnow().isoformat() + "Z"
    hash_seal = "HASHSTAMP#𝓕(GenesisΩ†Black)×ΣΩ⧖"

    story = build_story(timestamp=timestamp, hash_seal=hash_seal)

    doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)
    doc.build(story)
    return output_path.resolve()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate a PDF refutation of the claim that 2 + 2 = 5.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("WhitePaper_2plus2_Not5.pdf"),
        help="Destination path for the generated PDF (default: ./WhitePaper_2plus2_Not5.pdf)",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""

    args = parse_args()
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = generate_whitepaper(output_path)
    print(f"White paper written to {pdf_path}")


if __name__ == "__main__":
    main()
