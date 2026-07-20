import hashlib
import json
from pathlib import Path

from scripts.validate_outputs import validate


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_expected(root: Path, entries) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}, indent=2),
        encoding="utf-8",
    )


def write_stale_manifest(root: Path, path: str, content: bytes) -> None:
    logs_dir = root / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": path,
                        "sha256": sha256_bytes(content),
                        "exists": True,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    output_path = "outputs/table.csv"
    original = b"canonical\n"
    output = tmp_path / output_path
    output.parent.mkdir()
    output.write_bytes(original)
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": sha256_bytes(original), "required": True}],
    )
    write_stale_manifest(tmp_path, output_path, original)

    output.write_bytes(b"corrupted\n")

    failures = validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {output_path}")


def test_validate_reports_missing_required_output_despite_stale_manifest(tmp_path):
    output_path = "outputs/table.csv"
    original = b"canonical\n"
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": sha256_bytes(original), "required": True}],
    )
    write_stale_manifest(tmp_path, output_path, original)

    assert validate(tmp_path) == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_output(tmp_path):
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validate(tmp_path) == []


def test_validate_accepts_matching_live_output_without_manifest(tmp_path):
    output_path = "outputs/table.csv"
    content = b"canonical\n"
    output = tmp_path / output_path
    output.parent.mkdir()
    output.write_bytes(content)
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": sha256_bytes(content), "required": True}],
    )

    assert validate(tmp_path) == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path):
    output_path = "outputs/table.csv"
    output = tmp_path / output_path
    output.parent.mkdir()
    output.write_bytes(b"canonical\n")
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": True}],
    )

    assert validate(tmp_path) == [
        f"Missing expected SHA-256 for required output: {output_path}"
    ]
