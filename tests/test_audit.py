import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from audit import run_audit, REPO_ROOT


class AuditTests(unittest.TestCase):
    def test_audit_includes_readme(self) -> None:
        report = run_audit(REPO_ROOT)
        readme_relpath = Path("README.md")
        audited_paths = {result.path for result in report.files}
        self.assertIn(readme_relpath, audited_paths, "README should be part of the audit results")

    def test_audit_reports_hashes(self) -> None:
        report = run_audit(REPO_ROOT)
        self.assertTrue(all(len(result.sha256) == 64 for result in report.files), "Each file must include a SHA-256 digest")
