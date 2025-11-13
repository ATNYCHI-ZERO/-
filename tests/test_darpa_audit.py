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


def test_iter_repository_files_can_include_hidden(tmp_path):
    hidden = tmp_path / ".secret.txt"
    hidden.write_text("hidden", encoding="utf-8")

    visible = tmp_path / "visible.txt"
    visible.write_text("visible", encoding="utf-8")

    default_files = list(iter_repository_files(tmp_path))
    assert visible in default_files
    assert hidden not in default_files

    with_hidden = list(iter_repository_files(tmp_path, include_hidden=True))
    assert hidden in with_hidden
