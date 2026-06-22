import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validator


def _write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_file_not_stale_manifest(tmp_path, monkeypatch) -> None:
    expected_content = b"authoritative output\n"
    live_content = b"corrupted output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(live_content)
    expected_hash = _sha256(expected_content)
    _write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": expected_hash, "required": True}],
    )
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/table.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    failures = validator.validate()

    assert len(failures) == 1
    assert "Hash mismatch for outputs/table.csv" in failures[0]
    assert _sha256(live_content) in failures[0]


def test_validate_reports_missing_required_live_file(tmp_path, monkeypatch) -> None:
    expected_hash = _sha256(b"expected output\n")
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
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch) -> None:
    _write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_passes_matching_live_file_without_manifest(tmp_path, monkeypatch) -> None:
    content = b"authoritative output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    _write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": _sha256(content), "required": True}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
