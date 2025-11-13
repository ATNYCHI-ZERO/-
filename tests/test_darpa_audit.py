from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_collect_file_audit_records_excludes_pytest_cache(tmp_path: Path) -> None:
    cache_dir = tmp_path / ".pytest_cache"
    cache_dir.mkdir()
    (cache_dir / "ignored.txt").write_text("cached artifact", encoding="utf-8")
    tracked_file = tmp_path / "tracked.txt"
    tracked_file.write_text("tracked", encoding="utf-8")

    records = collect_file_audit_records(tmp_path)
    relative_paths = {record.path.relative_to(tmp_path) for record in records}

    assert Path("tracked.txt") in relative_paths
    assert Path(".pytest_cache/ignored.txt") not in relative_paths
