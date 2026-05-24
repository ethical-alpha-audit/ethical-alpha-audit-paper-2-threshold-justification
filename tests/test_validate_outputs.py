"""Regression tests for live output hash validation."""
import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def _write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (root / "logs").mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_files_not_stale_manifest(tmp_path, monkeypatch) -> None:
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    output.write_bytes(b"corrupt live output\n")

    expected_hash = _sha256(b"expected output\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    # A stale manifest says the output is correct; validation must ignore it and
    # inspect the live artefact instead.
    (tmp_path / "logs" / "actual_manifest.json").write_text(
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

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/table.csv")


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch) -> None:
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256(b"expected output\n"),
                "required": True,
            },
            {
                "path": "outputs/optional-run-metadata.json",
                "sha256": "",
                "required": False,
            },
        ],
    )
    (tmp_path / "logs" / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/missing.csv",
                        "sha256": _sha256(b"expected output\n"),
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_passes_when_live_output_matches_expected_hash(tmp_path, monkeypatch) -> None:
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    content = b"expected output\n"
    output.write_bytes(content)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": _sha256(content),
                "required": True,
            }
        ],
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
