import json
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


def test_collect_file_audit_records_respects_custom_excludes(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    included = root / "keep.txt"
    included.write_text("retain", encoding="utf-8")
    excluded_dir = root / "skip"
    excluded_dir.mkdir()
    (excluded_dir / "ignore.txt").write_text("omit", encoding="utf-8")

    records = collect_file_audit_records(root, excluded_dirs={"skip"})

    audited_paths = {record.path for record in records}
    assert included in audited_paths
    assert all("skip" not in path.parts for path in audited_paths)


def test_cli_respects_exclude_argument(tmp_path, monkeypatch, capsys):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "included.txt").write_text("hello", encoding="utf-8")
    (root / "ignore_me").mkdir()
    (root / "ignore_me" / "data.txt").write_text("world", encoding="utf-8")

    output_path = tmp_path / "report.json"

    exit_code = main(
        [
            "--root",
            str(root),
            "--output",
            str(output_path),
            "--exclude",
            "ignore_me",
        ]
    )

    assert exit_code == 0

    stdout = capsys.readouterr().out
    records = json.loads(stdout)
    assert all("ignore_me" not in entry["path"] for entry in records)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["file_count"] == 1
    assert payload["files"][0]["path"] == "included.txt"
