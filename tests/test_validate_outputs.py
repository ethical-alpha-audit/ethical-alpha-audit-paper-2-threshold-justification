import hashlib
import json
from pathlib import Path

from scripts.validate_outputs import validate


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_expected_outputs(base_dir: Path, files: list[dict]) -> None:
    _write_json(base_dir / "config" / "expected_outputs.json", {"files": files})


def _write_stale_manifest(base_dir: Path, path: str, digest: str, exists: bool = True) -> None:
    _write_json(
        base_dir / "logs" / "actual_manifest.json",
        {"generated_at": "stale", "files": [{"path": path, "sha256": digest, "exists": exists}]},
    )


def test_validate_hashes_live_file_not_stale_manifest(tmp_path):
    output_path = "outputs/tables/table.csv"
    expected_bytes = b"expected\n"
    expected_digest = _sha256(expected_bytes)
    live_file = tmp_path / output_path
    live_file.parent.mkdir(parents=True)
    live_file.write_bytes(b"corrupted\n")

    _write_expected_outputs(
        tmp_path,
        [{"path": output_path, "sha256": expected_digest, "required": True}],
    )
    _write_stale_manifest(tmp_path, output_path, expected_digest)

    failures = validate(tmp_path)
    actual_digest = _sha256(b"corrupted\n")

    assert failures == [f"Hash mismatch for {output_path}: expected {expected_digest}, got {actual_digest}"]


def test_validate_reports_missing_required_live_file_not_stale_manifest(tmp_path):
    output_path = "outputs/tables/missing.csv"
    expected_digest = _sha256(b"expected\n")
    _write_expected_outputs(
        tmp_path,
        [{"path": output_path, "sha256": expected_digest, "required": True}],
    )
    _write_stale_manifest(tmp_path, output_path, expected_digest)

    assert validate(tmp_path) == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_output(tmp_path):
    output_path = "outputs/sensitivity/run_metadata.json"
    _write_expected_outputs(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": False}],
    )

    assert validate(tmp_path) == []


def test_validate_accepts_matching_live_file(tmp_path):
    output_path = "outputs/tables/table.csv"
    live_bytes = b"ok\n"
    live_file = tmp_path / output_path
    live_file.parent.mkdir(parents=True)
    live_file.write_bytes(live_bytes)
    _write_expected_outputs(
        tmp_path,
        [{"path": output_path, "sha256": _sha256(live_bytes), "required": True}],
    )

    assert validate(tmp_path) == []
