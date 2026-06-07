import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _configure_validator(tmp_path, monkeypatch, expected_files, manifest_files=None):
    (tmp_path / "config").mkdir()
    (tmp_path / "logs").mkdir()
    _write_json(tmp_path / "config" / "expected_outputs.json", {"files": expected_files})
    _write_json(tmp_path / "logs" / "actual_manifest.json", {"files": manifest_files or []})
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"expected output\n"
    expected_hash = _sha256_bytes(expected_bytes)
    output_path = tmp_path / "outputs" / "required.txt"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"corrupted output\n")

    _configure_validator(
        tmp_path,
        monkeypatch,
        expected_files=[
            {"path": "outputs/required.txt", "sha256": expected_hash, "required": True}
        ],
        manifest_files=[
            {
                "path": "outputs/required.txt",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert "Hash mismatch for outputs/required.txt" in failures[0]


def test_validate_checks_live_presence_not_stale_manifest(tmp_path, monkeypatch):
    expected_hash = _sha256_bytes(b"expected output\n")
    _configure_validator(
        tmp_path,
        monkeypatch,
        expected_files=[
            {"path": "outputs/missing.txt", "sha256": expected_hash, "required": True}
        ],
        manifest_files=[
            {
                "path": "outputs/missing.txt",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.txt"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _configure_validator(
        tmp_path,
        monkeypatch,
        expected_files=[
            {"path": "outputs/optional.json", "sha256": "", "required": False}
        ],
    )

    assert validate_outputs.validate() == []


def test_validate_accepts_matching_live_output(tmp_path, monkeypatch):
    output_bytes = b"expected output\n"
    output_path = tmp_path / "outputs" / "required.txt"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(output_bytes)
    _configure_validator(
        tmp_path,
        monkeypatch,
        expected_files=[
            {
                "path": "outputs/required.txt",
                "sha256": _sha256_bytes(output_bytes),
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == []
