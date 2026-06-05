import hashlib
import json

from scripts import validate_outputs


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _expected_config(*items):
    return {"files": list(items)}


def _file_item(path, sha256, required=True):
    return {"path": path, "sha256": sha256, "required": required}


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_file_not_stale_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
    output_path = tmp_path / "outputs" / "tables" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"corrupted\n")

    expected_hash = _sha256_bytes(b"expected\n")
    stale_manifest_hash = expected_hash
    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        _expected_config(_file_item("outputs/tables/table.csv", expected_hash)),
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/tables/table.csv", "sha256": stale_manifest_hash, "exists": True}]},
    )

    failures = validate_outputs.validate()
    corrupt_hash = _sha256_bytes(b"corrupted\n")

    assert failures == [
        "Hash mismatch for outputs/tables/table.csv: "
        f"expected {expected_hash}, got {corrupt_hash}"
    ]


def test_validate_checks_live_missing_required_output(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
    expected_hash = _sha256_bytes(b"expected\n")
    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        _expected_config(_file_item("outputs/tables/missing.csv", expected_hash)),
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": "outputs/tables/missing.csv", "sha256": expected_hash, "exists": True}]},
    )

    assert validate_outputs.validate() == ["Missing required output: outputs/tables/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        _expected_config(_file_item("outputs/sensitivity/run_metadata.json", "", required=False)),
    )

    assert validate_outputs.validate() == []
