from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import hashlib

from darpa_audit import (
    build_file_audit,
    collect_file_audit_records,
    iter_repository_files,
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


def test_iter_repository_files_allows_custom_exclusions(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    allowed_artifact = allowed / "keep.txt"
    allowed_artifact.write_text("retain", encoding="utf-8")

    skipped = tmp_path / "skip_me"
    skipped.mkdir()
    skipped_artifact = skipped / "ignore.txt"
    skipped_artifact.write_text("ignore", encoding="utf-8")

    discovered = list(iter_repository_files(tmp_path, excluded_dirs={"skip_me"}))

    relative_paths = {path.relative_to(tmp_path) for path in discovered}

    assert allowed_artifact.relative_to(tmp_path) in relative_paths
    assert skipped_artifact.relative_to(tmp_path) not in relative_paths
