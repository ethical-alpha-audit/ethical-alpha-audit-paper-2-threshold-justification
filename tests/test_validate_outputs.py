import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import validate_outputs  # noqa: E402


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_output_files(monkeypatch, tmp_path):
    """Validation must not trust a stale checked-in manifest."""
    expected_bytes = b"expected output\n"
    actual_bytes = b"corrupted output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(actual_bytes)

    config_dir = tmp_path / "config"
    logs_dir = tmp_path / "logs"
    config_dir.mkdir()
    logs_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/table.csv",
                        "sha256": _sha256(expected_bytes),
                        "required": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/table.csv",
                        "sha256": _sha256(expected_bytes),
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
    assert _sha256(actual_bytes) in failures[0]


def test_validate_ignores_missing_optional_outputs(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/optional.json",
                        "sha256": "",
                        "required": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
