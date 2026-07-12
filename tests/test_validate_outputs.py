import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "validate_outputs_under_test",
        ROOT / "scripts" / "validate_outputs.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.BASE_DIR = tmp_path
    return module


def write_expected(root, files):
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def write_manifest(root, files):
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def write_output(root, relative_path, content):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def digest(content):
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    original = b"canonical output\n"
    corrupted = b"corrupted live output\n"
    original_hash = digest(original)
    corrupted_hash = digest(corrupted)
    write_output(tmp_path, output_path, original)
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": original_hash, "required": True}],
    )
    write_manifest(
        tmp_path,
        [{"path": output_path, "sha256": original_hash, "exists": True}],
    )
    write_output(tmp_path, output_path, corrupted)

    failures = load_validator(tmp_path).validate()

    assert failures == [
        f"Hash mismatch for {output_path}: expected {original_hash}, got {corrupted_hash}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    original = b"canonical output\n"
    original_hash = digest(original)
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": original_hash, "required": True}],
    )
    write_manifest(
        tmp_path,
        [{"path": output_path, "sha256": original_hash, "exists": True}],
    )

    failures = load_validator(tmp_path).validate()

    assert failures == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path):
    output_path = "outputs/sensitivity/run_metadata.json"
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": False}],
    )

    assert load_validator(tmp_path).validate() == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    write_output(tmp_path, output_path, b"canonical output\n")
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": "", "required": True}],
    )

    failures = load_validator(tmp_path).validate()

    assert failures == [f"Missing expected SHA-256 for required output: {output_path}"]


def test_validate_passes_matching_live_output_without_manifest(tmp_path):
    output_path = "outputs/tables/table1_failure_mechanisms.csv"
    original = b"canonical output\n"
    write_output(tmp_path, output_path, original)
    write_expected(
        tmp_path,
        [{"path": output_path, "sha256": digest(original), "required": True}],
    )

    assert load_validator(tmp_path).validate() == []
