import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator_module():
    module_path = ROOT / "scripts" / "validate_outputs.py"
    spec = importlib.util.spec_from_file_location("validate_outputs", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_expected_outputs(base_dir, entries):
    config_dir = base_dir / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}, indent=2),
        encoding="utf-8",
    )


def write_stale_manifest(base_dir, entries):
    logs_dir = base_dir / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"generated_at": "stale", "files": entries}, indent=2),
        encoding="utf-8",
    )


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_file_not_stale_manifest(tmp_path):
    validator = load_validator_module()
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    expected_bytes = b"authorised,threshold\ntrue,0.85\n"
    output_path.write_bytes(b"corrupted\n")
    expected_hash = sha256_bytes(expected_bytes)

    entry = {
        "path": "outputs/table.csv",
        "sha256": expected_hash,
        "required": True,
    }
    write_expected_outputs(tmp_path, [entry])
    write_stale_manifest(
        tmp_path,
        [{"path": entry["path"], "sha256": expected_hash, "exists": True}],
    )

    failures = validator.validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/table.csv")


def test_validate_reports_missing_required_file_even_when_manifest_is_stale(tmp_path):
    validator = load_validator_module()
    expected_hash = sha256_bytes(b"expected\n")
    entry = {
        "path": "outputs/required.csv",
        "sha256": expected_hash,
        "required": True,
    }
    write_expected_outputs(tmp_path, [entry])
    write_stale_manifest(
        tmp_path,
        [{"path": entry["path"], "sha256": expected_hash, "exists": True}],
    )

    failures = validator.validate(tmp_path)

    assert failures == ["Missing required output: outputs/required.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    validator = load_validator_module()
    write_expected_outputs(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    assert validator.validate(tmp_path) == []


def test_validate_accepts_matching_live_file_without_manifest(tmp_path):
    validator = load_validator_module()
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    expected_bytes = b"authorised,threshold\ntrue,0.85\n"
    output_path.write_bytes(expected_bytes)
    write_expected_outputs(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": sha256_bytes(expected_bytes),
                "required": True,
            }
        ],
    )

    assert validator.validate(tmp_path) == []
