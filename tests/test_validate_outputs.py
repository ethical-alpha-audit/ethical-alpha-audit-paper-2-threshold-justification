import hashlib
import json
from pathlib import Path

from scripts.validate_outputs import validate


def write_expected(root: Path, entries):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}, indent=2),
        encoding="utf-8",
    )
    (root / "logs").mkdir()
    (root / "logs" / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {"path": entry["path"], "sha256": entry.get("sha256", ""), "exists": True}
                    for entry in entries
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    original = b"canonical\n"
    output.write_bytes(original)
    write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": sha256_bytes(original), "required": True}],
    )

    output.write_bytes(b"corrupted\n")

    failures = validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/table.csv")


def test_validate_reports_missing_required_output_even_with_stale_manifest(tmp_path):
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    original = b"canonical\n"
    output.write_bytes(original)
    write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": sha256_bytes(original), "required": True}],
    )

    output.unlink()

    assert validate(tmp_path) == ["Missing required output: outputs/table.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validate(tmp_path) == []


def test_validate_accepts_matching_live_output_without_manifest_dependency(tmp_path):
    output = tmp_path / "outputs" / "table.csv"
    output.parent.mkdir()
    original = b"canonical\n"
    output.write_bytes(original)
    write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": sha256_bytes(original), "required": True}],
    )
    (tmp_path / "logs" / "actual_manifest.json").unlink()

    assert validate(tmp_path) == []
