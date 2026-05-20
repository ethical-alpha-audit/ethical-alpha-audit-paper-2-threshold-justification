import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"approved output\n"
    expected_hash = hashlib.sha256(expected_bytes).hexdigest()
    output_path = tmp_path / "outputs" / "tables" / "result.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"tampered output\n")

    write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/tables/result.csv",
                    "sha256": expected_hash,
                    "required": True,
                }
            ]
        },
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/result.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/tables/result.csv")


def test_validate_reports_live_required_output_missing(tmp_path, monkeypatch):
    write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/tables/missing.csv",
                    "sha256": hashlib.sha256(b"expected\n").hexdigest(),
                    "required": True,
                },
                {
                    "path": "outputs/sensitivity/run_metadata.json",
                    "sha256": "",
                    "required": False,
                },
            ]
        },
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/missing.csv",
                    "sha256": hashlib.sha256(b"expected\n").hexdigest(),
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/tables/missing.csv"]
