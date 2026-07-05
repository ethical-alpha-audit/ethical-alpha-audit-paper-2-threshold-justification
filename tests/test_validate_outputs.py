import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", ROOT / "scripts" / "validate_outputs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_expected(base: Path, files):
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}, indent=2),
        encoding="utf-8",
    )


def write_stale_manifest(base: Path, path: str, sha256: str):
    logs_dir = base / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": path, "sha256": sha256, "exists": True}]}),
        encoding="utf-8",
    )


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_output_instead_of_stale_manifest(tmp_path, monkeypatch):
    validator = load_validator()
    expected_path = "outputs/table.csv"
    expected_content = b"authorised,threshold\nyes,0.85\n"
    stale_hash = sha256_bytes(expected_content)

    write_expected(
        tmp_path,
        [{"path": expected_path, "sha256": stale_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, expected_path, stale_hash)
    live_path = tmp_path / expected_path
    live_path.parent.mkdir(parents=True)
    live_path.write_bytes(b"corrupted\n")

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {expected_path}:")


def test_validate_reports_missing_required_live_output_even_with_stale_manifest(tmp_path, monkeypatch):
    validator = load_validator()
    expected_path = "outputs/missing.csv"
    stale_hash = sha256_bytes(b"old output\n")

    write_expected(
        tmp_path,
        [{"path": expected_path, "sha256": stale_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, expected_path, stale_hash)

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [f"Missing required output: {expected_path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    validator = load_validator()
    expected_path = "outputs/sensitivity/run_metadata.json"
    write_expected(tmp_path, [{"path": expected_path, "sha256": "", "required": False}])

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    validator = load_validator()
    expected_path = "outputs/table.csv"
    write_expected(tmp_path, [{"path": expected_path, "sha256": "", "required": True}])
    live_path = tmp_path / expected_path
    live_path.parent.mkdir(parents=True)
    live_path.write_text("complete\n", encoding="utf-8")

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [f"Required output has no pinned SHA-256: {expected_path}"]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    validator = load_validator()
    expected_path = "outputs/table.csv"
    content = b"authorised,threshold\nno,0.85\n"
    write_expected(
        tmp_path,
        [{"path": expected_path, "sha256": sha256_bytes(content), "required": True}],
    )
    live_path = tmp_path / expected_path
    live_path.parent.mkdir(parents=True)
    live_path.write_bytes(content)

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
