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


def test_iter_repository_files_prunes_default_exclusions(tmp_path):
    excluded_dir = tmp_path / "venv" / "subdir"
    excluded_dir.mkdir(parents=True)
    (excluded_dir / "ignored.txt").write_text("ignore me", encoding="utf-8")

    included_file = tmp_path / "kept.txt"
    included_file.write_text("retain", encoding="utf-8")

    discovered = {path.relative_to(tmp_path) for path in iter_repository_files(tmp_path)}

    assert included_file.relative_to(tmp_path) in discovered
    assert all("ignored.txt" not in str(path) for path in discovered)
