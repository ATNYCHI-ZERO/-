from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import DEFAULT_EXCLUDED_DIRS, collect_file_audit_records


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_collect_file_audit_records_respects_additional_exclusions():
    records = collect_file_audit_records(
        repo_root, excluded_dirs=set(DEFAULT_EXCLUDED_DIRS) | {"docs"}
    )

    assert all("docs" not in record.path.relative_to(repo_root).parts for record in records)
