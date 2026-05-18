import hashlib
import json

from scripts.validate_outputs import validate


def write_expected_outputs(root, entries):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}),
        encoding="utf-8",
    )


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    corrupted_output = b"corrupted output\n"
    output_path.write_bytes(corrupted_output)

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    stale_hash = sha256_bytes(b"expected output\n")
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": "outputs/table.csv", "sha256": stale_hash, "exists": True}]}),
        encoding="utf-8",
    )
    write_expected_outputs(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": stale_hash, "required": True}],
    )

    failures = validate(tmp_path)

    assert failures == [
        "Hash mismatch for outputs/table.csv: "
        f"expected {stale_hash}, got {sha256_bytes(corrupted_output)}"
    ]


def test_validate_reports_missing_required_output(tmp_path):
    write_expected_outputs(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": "abc123", "required": True}],
    )

    assert validate(tmp_path) == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    write_expected_outputs(
        tmp_path,
        [{"path": "outputs/sensitivity/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validate(tmp_path) == []
