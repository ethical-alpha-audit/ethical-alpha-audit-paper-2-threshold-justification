import hashlib
import json

import scripts.validate_outputs as validate_outputs


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected(root, path, expected_hash, required=True):
    config_dir = root / "config"
    config_dir.mkdir()
    expected = {
        "files": [
            {
                "path": path,
                "sha256": expected_hash,
                "required": required,
            }
        ]
    }
    (config_dir / "expected_outputs.json").write_text(
        json.dumps(expected),
        encoding="utf-8",
    )


def _write_stale_manifest(root, path, expected_hash, exists=True):
    logs_dir = root / "logs"
    logs_dir.mkdir()
    manifest = {
        "files": [
            {
                "path": path,
                "sha256": expected_hash,
                "exists": exists,
            }
        ]
    }
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_bytes = b"correct\n"
    corrupt_bytes = b"corrupt\n"
    expected_hash = _sha256(expected_bytes)

    _write_expected(tmp_path, output_path, expected_hash)
    _write_stale_manifest(tmp_path, output_path, expected_hash)
    live_output = tmp_path / output_path
    live_output.parent.mkdir(parents=True)
    live_output.write_bytes(corrupt_bytes)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        "Hash mismatch for outputs/table.csv: "
        f"expected {expected_hash}, got {_sha256(corrupt_bytes)}"
    ]


def test_validate_checks_live_required_output_presence(tmp_path, monkeypatch):
    output_path = "outputs/missing.csv"
    expected_hash = _sha256(b"expected\n")

    _write_expected(tmp_path, output_path, expected_hash)
    _write_stale_manifest(tmp_path, output_path, expected_hash, exists=True)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    output_path = "outputs/optional.json"

    _write_expected(tmp_path, output_path, "", required=False)
    _write_stale_manifest(tmp_path, output_path, "", exists=False)

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
