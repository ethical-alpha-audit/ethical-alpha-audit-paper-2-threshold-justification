import hashlib
import json

from scripts import validate_outputs


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected_outputs(base, files):
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _write_stale_manifest(base, path, sha256):
    logs_dir = base / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": path, "sha256": sha256, "exists": True}]}),
        encoding="utf-8",
    )


def test_validate_hashes_live_file_instead_of_trusting_stale_manifest(tmp_path, monkeypatch):
    path = "outputs/tables/table.csv"
    expected_bytes = b"correct\n"
    stale_hash = _sha256_bytes(expected_bytes)
    output_path = tmp_path / path
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"corrupted\n")
    _write_expected_outputs(
        tmp_path,
        [{"path": path, "sha256": stale_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, path, stale_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {path}: expected {stale_hash}, got ")


def test_validate_checks_live_required_file_existence(tmp_path, monkeypatch):
    path = "outputs/tables/missing.csv"
    stale_hash = _sha256_bytes(b"present in stale manifest\n")
    _write_expected_outputs(
        tmp_path,
        [{"path": path, "sha256": stale_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, path, stale_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [f"Missing required output: {path}"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _write_expected_outputs(
        tmp_path,
        [{"path": "outputs/sensitivity/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_passes_when_live_file_matches_expected_hash(tmp_path, monkeypatch):
    path = "outputs/tables/table.csv"
    output_path = tmp_path / path
    data = b"correct\n"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(data)
    _write_expected_outputs(
        tmp_path,
        [{"path": path, "sha256": _sha256_bytes(data), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
