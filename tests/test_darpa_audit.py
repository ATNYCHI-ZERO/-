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


def test_iter_repository_files_skips_excluded_directories(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("dummy", encoding="utf-8")

    safe_file = tmp_path / "notes.txt"
    safe_file.write_text("audit", encoding="utf-8")

    discovered = list(iter_repository_files(tmp_path))
    relative_paths = {path.relative_to(tmp_path).as_posix() for path in discovered}

    assert "notes.txt" in relative_paths
    assert all(".git" not in path for path in relative_paths)
