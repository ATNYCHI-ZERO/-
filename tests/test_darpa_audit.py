import json
from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import hashlib

from darpa_audit import build_file_audit, collect_file_audit_records, main


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_build_file_audit_streams_content(tmp_path):
    payload = b"DARPA" * 100_000  # Large enough to require chunked reads in tests.
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(payload)

    record = build_file_audit(artifact)

    assert record.size == len(payload)
    assert record.sha256 == hashlib.sha256(payload).hexdigest()


def test_main_emits_json(tmp_path, capsys):
    output = tmp_path / "report.json"

    exit_code = main(["--root", str(repo_root), "--output", str(output)])

    assert exit_code == 0

    stdout = capsys.readouterr().out
    listing = json.loads(stdout)

    assert isinstance(listing, list)
    assert listing, "CLI output should include at least one record"
    assert isinstance(listing[0]["path"], str)
    assert isinstance(listing[0]["size"], int)
    assert isinstance(listing[0]["sha256"], str)

    report = json.loads(output.read_text())
    assert report["file_count"] == len(listing)
