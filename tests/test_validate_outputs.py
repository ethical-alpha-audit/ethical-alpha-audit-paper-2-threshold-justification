import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def configure_expected(base_dir: Path, files: list[dict]) -> None:
    (base_dir / "config").mkdir()
    write_json(base_dir / "config" / "expected_outputs.json", {"files": files})


def configure_stale_manifest(base_dir: Path, path: str, sha256: str) -> None:
    (base_dir / "logs").mkdir()
    write_json(
        base_dir / "logs" / "actual_manifest.json",
        {"files": [{"path": path, "sha256": sha256, "exists": True}]},
    )


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_hash = sha256_text("canonical\n")
    live_file = tmp_path / output_path
    live_file.parent.mkdir()
    live_file.write_text("corrupted\n", encoding="utf-8")
    configure_expected(
        tmp_path,
        [{"path": output_path, "sha256": expected_hash, "required": True}],
    )
    configure_stale_manifest(tmp_path, output_path, expected_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        f"Hash mismatch for {output_path}: expected {expected_hash}, got {sha256_text('corrupted\n')}"
    ]


def test_validate_reports_missing_required_output_even_with_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    expected_hash = sha256_text("canonical\n")
    configure_expected(
        tmp_path,
        [{"path": output_path, "sha256": expected_hash, "required": True}],
    )
    configure_stale_manifest(tmp_path, output_path, expected_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    configure_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "unused", "required": False}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output_path = "outputs/table.csv"
    live_file = tmp_path / output_path
    live_file.parent.mkdir()
    live_file.write_text("canonical\n", encoding="utf-8")
    configure_expected(
        tmp_path,
        [{"path": output_path, "sha256": sha256_text("canonical\n"), "required": True}],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
