import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_expected(base: Path, files: list[dict]) -> None:
    _write_json(base / "config" / "expected_outputs.json", {"files": files})


def _write_stale_manifest(base: Path, output_path: str, expected_hash: str, exists: bool = True) -> None:
    _write_json(
        base / "logs" / "actual_manifest.json",
        {"files": [{"path": output_path, "sha256": expected_hash, "exists": exists}]},
    )


def test_validate_hashes_live_files_instead_of_trusting_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    expected_hash = _sha256_bytes(b"correct\n")
    live_file = tmp_path / output_path
    live_file.parent.mkdir(parents=True)
    live_file.write_bytes(b"corrupted\n")
    _write_expected(
        tmp_path,
        [{"path": output_path, "sha256": expected_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, output_path, expected_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    corrupted_hash = _sha256_bytes(b"corrupted\n")
    assert failures == [
        (
            f"Hash mismatch for {output_path}: expected {expected_hash}, "
            f"got {corrupted_hash}"
        )
    ]


def test_validate_reports_missing_required_live_file_despite_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    expected_hash = _sha256_bytes(b"correct\n")
    _write_expected(
        tmp_path,
        [{"path": output_path, "sha256": expected_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, output_path, expected_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    output_path = "outputs/sensitivity/run_metadata.json"
    _write_expected(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    live_file = tmp_path / output_path
    live_file.parent.mkdir(parents=True)
    live_file.write_bytes(b"content\n")
    _write_expected(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        f"Missing expected SHA-256 for required output: {output_path}"
    ]


def test_validate_accepts_matching_live_file_without_manifest(tmp_path, monkeypatch):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    content = b"correct\n"
    live_file = tmp_path / output_path
    live_file.parent.mkdir(parents=True)
    live_file.write_bytes(content)
    _write_expected(
        tmp_path,
        [{"path": output_path, "sha256": _sha256_bytes(content), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
