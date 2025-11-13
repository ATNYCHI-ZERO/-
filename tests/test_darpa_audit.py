from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records
from audit_check import ROOT as AUDIT_ROOT, generate_report, iter_repository_files


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_audit_check_reports_readme_metadata():
    """The standalone audit script should report key repository assets."""

    files = list(iter_repository_files(AUDIT_ROOT))
    report = generate_report(files)

    readme_entries = [entry for entry in report if entry.path == "README.md"]
    assert readme_entries, "audit_check should include README.md in the report"

    entry = readme_entries[0]
    assert entry.size > 0
    assert len(entry.sha256) == 64
