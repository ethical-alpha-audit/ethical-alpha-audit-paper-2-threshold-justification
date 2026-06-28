import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validator


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def configure_expected(root: Path, files: list[dict]) -> None:
    write_json(root / "config" / "expected_outputs.json", {"files": files})


def write_output(root: Path, relative_path: str, content: bytes) -> str:
    output_path = root / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def validate_from(root: Path, monkeypatch) -> list[str]:
    monkeypatch.setattr(validator, "BASE_DIR", root)
    return validator.validate()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    expected_path = "outputs/tables/table1_failure_mechanisms.csv"
    expected_hash = hashlib.sha256(b"approved output\n").hexdigest()
    write_output(tmp_path, expected_path, b"corrupted live output\n")
    configure_expected(
        tmp_path,
        [{"path": expected_path, "sha256": expected_hash, "required": True}],
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": expected_path, "sha256": expected_hash, "exists": True}]},
    )

    failures = validate_from(tmp_path, monkeypatch)

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {expected_path}:")


def test_validate_reports_missing_required_output_even_with_stale_manifest(tmp_path, monkeypatch):
    expected_path = "outputs/tables/table1_failure_mechanisms.csv"
    expected_hash = hashlib.sha256(b"approved output\n").hexdigest()
    configure_expected(
        tmp_path,
        [{"path": expected_path, "sha256": expected_hash, "required": True}],
    )
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": expected_path, "sha256": expected_hash, "exists": True}]},
    )

    assert validate_from(tmp_path, monkeypatch) == [f"Missing required output: {expected_path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    configure_expected(
        tmp_path,
        [{"path": "outputs/sensitivity/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validate_from(tmp_path, monkeypatch) == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    expected_path = "outputs/tables/table1_failure_mechanisms.csv"
    write_output(tmp_path, expected_path, b"approved output\n")
    configure_expected(tmp_path, [{"path": expected_path, "sha256": "", "required": True}])

    assert validate_from(tmp_path, monkeypatch) == [
        f"Required output has no expected SHA-256: {expected_path}"
    ]


def test_validate_passes_matching_live_output_without_manifest(tmp_path, monkeypatch):
    expected_path = "outputs/tables/table1_failure_mechanisms.csv"
    expected_hash = write_output(tmp_path, expected_path, b"approved output\n")
    configure_expected(
        tmp_path,
        [{"path": expected_path, "sha256": expected_hash, "required": True}],
    )

    assert validate_from(tmp_path, monkeypatch) == []
