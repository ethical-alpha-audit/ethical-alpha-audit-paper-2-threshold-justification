import hashlib
import json
from pathlib import Path

from scripts.validate_outputs import validate


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def expected_config(path: str, sha256: str, required: bool = True) -> dict:
    return {"files": [{"path": path, "sha256": sha256, "required": required}]}


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("corrupted,data\n", encoding="utf-8")

    expected_sha = hashlib.sha256(b"correct,data\n").hexdigest()
    write_json(
        tmp_path / "config" / "expected_outputs.json",
        expected_config("outputs/result.csv", expected_sha),
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/result.csv",
                    "sha256": expected_sha,
                    "exists": True,
                }
            ]
        },
    )

    failures = validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv")


def test_validate_reports_missing_required_output_despite_stale_manifest(tmp_path):
    expected_sha = hashlib.sha256(b"expected\n").hexdigest()
    write_json(
        tmp_path / "config" / "expected_outputs.json",
        expected_config("outputs/missing.csv", expected_sha),
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/missing.csv",
                    "sha256": expected_sha,
                    "exists": True,
                }
            ]
        },
    )

    assert validate(tmp_path) == ["Missing required output: outputs/missing.csv"]
