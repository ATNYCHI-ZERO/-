from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from audit import DocumentMetadata, extract_document_metadata, format_metadata_report, iter_audit_documents


def test_extract_document_metadata_reads_readme(tmp_path: Path):
    sample = tmp_path / "README.md"
    sample.write_text("# Heading\n\nContent", encoding="utf-8")

    metadata = extract_document_metadata(sample)

    assert metadata.path == sample
    assert metadata.line_count == 2
    assert metadata.headings == ("Heading",)


def test_extract_document_metadata_rejects_empty_file(tmp_path: Path):
    sample = tmp_path / "README.md"
    sample.write_text("\n\n", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_document_metadata(sample)


def test_iter_audit_documents_filters_non_markdown(tmp_path: Path):
    md_file = tmp_path / "doc.md"
    md_file.write_text("content", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    docs = list(iter_audit_documents([md_file, tmp_path / "notes.txt"]))

    assert len(docs) == 1
    assert docs[0].path == md_file


def test_format_metadata_report_includes_headings(tmp_path: Path):
    metadata = DocumentMetadata(path=tmp_path / "doc.md", line_count=5, headings=("One", "Two"))

    report = format_metadata_report(metadata)

    assert "Non-empty lines: 5" in report
    assert "Headings: One, Two" in report
