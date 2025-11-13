import pathlib

import pytest


@pytest.mark.parametrize(
    "path, expected_title",
    [
        (pathlib.Path("README.md"), "pi"),
        (
            pathlib.Path("docs/recursive_identity_white_paper.md"),
            "Recursive Identity and the Collapse of Vortex Symbolism into k₁",
        ),
        (
            pathlib.Path("docs/bitcoin_internet_currency_white_paper.md"),
            "Bitcoin as the Native Currency of the Internet",
        ),
    ],
)
def test_document_headers(path: pathlib.Path, expected_title: str) -> None:
    """Ensure key documentation headers remain intact for audit readiness."""
    assert path.exists(), f"Expected documentation at {path}"

    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    assert expected_title in first_line
