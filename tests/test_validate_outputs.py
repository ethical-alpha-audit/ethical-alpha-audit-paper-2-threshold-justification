import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validator


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def configure_repo(tmp_path, expected_files):
    (tmp_path / "logs").mkdir()
    write_json(tmp_path / "config" / "expected_outputs.json", {"files": expected_files})
    write_json(tmp_path / "logs" / "actual_manifest.json", {"files": []})


def run_validate(tmp_path, monkeypatch):
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)
    return validator.validate()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"approved output\n"
    actual_bytes = b"corrupted live output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(actual_bytes)
    configure_repo(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": digest(expected_bytes),
                "required": True,
            }
        ],
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/table.csv",
                    "sha256": digest(expected_bytes),
                    "exists": True,
                }
            ]
        },
    )

    failures = run_validate(tmp_path, monkeypatch)

    assert len(failures) == 1
    assert "Hash mismatch for outputs/table.csv" in failures[0]
    assert digest(actual_bytes) in failures[0]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    configure_repo(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": digest(b"expected\n"),
                "required": True,
            }
        ],
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/missing.csv",
                    "sha256": digest(b"expected\n"),
                    "exists": True,
                }
            ]
        },
    )

    assert run_validate(tmp_path, monkeypatch) == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    configure_repo(
        tmp_path,
        [
            {
                "path": "outputs/optional.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    assert run_validate(tmp_path, monkeypatch) == []


def test_validate_accepts_matching_live_output(tmp_path, monkeypatch):
    output_bytes = b"approved output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(output_bytes)
    configure_repo(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": digest(output_bytes),
                "required": True,
            }
        ],
    )

    assert run_validate(tmp_path, monkeypatch) == []
