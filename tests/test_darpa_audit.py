import json
import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import hashlib

from darpa_audit import (
    _serialise_record,
    build_file_audit,
    collect_file_audit_records,
    main,
)


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


def test_serialise_record_normalises_paths(tmp_path):
    (tmp_path / "nested").mkdir()
    target = tmp_path / "nested" / "artifact.bin"
    target.write_bytes(b"payload")

    record = build_file_audit(target)
    serialised = _serialise_record(record, root=tmp_path)

    assert serialised["path"] == "nested/artifact.bin"
    assert serialised["size"] == record.size
    assert serialised["sha256"] == record.sha256


def test_normalise_path_resolves_relative_segments(tmp_path):
    nested = tmp_path / "nested" / ".." / "artifact.bin"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text("payload")

    record = build_file_audit(nested)
    serialised = _serialise_record(record, root=tmp_path)

    assert serialised["path"] == "artifact.bin"


def test_serialise_record_allows_size_key_override(tmp_path):
    target = tmp_path / "artifact.bin"
    target.write_bytes(b"payload")

    record = build_file_audit(target)
    serialised = _serialise_record(record, root=tmp_path, size_key="size_bytes")

    assert "size" not in serialised
    assert serialised["size_bytes"] == record.size
