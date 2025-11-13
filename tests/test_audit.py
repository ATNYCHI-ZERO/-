from pathlib import Path

from audit import audit_repository


def test_audit_reads_readme(tmp_path: Path):
    # Copy README into temporary directory to ensure isolation.
    repo_root = tmp_path
    readme_content = Path("README.md").read_bytes()
    (repo_root / "README.md").write_bytes(readme_content)

    report = audit_repository(repo_root)

    assert report.total_files == 1
    result = report.files[0]
    assert result.path == "README.md"
    assert result.readable is True
    assert result.size_bytes == len(readme_content)
    # Ensure hashing is deterministic and non-empty.
    assert len(result.sha256) == 64
