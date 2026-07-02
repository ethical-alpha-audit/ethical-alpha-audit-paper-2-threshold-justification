import hashlib
import json

import scripts.validate_outputs as validator


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _set_expected(root, files):
    _write_json(root / "config" / "expected_outputs.json", {"files": files})


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("corrupted\n", encoding="utf-8")
    expected_hash = _sha256_text("canonical\n")
    corrupted_hash = _sha256_text("corrupted\n")
    _set_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": expected_hash, "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/critical.csv", "sha256": expected_hash, "exists": True}]},
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    failures = validator.validate()

    assert failures == [
        "Hash mismatch for outputs/critical.csv: "
        f"expected {expected_hash}, got {corrupted_hash}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    expected_hash = _sha256_text("canonical\n")
    _set_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": expected_hash, "required": True}],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/critical.csv", "sha256": expected_hash, "exists": True}]},
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == ["Missing required output: outputs/critical.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _set_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_rejects_required_unpinned_output(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("canonical\n", encoding="utf-8")
    _set_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [
        "Missing expected SHA-256 for required output: outputs/critical.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("canonical\n", encoding="utf-8")
    _set_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": _sha256_text("canonical\n"), "required": True}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
