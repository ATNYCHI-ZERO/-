import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from audit import iter_repo_files, run_audit, REPO_ROOT as AUDIT_ROOT


class AuditTests(unittest.TestCase):
    def test_audit_includes_readme(self) -> None:
        report = run_audit(AUDIT_ROOT)
        readme_relpath = Path("README.md")
        audited_paths = {result.path for result in report.files}
        self.assertIn(readme_relpath, audited_paths, "README should be part of the audit results")

    def test_audit_reports_hashes(self) -> None:
        report = run_audit(AUDIT_ROOT)
        self.assertTrue(all(len(result.sha256) == 64 for result in report.files), "Each file must include a SHA-256 digest")


def test_iter_repo_files_is_sorted(tmp_path: Path) -> None:
    # Create files out of order to verify traversal order is deterministic.
    unordered_files = [tmp_path / name for name in ["b.txt", "a.txt", "c.txt"]]
    for file_path in unordered_files:
        file_path.write_text("audit", encoding="utf-8")

    discovered = list(iter_repo_files(tmp_path))
    assert [path.name for path in discovered] == sorted(path.name for path in unordered_files)
