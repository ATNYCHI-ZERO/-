import json
from pathlib import Path
import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import hashlib

import json

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


def test_collect_file_audit_records_respects_excluded_dirs(tmp_path):
    keep = tmp_path / "keep.txt"
    keep.write_text("keep")
    ignored_dir = tmp_path / "ignored"
    ignored_dir.mkdir()
    ignored_file = ignored_dir / "ignored.txt"
    ignored_file.write_text("ignore me")

    records = collect_file_audit_records(tmp_path, excluded_dirs={"ignored"})
    recorded_paths = {record.path for record in records}

    assert keep in recorded_paths
    assert ignored_file not in recorded_paths


def test_cli_exclude_flag(tmp_path, capsys):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "keep.txt").write_text("keep")
    skip_dir = root / "skip"
    skip_dir.mkdir()
    (skip_dir / "skip.txt").write_text("skip")
    output = tmp_path / "report.json"

    exit_code = main(["--root", str(root), "--output", str(output), "--exclude", "skip"])

    assert exit_code == 0
    payload = json.loads(output.read_text())
    audited_files = {entry["path"] for entry in payload["files"]}
    assert "keep.txt" in audited_files
    assert "skip/skip.txt" not in audited_files

    captured = json.loads(capsys.readouterr().out)
    emitted_paths = {entry["path"] for entry in captured}
    assert any("keep.txt" in str(path) for path in emitted_paths)
    assert all("skip/skip.txt" not in str(path) for path in emitted_paths)
