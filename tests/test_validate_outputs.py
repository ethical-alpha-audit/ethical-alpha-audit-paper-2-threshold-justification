import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _configure_expected(base: Path, files: list[dict]) -> None:
    _write_json(base / "config" / "expected_outputs.json", {"files": files})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    live_path = tmp_path / "outputs" / "result.csv"
    live_path.parent.mkdir(parents=True)
    expected_bytes = b"expected scientific output\n"
    live_path.write_bytes(b"corrupted live output\n")
    expected_hash = _sha256(expected_bytes)
    _configure_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": expected_hash, "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/result.csv", "sha256": expected_hash, "exists": True}]},
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()
    corrupted_hash = _sha256(b"corrupted live output\n")

    assert failures == [
        f"Hash mismatch for outputs/result.csv: expected {expected_hash}, got {corrupted_hash}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    _configure_expected(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": _sha256(b"expected\n"), "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/missing.csv", "sha256": _sha256(b"expected\n"), "exists": True}]},
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _configure_expected(
        tmp_path,
        [{"path": "outputs/runtime_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path, monkeypatch):
    live_path = tmp_path / "outputs" / "result.csv"
    live_path.parent.mkdir(parents=True)
    live_path.write_text("present but unpinned\n", encoding="utf-8")
    _configure_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Missing expected SHA-256 for required output: outputs/result.csv"
    ]
