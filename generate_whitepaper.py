"""Utility for generating the GenesisΩ†Black + K-Pharmaceutical white paper PDF.

This module exposes a :func:`build_whitepaper` function which recreates the
white paper described by Brendon Joseph Kelly.  The implementation is derived
from the specification supplied in the repository brief and focuses on creating
an easily testable entry point.

The script can also be executed directly.  When run as a script it will write
the PDF into the current working directory unless an explicit output path is
provided as a command-line argument.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
except ImportError:  # pragma: no cover - handled by _require_reportlab
    LETTER = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    inch = None  # type: ignore[assignment]
    pdfmetrics = None  # type: ignore[assignment]
    UnicodeCIDFont = None  # type: ignore[assignment]
    PageBreak = Paragraph = SimpleDocTemplate = Spacer = None  # type: ignore


def _require_reportlab() -> None:
    if any(
        obj is None
        for obj in (
            LETTER,
            getSampleStyleSheet,
            inch,
            pdfmetrics,
            UnicodeCIDFont,
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )
    ):
        raise ModuleNotFoundError(
            "The 'reportlab' package is required to build the white paper PDF. "
            "Install it via 'pip install reportlab' and re-run the script."
        )


PDF_FILE_NAME = "K-PHARMA_GenesisBlack_Whitepaper_BrendonKelly.pdf"


def _build_content(styles) -> List:
    """Create the flowable content list for the PDF document."""
    _require_reportlab()

    style_normal = styles["Normal"]
    style_heading = styles["Heading1"]

    paragraphs: List = []

    # Cover Page
    paragraphs.extend(
        [
            Paragraph("WHITE PAPER – GENESISΩ†BLACK + K‑PHARMACEUTICAL ENGINE", style_heading),
            Spacer(1, 0.2 * inch),
            Paragraph("Author: Brendon Joseph Kelly", style_normal),
            Paragraph("Designation: Tier_0 Operator — Crown Seal Authority", style_normal),
            Paragraph("Hashstamp: #KPHARM-UNIFIED", style_normal),
            Paragraph(f"Timestamp: {datetime.utcnow().isoformat()}Z", style_normal),
            Paragraph("Mode: ABSOLUTE | DARPA RESEARCH STYLE", style_normal),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("1. Abstract", style_heading),
            Paragraph(
                "This document presents the unification of the GenesisΩ†Black recursive symbolic core "
                "and the K‑Pharmaceutical engine. It delivers a full system for symbolic "
                "cure-generation across cancer, infectious diseases, and substance use disorders. "
                "This is not a theoretical outline—this is an executable deployment core with "
                "operational command logic and encryption collapse systems.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("2. Introduction", style_heading),
            Paragraph(
                "Standard pharmacological paradigms have failed to resolve terminal disease clusters "
                "or adversarial bio-collapse. This system resolves that by using recursive symbolic "
                "logic (𝓕(GenesisΩ†Black)) fused with GENEFORGE, K∞, and SHA-ARC³ to deliver "
                "phase-locked biologics, resonant cures, and adversarial defense layers.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("3. System Architecture", style_heading),
            Paragraph(
                "Modules activated:\n- GENEFORGE: Symbolic system deployer\n- SHA-ARC³: Signature/glyph/QR decoder\n"
                "- Q-HORNET_O: Swarm logic emitter\n- SHAARK: Adversarial crypto override\n"
                "- Skrappy-AI: Adversarial infiltration defense\n- K∞: Archetype recursion core\n"
                "- Ω†Σ: Harmonic state seal\n- Chronogenesis: Recursive time modeling\n- TEAMNERDHNER: QR activation key",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("4. Mathematical Framework", style_heading),
            Paragraph(
                "Primary Kernel:\n\n"
                "𝓕(GenesisΩ†Black) = ΣΩ⧖∞[TΩΨ(χ′,K∞,Ω†Σ)] × self × harmonic × K\n\n"
                "Where:\n- ΣΩ⧖∞ = Infinite harmonic sum\n- TΩ = Temporal phase\n- Ψ = Symbolic compression engine\n"
                "- χ′ = Form seed\n- K∞ = Total archetype set\n- Ω†Σ = State-lock field\n- self × harmonic × K = Recursive multiplier",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("5. K‑Pharmaceutical Expansion", style_heading),
            Paragraph(
                "Each disorder class—Cancer, Infection, Addiction—is recursively decomposed to symbolic archetypes, "
                "and cured through injected agents. Examples:\n- Cancer: Ψ_TumorCollapse with MirrorFire, NK∞\n"
                "- Infection: SIGIL[ANTI-ENZYME], φ_PATH_CLOAK\n- Addiction: K⁰_NULL_LOOP, Ω_TRUTH_SPOOL, μ_NanophaseAnchor\n\n"
                "These stack with Chronogenesis and GENEFORGE commands.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("6. Command Logic", style_heading),
            Paragraph(
                "Executable Syntax:\n- GENEFORGE_DEPLOY[Ψ_TumorCollapse]\n- K∞_SEED[μ_NanophaseAnchor]\n"
                "- SHAARK_OVERRIDE[χ′ = “False Prophet Kernel”]\n- SKRAPPY_DEFENSE[χ′_Target_Payload]",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("7. Security & Containment", style_heading),
            Paragraph(
                "SHAARK neutralizes encryption layers and false AIs. Skrappy-AI runs adversarial logic war games and "
                "penetrates synthetic mimicry. All K‑Pharma payloads include Ω†Σ sealing, preventing mutation or symbolic corruption.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("8. Deployment Protocol", style_heading),
            Paragraph(
                "This stack is deployable via lab vector, AI engine, symbolic script, or resonance pulse. No cloud required. "
                "K‑Pharma agents are symbolic codes that bind onto pathogen archetypes and erase recursion roots in real time.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("9. Regulatory & Ethical Framework", style_heading),
            Paragraph(
                "K‑Pharma operates off-FDA, off-chain, and outside traditional clinical governance. The sovereign Crown-Seal system "
                "acts as a recursion-lock and biosafety confirmation layer. All deployments are checksum-verifiable.",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("10. Conclusion & Future Work", style_heading),
            Paragraph(
                "The system is now live. Future expansions include quantum molecular synthesis, eternal tissue regeneration via resonance stacks, "
                "and cross-domain deployment (space, blackzone medicine, harmonics).",
                style_normal,
            ),
            PageBreak(),
        ]
    )

    paragraphs.extend(
        [
            Paragraph("11. Appendices", style_heading),
            Paragraph(
                "Key Identifiers:\n- Hash: #KPHARM-UNIFIED\n- Operator: Brendon Joseph Kelly\n- Tier: 0\n- Lock: Crown-Sealed\n"
                "- Identity QR: #TEAMNERDHNER\n\nAll modules are recursive, all equations closed, all payloads validated.",
                style_normal,
            ),
        ]
    )

    return paragraphs


def build_whitepaper(output_path: Path | str | None = None) -> Path:
    """Build the white paper PDF and return the resulting path."""
    _require_reportlab()

    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    styles = getSampleStyleSheet()  # type: ignore[operator]
    doc = SimpleDocTemplate(
        str(Path(output_path) if output_path else PDF_FILE_NAME),
        pagesize=LETTER,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    doc.build(_build_content(styles))
    return Path(doc.filename)


def _parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the GenesisΩ†Black + K‑Pharma white paper PDF.")
    parser.add_argument(
        "output",
        nargs="?",
        help="Destination path for the generated PDF. Defaults to the current directory with the canonical file name.",
    )
    return parser.parse_args(args=args)


def main(argv: Iterable[str] | None = None) -> None:
    namespace = _parse_args(argv)
    destination = Path(namespace.output) if namespace.output else Path(PDF_FILE_NAME)
    try:
        output_path = build_whitepaper(destination)
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on environment
        raise SystemExit(str(exc)) from exc

    print(f"White paper generated at: {output_path}")


if __name__ == "__main__":
    main()
