import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _configure_expected(root: Path, files: list[dict]) -> None:
    _write_json(root / "config" / "expected_outputs.json", {"files": files})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"reviewer-approved output\n"
    corrupted_bytes = b"corrupted output\n"
    expected_hash = _sha256(expected_bytes)
    corrupted_hash = _sha256(corrupted_bytes)
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(corrupted_bytes)
    _configure_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": expected_hash, "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/table.csv", "sha256": expected_hash, "exists": True}]},
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        f"Hash mismatch for outputs/table.csv: expected {expected_hash}, got {corrupted_hash}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    expected_hash = _sha256(b"expected output\n")
    _configure_expected(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": expected_hash, "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/missing.csv", "sha256": expected_hash, "exists": True}]},
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _configure_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "required.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("required output\n", encoding="utf-8")
    _configure_expected(
        tmp_path,
        [{"path": "outputs/required.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Required output has no expected SHA-256: outputs/required.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output_bytes = b"matching output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(output_bytes)
    _configure_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": _sha256(output_bytes), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
