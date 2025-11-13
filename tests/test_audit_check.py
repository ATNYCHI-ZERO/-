from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from audit_check import ROOT, generate_report, iter_repository_files


def test_iter_repository_files_includes_readme() -> None:
    files = list(iter_repository_files(ROOT))
    readme_path = ROOT / "README.md"

    assert readme_path in files, "README.md should be part of the audit walk"


def test_generate_report_serializable() -> None:
    reports = generate_report([ROOT / "README.md"])
    assert reports, "Expected README.md to produce an audit report entry"

    # Ensure the dataclass can be serialized to JSON for DARPA exports.
    payload = [report.__dict__ for report in reports]
    encoded = json.dumps(payload)

    assert "README.md" in encoded
