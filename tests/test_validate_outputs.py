import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected(base: Path, files):
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    original = b"canonical-output\n"
    corrupted = b"corrupted-output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(corrupted)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": _sha256(original),
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
                        "sha256": _sha256(original),
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


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256(b"canonical-output\n"),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"canonical-output\n")
    _write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Missing expected SHA-256 for required output: outputs/table.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"canonical-output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
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
