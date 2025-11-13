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


def test_collect_file_audit_records_excludes_pytest_cache():
    pytest_cache_dir = repo_root / ".pytest_cache"
    pytest_cache_dir.mkdir(exist_ok=True)
    marker_file = pytest_cache_dir / "tmp_audit_marker.txt"
    marker_file.write_text("darpa", encoding="utf-8")

    try:
        records = collect_file_audit_records(repo_root)
        assert all(".pytest_cache" not in record.path.parts for record in records)
    finally:
        marker_file.unlink(missing_ok=True)
