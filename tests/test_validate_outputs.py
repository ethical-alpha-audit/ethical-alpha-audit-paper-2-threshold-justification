import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _write_stale_manifest(root: Path, path: str, expected_hash: str) -> None:
    logs_dir = root / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": path,
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path: Path) -> None:
    path = "outputs/tables/table.csv"
    expected_bytes = b"stable,expected\n"
    expected_hash = _sha256(expected_bytes)
    live_bytes = b"corrupted,live\n"
    live_hash = _sha256(live_bytes)
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, path, expected_hash)
    output_path = tmp_path / path
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(live_bytes)

    failures = validate_outputs.validate(tmp_path)

    assert failures == [
        f"Hash mismatch for {path}: expected {expected_hash}, got {live_hash}"
    ]


def test_validate_reports_live_missing_required_output(tmp_path: Path) -> None:
    path = "outputs/tables/table.csv"
    expected_hash = _sha256(b"stable,expected\n")
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    _write_stale_manifest(tmp_path, path, expected_hash)

    failures = validate_outputs.validate(tmp_path)

    assert failures == [f"Missing required output: {path}"]


def test_validate_allows_missing_optional_output(tmp_path: Path) -> None:
    path = "outputs/sensitivity/run_metadata.json"
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": "", "required": False}],
    )

    failures = validate_outputs.validate(tmp_path)

    assert failures == []
