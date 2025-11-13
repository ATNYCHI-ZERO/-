from pathlib import Path

import pytest

_reportlab = pytest.importorskip("reportlab")

from generate_whitepaper import PDF_FILE_NAME, build_whitepaper  # noqa: E402


def test_build_whitepaper_creates_pdf(tmp_path: Path) -> None:
    output_path = tmp_path / PDF_FILE_NAME
    path = build_whitepaper(output_path)
    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.parametrize("relative", [None, PDF_FILE_NAME])
def test_default_output_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative):
    monkeypatch.chdir(tmp_path)
    if relative is None:
        output_path = build_whitepaper()
        expected = tmp_path / PDF_FILE_NAME
    else:
        output_path = build_whitepaper(relative)
        expected = tmp_path / relative

    assert output_path == expected
    assert output_path.exists()
    assert output_path.stat().st_size > 0
