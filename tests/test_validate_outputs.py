import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "result.txt"
    output.parent.mkdir()
    output.write_text("corrupted live bytes", encoding="utf-8")
    expected_hash = hashlib.sha256(b"expected bytes").hexdigest()
    write_expected(
        tmp_path,
        [{"path": "outputs/result.txt", "sha256": expected_hash, "required": True}],
    )

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.txt",
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

    assert failures == [
        f"Hash mismatch for outputs/result.txt: expected {expected_hash}, "
        f"got {hashlib.sha256(b'corrupted live bytes').hexdigest()}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    expected_hash = hashlib.sha256(b"expected bytes").hexdigest()
    write_expected(
        tmp_path,
        [{"path": "outputs/missing.txt", "sha256": expected_hash, "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.txt"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "result.txt"
    output.parent.mkdir()
    output.write_text("live bytes", encoding="utf-8")
    write_expected(
        tmp_path,
        [{"path": "outputs/result.txt", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Missing expected SHA-256 for required output: outputs/result.txt"
    ]


def test_validate_passes_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "result.txt"
    output.parent.mkdir()
    output.write_text("expected bytes", encoding="utf-8")
    expected_hash = hashlib.sha256(b"expected bytes").hexdigest()
    write_expected(
        tmp_path,
        [{"path": "outputs/result.txt", "sha256": expected_hash, "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
