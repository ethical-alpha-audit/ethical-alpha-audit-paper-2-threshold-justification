import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_outputs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_expected(root: Path, files):
    (root / "config").mkdir()
    (root / "config" / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    expected_hash = hashlib.sha256(b"authorised\n").hexdigest()
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted\n")
    write_expected(
        tmp_path,
        [{"path": "outputs/table.csv", "sha256": expected_hash, "required": True}],
    )
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/table.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    failures = validator.validate()

    assert len(failures) == 1
    assert "Hash mismatch for outputs/table.csv" in failures[0]


def test_validate_reports_missing_required_live_output(tmp_path):
    write_expected(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": "expected", "required": True}],
    )
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/missing.csv",
                        "sha256": "expected",
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    assert validator.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    assert validator.validate() == []


def test_validate_does_not_require_manifest_for_matching_live_output(tmp_path):
    content = b"authorised\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": hashlib.sha256(content).hexdigest(),
                "required": True,
            }
        ],
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    assert validator.validate() == []
