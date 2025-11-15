import json
from pathlib import Path
import sys
from pathlib import Path


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


def test_main_generates_json_report(tmp_path, capsys):
    root = tmp_path / "repo"
    root.mkdir()
    target = root / "file.txt"
    target.write_text("classified", encoding="utf-8")

    output = tmp_path / "report.json"
    exit_code = main(["--root", str(root), "--output", str(output)])

    assert exit_code == 0
    assert output.exists()

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["file_count"] == 1
    assert payload["files"][0]["path"] == "file.txt"

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload == payload
