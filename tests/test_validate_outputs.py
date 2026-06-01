import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _configure_expected(root: Path, files: list[dict]) -> None:
    _write_json(root / "config" / "expected_outputs.json", {"files": files})


def _write_stale_manifest(root: Path, files: list[dict]) -> None:
    _write_json(root / "logs" / "actual_manifest.json", {"files": files})


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "tables" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"corrupted output\n")
    expected_hash = _sha256(b"expected output\n")

    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/tables/table.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert "Hash mismatch for outputs/tables/table.csv" in failures[0]
    assert _sha256(b"corrupted output\n") in failures[0]


def test_validate_checks_live_required_file_existence(tmp_path, monkeypatch):
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/missing.csv",
                "sha256": _sha256(b"expected output\n"),
                "required": True,
            }
        ],
    )
    _write_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/tables/missing.csv",
                "sha256": _sha256(b"expected output\n"),
                "exists": True,
            }
        ],
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/tables/missing.csv"]


def test_validate_allows_missing_optional_outputs(tmp_path, monkeypatch):
    _configure_expected(
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
