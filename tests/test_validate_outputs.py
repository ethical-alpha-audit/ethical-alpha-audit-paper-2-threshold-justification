import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_expected(root: Path, entries):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}),
        encoding="utf-8",
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_live_output_hash_is_checked_even_when_manifest_is_stale(tmp_path, monkeypatch):
    expected_bytes = b"expected\n"
    corrupted_bytes = b"corrupted\n"
    output = tmp_path / "outputs" / "critical.csv"
    output.parent.mkdir()
    output.write_bytes(corrupted_bytes)
    expected_hash = _sha256(expected_bytes)
    _write_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": expected_hash, "required": True}],
    )

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/critical.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/critical.csv")


def test_missing_required_output_is_checked_against_live_files(tmp_path, monkeypatch):
    expected_hash = _sha256(b"expected\n")
    _write_expected(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": expected_hash, "required": True}],
    )
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/missing.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_missing_optional_output_is_allowed(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [{"path": "outputs/optional.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_valid_live_output_passes_without_manifest(tmp_path, monkeypatch):
    output_bytes = b"expected\n"
    output = tmp_path / "outputs" / "critical.csv"
    output.parent.mkdir()
    output.write_bytes(output_bytes)
    _write_expected(
        tmp_path,
        [{"path": "outputs/critical.csv", "sha256": _sha256(output_bytes), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
