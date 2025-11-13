from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records, summarize_records


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_collect_file_audit_records_respects_excluded_dirs():
    records = collect_file_audit_records(repo_root, excluded_dirs={"docs"})

    docs_dir = repo_root / "docs"
    assert all(docs_dir not in record.path.parents for record in records)


def test_summarize_records_matches_manual_calculation():
    records = collect_file_audit_records(repo_root)
    summary = summarize_records(records)

    assert summary.file_count == len(records)
    assert summary.total_bytes == sum(record.size for record in records)
