import importlib.util
import json
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_outputs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def make_repo(tmp_path: Path, files: list[dict]) -> Path:
    (tmp_path / "config").mkdir()
    write_json(tmp_path / "config" / "expected_outputs.json", {"files": files})
    return tmp_path


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path):
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    expected_hash = sha256(b"correct\n").hexdigest()
    output_path.write_bytes(b"corrupted\n")
    make_repo(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": expected_hash, "required": True}],
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv")


def test_validate_reports_missing_required_output_even_if_manifest_is_stale(tmp_path):
    make_repo(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": sha256(b"old\n").hexdigest(), "required": True}],
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    assert validator.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    make_repo(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    validator = load_validator()
    validator.BASE_DIR = tmp_path

    assert validator.validate() == []
