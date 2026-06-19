import hashlib
import json

from scripts import validate_outputs


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected(root, files):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}, indent=2),
        encoding="utf-8",
    )


def _write_stale_manifest(root, files):
    logs_dir = root / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": files}, indent=2),
        encoding="utf-8",
    )


def test_validate_hashes_live_file_not_stale_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    expected_bytes = b"expected data\n"
    output.write_bytes(b"corrupted data\n")
    expected_hash = _sha256(expected_bytes)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        (
            "Hash mismatch for outputs/table.csv: "
            f"expected {expected_hash}, got {_sha256(b'corrupted data\\n')}"
        )
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    expected_hash = _sha256(b"expected data\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_passes_live_matching_output_without_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    data = b"expected data\n"
    output.write_bytes(data)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": _sha256(data),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
