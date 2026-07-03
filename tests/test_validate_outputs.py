import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def write_expected(base: Path, files):
    config = base / "config"
    config.mkdir(parents=True)
    (config / "expected_outputs.json").write_text(json.dumps({"files": files}), encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"expected\n"
    corrupted_bytes = b"corrupted\n"
    expected_hash = sha256_bytes(expected_bytes)
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(corrupted_bytes)
    write_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": expected_hash, "required": True}],
    )

    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": "outputs/result.csv", "sha256": expected_hash, "exists": True}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        "Hash mismatch for outputs/result.csv: "
        f"expected {expected_hash}, got {sha256_bytes(corrupted_bytes)}"
    ]


def test_validate_reports_live_missing_required_output(tmp_path, monkeypatch):
    expected_hash = sha256_bytes(b"expected\n")
    write_expected(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": expected_hash, "required": True}],
    )

    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": "outputs/missing.csv", "sha256": expected_hash, "exists": True}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_existing_required_output_without_pinned_hash(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "unpinned.csv"
    output_path.parent.mkdir()
    output_path.write_text("value\n", encoding="utf-8")
    write_expected(
        tmp_path,
        [{"path": "outputs/unpinned.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Required output lacks expected sha256: outputs/unpinned.csv"]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    contents = b"expected\n"
    output_path.write_bytes(contents)
    write_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": sha256_bytes(contents), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
