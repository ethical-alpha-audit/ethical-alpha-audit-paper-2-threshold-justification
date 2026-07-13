import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_outputs", ROOT / "scripts" / "validate_outputs.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_expected(root: Path, files):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}), encoding="utf-8"
    )


def write_stale_manifest(root: Path, path: str, sha256: str, exists: bool = True):
    logs_dir = root / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps({"files": [{"path": path, "sha256": sha256, "exists": exists}]}),
        encoding="utf-8",
    )


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    validator = load_validator()
    path = "outputs/result.csv"
    expected_hash = digest_bytes(b"expected\n")
    output_path = tmp_path / path
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted\n")
    write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, path, expected_hash)

    failures = validator.validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {path}:")


def test_validate_reports_missing_required_live_output(tmp_path):
    validator = load_validator()
    path = "outputs/missing.csv"
    expected_hash = digest_bytes(b"expected\n")
    write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, path, expected_hash)

    assert validator.validate(tmp_path) == [f"Missing required output: {path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path):
    validator = load_validator()
    write_expected(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validator.validate(tmp_path) == []


def test_validate_rejects_required_output_without_pinned_sha(tmp_path):
    validator = load_validator()
    path = "outputs/result.csv"
    output_path = tmp_path / path
    output_path.parent.mkdir()
    output_path.write_text("expected\n", encoding="utf-8")
    write_expected(tmp_path, [{"path": path, "sha256": "", "required": True}])

    assert validator.validate(tmp_path) == [
        f"Required output lacks pinned SHA-256: {path}"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path):
    validator = load_validator()
    path = "outputs/result.csv"
    content = b"expected\n"
    output_path = tmp_path / path
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    write_expected(
        tmp_path,
        [{"path": path, "sha256": digest_bytes(content), "required": True}],
    )

    assert validator.validate(tmp_path) == []
