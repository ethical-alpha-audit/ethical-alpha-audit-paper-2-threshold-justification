import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_outputs  # noqa: E402


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_expected_config(tmp_path: Path, files: list[dict]) -> None:
    _write_json(tmp_path / "config" / "expected_outputs.json", {"files": files})


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "tables" / "table.csv"
    output_path.parent.mkdir(parents=True)
    original_content = b"canonical output\n"
    output_path.write_bytes(b"corrupted output\n")
    expected_hash = _sha256(original_content)

    _write_expected_config(
        tmp_path,
        [
            {
                "path": "outputs/tables/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/table.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()
    corrupted_hash = _sha256(b"corrupted output\n")

    assert failures == [
        "Hash mismatch for outputs/tables/table.csv: "
        f"expected {expected_hash}, got {corrupted_hash}"
    ]


def test_validate_detects_missing_required_output_despite_stale_manifest(tmp_path, monkeypatch):
    expected_hash = _sha256(b"canonical output\n")
    _write_expected_config(
        tmp_path,
        [
            {
                "path": "outputs/tables/missing.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/missing.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/tables/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _write_expected_config(
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
