import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_outputs.py"
SPEC = importlib.util.spec_from_file_location("validate_outputs", MODULE_PATH)
validate_outputs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_outputs)


def _write_expected(root: Path, path: str, content: bytes, required: bool = True) -> None:
    (root / "config").mkdir()
    expected_hash = hashlib.sha256(content).hexdigest()
    config = {"files": [{"path": path, "sha256": expected_hash, "required": required}]}
    (root / "config" / "expected_outputs.json").write_text(json.dumps(config), encoding="utf-8")


def _write_stale_manifest(root: Path, path: str, content: bytes, exists: bool = True) -> None:
    (root / "logs").mkdir()
    stale_hash = hashlib.sha256(content).hexdigest()
    manifest = {"files": [{"path": path, "sha256": stale_hash, "exists": exists}]}
    (root / "logs" / "actual_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_content = b"expected output\n"
    _write_expected(tmp_path, output_path, expected_content)
    _write_stale_manifest(tmp_path, output_path, expected_content)

    live_path = tmp_path / output_path
    live_path.parent.mkdir()
    live_path.write_bytes(b"corrupted output\n")

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {output_path}:")


def test_validate_reports_missing_required_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_content = b"expected output\n"
    _write_expected(tmp_path, output_path, expected_content)
    _write_stale_manifest(tmp_path, output_path, expected_content)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    output_path = "outputs/run_metadata.json"
    _write_expected(tmp_path, output_path, b"variable metadata\n", required=False)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_passes_when_live_output_matches_expected_hash(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_content = b"expected output\n"
    _write_expected(tmp_path, output_path, expected_content)

    live_path = tmp_path / output_path
    live_path.parent.mkdir()
    live_path.write_bytes(expected_content)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
