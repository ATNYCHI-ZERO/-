import json
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records, format_audit_records


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_format_audit_records_json_output():
    records = collect_file_audit_records(repo_root)
    payload = json.loads(
        format_audit_records(records, root=repo_root, output_format="json")
    )

    assert isinstance(payload, list)
    assert payload, "JSON payload should include at least one file entry"

    readme_entries = [
        entry for entry in payload if entry["path"].endswith("README.md")
    ]
    assert readme_entries, "README.md entry should be present in JSON payload"


def test_format_audit_records_text_output_contains_header():
    records = collect_file_audit_records(repo_root)
    output = format_audit_records(records, root=repo_root)

    assert output.startswith("DARPA Repository Audit Summary")
    assert "SHA256=" in output
