import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validate_outputs_module():
    spec = importlib.util.spec_from_file_location(
        "validate_outputs_for_test",
        ROOT / "scripts" / "validate_outputs.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_file = tmp_path / "outputs" / "result.csv"
    expected_file.parent.mkdir(parents=True)
    expected_file.write_text("correct\n", encoding="utf-8")
    expected_hash = hashlib.sha256(expected_file.read_bytes()).hexdigest()

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.csv",
                        "sha256": expected_hash,
                        "required": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    expected_file.write_text("corrupted\n", encoding="utf-8")

    validate_outputs = load_validate_outputs_module()
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        "Hash mismatch for outputs/result.csv: "
        f"expected {expected_hash}, got {hashlib.sha256(expected_file.read_bytes()).hexdigest()}"
    ]
