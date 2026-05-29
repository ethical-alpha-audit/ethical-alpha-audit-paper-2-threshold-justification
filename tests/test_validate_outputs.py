import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected_outputs(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}, indent=2),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    expected_payload = b"canonical output\n"
    output_path.write_bytes(b"corrupted output\n")
    _write_expected_outputs(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": _sha256_bytes(expected_payload),
                "required": True,
            }
        ],
    )
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/table.csv",
                        "sha256": _sha256_bytes(expected_payload),
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
    assert failures[0].startswith("Hash mismatch for outputs/table.csv")


def test_validate_reports_live_missing_required_output(tmp_path, monkeypatch):
    _write_expected_outputs(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256_bytes(b"canonical output\n"),
                "required": True,
            }
        ],
    )
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/missing.csv",
                        "sha256": _sha256_bytes(b"canonical output\n"),
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _write_expected_outputs(
        tmp_path,
        [
            {
                "path": "outputs/optional.json",
                "sha256": _sha256_bytes(b"variable metadata\n"),
                "required": False,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
