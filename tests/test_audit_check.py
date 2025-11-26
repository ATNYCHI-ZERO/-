from __future__ import annotations

import hashlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import audit_check


def test_iter_repository_files_skips_hidden(tmp_path):
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    visible_dir = tmp_path / "visible"
    visible_dir.mkdir()

    visible_file = visible_dir / "artifact.txt"
    visible_file.write_text("audit", encoding="utf-8")
    hidden_file = hidden_dir / "secret.txt"
    hidden_file.write_text("ignore", encoding="utf-8")

    discovered = list(audit_check.iter_repository_files(tmp_path))

    assert visible_file in discovered
    assert hidden_file not in discovered


def test_file_report_streams_large_files(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_check, "ROOT", tmp_path)

    payload = b"DARPA" * 100_000
    artifact = tmp_path / "large.bin"
    artifact.write_bytes(payload)

    report = audit_check.file_report(artifact)

    assert report.path == "large.bin"
    assert report.size == len(payload)
    assert report.sha256 == hashlib.sha256(payload).hexdigest()
