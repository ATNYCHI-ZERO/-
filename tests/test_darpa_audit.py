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


def test_iter_repository_files_excludes_pytest_cache(tmp_path):
    cache_dir = tmp_path / ".pytest_cache"
    cache_dir.mkdir()
    cached_file = cache_dir / "state.txt"
    cached_file.write_text("cache", encoding="utf-8")

    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("keep", encoding="utf-8")

    discovered = list(iter_repository_files(tmp_path))

    assert keep_file in discovered
    assert cached_file not in discovered
