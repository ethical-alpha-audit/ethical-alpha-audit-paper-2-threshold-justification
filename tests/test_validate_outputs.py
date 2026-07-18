import hashlib
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_outputs.py"
SPEC = importlib.util.spec_from_file_location("validate_outputs", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_config(base_dir, entries):
    config_dir = base_dir / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": entries}), encoding="utf-8"
    )


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_output_instead_of_stale_manifest(tmp_path, monkeypatch):
    expected_content = b"expected output"
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted output")
    write_config(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": sha256(expected_content),
                "required": True,
            }
        ],
    )
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.csv",
                        "sha256": sha256(expected_content),
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv:")


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    write_config(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": sha256(b"expected"),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [
        "Missing required output: outputs/missing.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"expected output"
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    write_config(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": sha256(content),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"output")
    write_config(
        tmp_path,
        [{"path": "outputs/result.csv", "sha256": "", "required": True}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [
        "Missing pinned SHA-256 for required output: outputs/result.csv"
    ]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    write_config(
        tmp_path,
        [{"path": "outputs/run_metadata.json", "sha256": "", "required": False}],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
