"""Regression tests for validation of live output artefacts."""

import hashlib
import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_outputs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_expected(base_dir: Path, files: list[dict]) -> None:
    config_dir = base_dir / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def write_stale_manifest(base_dir: Path, path: str, digest: str) -> None:
    logs_dir = base_dir / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {"files": [{"path": path, "sha256": digest, "exists": True}]}
        ),
        encoding="utf-8",
    )


def test_stale_manifest_cannot_mask_corrupted_live_output(tmp_path):
    validator = load_validator()
    validator.BASE_DIR = tmp_path
    relative_path = "outputs/result.csv"
    expected_content = b"expected\n"
    expected_hash = sha256(expected_content)
    write_expected(
        tmp_path,
        [{"path": relative_path, "sha256": expected_hash, "required": True}],
    )
    output = tmp_path / relative_path
    output.parent.mkdir()
    output.write_bytes(b"corrupted\n")
    write_stale_manifest(tmp_path, relative_path, expected_hash)

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {relative_path}:")


def test_stale_manifest_cannot_mask_missing_required_output(tmp_path):
    validator = load_validator()
    validator.BASE_DIR = tmp_path
    relative_path = "outputs/result.csv"
    expected_hash = sha256(b"expected\n")
    write_expected(
        tmp_path,
        [{"path": relative_path, "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, relative_path, expected_hash)

    assert validator.validate() == [f"Missing required output: {relative_path}"]


def test_matching_live_output_passes_without_manifest(tmp_path):
    validator = load_validator()
    validator.BASE_DIR = tmp_path
    relative_path = "outputs/result.csv"
    content = b"expected\n"
    write_expected(
        tmp_path,
        [{"path": relative_path, "sha256": sha256(content), "required": True}],
    )
    output = tmp_path / relative_path
    output.parent.mkdir()
    output.write_bytes(content)

    assert validator.validate() == []


def test_missing_optional_unpinned_output_is_allowed(tmp_path):
    validator = load_validator()
    validator.BASE_DIR = tmp_path
    write_expected(
        tmp_path,
        [{"path": "outputs/metadata.json", "sha256": "", "required": False}],
    )

    assert validator.validate() == []


def test_required_output_without_pinned_hash_fails_closed(tmp_path):
    validator = load_validator()
    validator.BASE_DIR = tmp_path
    relative_path = "outputs/result.csv"
    write_expected(
        tmp_path,
        [{"path": relative_path, "sha256": "", "required": True}],
    )
    output = tmp_path / relative_path
    output.parent.mkdir()
    output.write_bytes(b"content\n")

    assert validator.validate() == [
        f"Missing pinned SHA-256 for required output: {relative_path}"
    ]
