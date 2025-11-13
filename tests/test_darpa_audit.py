from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from darpa_audit import collect_file_audit_records


def test_collect_file_audit_records_includes_readme():
    records = collect_file_audit_records(repo_root)
    readme = [record for record in records if record.path.name == "README.md"]

    assert readme, "README.md should be discovered during the audit"
    assert readme[0].size > 0
    assert len(readme[0].sha256) == 64


def test_collect_file_audit_records_skips_hidden_paths(tmp_path: Path) -> None:
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "secret.txt").write_text("hidden", encoding="utf-8")

    visible_dir = tmp_path / "visible"
    visible_dir.mkdir()
    (visible_dir / "file.txt").write_text("visible", encoding="utf-8")

    (tmp_path / ".hidden_file").write_text("hidden root", encoding="utf-8")
    (tmp_path / "root.txt").write_text("root", encoding="utf-8")

    records = collect_file_audit_records(tmp_path, excluded_dirs=[])
    audited = {record.path.relative_to(tmp_path) for record in records}

    assert Path("visible/file.txt") in audited
    assert Path("root.txt") in audited
    assert Path(".hidden/secret.txt") not in audited
    assert Path(".hidden_file") not in audited
