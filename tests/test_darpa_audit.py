from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records, iter_repository_files


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_iter_repository_files_skips_excluded_dirs(tmp_path):
    """Ensure excluded directories are never walked during the audit."""

    excluded_dir = tmp_path / ".git"
    excluded_dir.mkdir()
    (excluded_dir / "ignored.txt").write_text("ignore me", encoding="utf-8")

    included_dir = tmp_path / "docs"
    included_dir.mkdir()
    expected_file = included_dir / "note.txt"
    expected_file.write_text("important", encoding="utf-8")

    files = list(iter_repository_files(tmp_path, excluded_dirs={".git"}))

    assert expected_file in files
    assert not any(".git" in str(path) for path in files)
