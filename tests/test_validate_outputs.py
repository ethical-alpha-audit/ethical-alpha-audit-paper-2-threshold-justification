import hashlib
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_outputs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_expected(base: Path, files):
    (base / "config").mkdir()
    (base / "config" / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def write_stale_manifest(base: Path, path: str, sha256: str, exists: bool = True):
    (base / "logs").mkdir()
    (base / "logs" / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": path, "sha256": sha256, "exists": exists}]}),
        encoding="utf-8",
    )


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    expected_bytes = b"approved output\n"
    expected_hash = sha256_bytes(expected_bytes)
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted output\n")
    write_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, "outputs/result.csv", expected_hash)

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv")


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    expected_hash = sha256_bytes(b"approved output\n")
    write_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, "outputs/result.csv", expected_hash)

    failures = validator.validate()

    assert failures == ["Missing required output: outputs/result.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validator.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_text("approved output\n", encoding="utf-8")
    write_expected(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": "", "required": True}],
    )

    failures = validator.validate()

    assert failures == ["Missing expected hash for required output: outputs/result.csv"]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    output_bytes = b"approved output\n"
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(output_bytes)
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": sha256_bytes(output_bytes),
                "required": True,
            }
        ],
    )

    assert validator.validate() == []
