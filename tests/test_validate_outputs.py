import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_content = b"expected output\n"
    expected_hash = _sha256_bytes(expected_content)

    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"corrupted output\n")

    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/result.csv",
                    "sha256": expected_hash,
                    "required": True,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/result.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        f"Hash mismatch for outputs/result.csv: expected {expected_hash}, got {_sha256_bytes(b'corrupted output\n')}"
    ]


def test_validate_reports_missing_live_required_output_despite_stale_manifest(tmp_path, monkeypatch):
    expected_hash = _sha256_bytes(b"expected output\n")

    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/result.csv",
                    "sha256": expected_hash,
                    "required": True,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/result.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/result.csv"]
