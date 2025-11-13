from pathlib import Path


def test_readme_exists_and_is_not_empty():
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    assert readme_path.is_file(), "README.md should exist at the repository root."
    assert readme_path.read_text(encoding="utf-8").strip(), "README.md should not be empty."
