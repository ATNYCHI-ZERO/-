from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import hashlib

from darpa_audit import (
    build_file_audit,
    collect_file_audit_records,
    compute_repository_digest,
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


def test_compute_repository_digest_is_stable(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("alpha", encoding="utf-8")
    file_b.write_text("beta", encoding="utf-8")

    records = collect_file_audit_records(tmp_path)
    digest = compute_repository_digest(records, root=tmp_path)

    # Reversing the records should not alter the aggregate digest because the
    # helper sorts paths prior to combining the individual checksums.
    reversed_digest = compute_repository_digest(list(reversed(records)), root=tmp_path)

    assert digest == reversed_digest

    file_b.write_text("beta+delta", encoding="utf-8")
    updated_records = collect_file_audit_records(tmp_path)
    assert compute_repository_digest(updated_records, root=tmp_path) != digest
