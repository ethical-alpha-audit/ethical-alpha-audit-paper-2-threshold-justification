import hashlib
import json

from scripts import validate_outputs


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "result.txt"
    output_path.parent.mkdir(parents=True)
    expected_bytes = b"expected output\n"
    output_path.write_bytes(expected_bytes)

    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/result.txt",
                    "sha256": _sha256(expected_bytes),
                    "required": True,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/result.txt",
                    "sha256": _sha256(expected_bytes),
                    "exists": True,
                }
            ]
        },
    )

    output_path.write_bytes(b"corrupted output\n")
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.txt")


def test_validate_checks_live_missing_required_output(tmp_path, monkeypatch):
    expected_bytes = b"expected output\n"
    _write_json(
        tmp_path / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/result.txt",
                    "sha256": _sha256(expected_bytes),
                    "required": True,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/result.txt",
                    "sha256": _sha256(expected_bytes),
                    "exists": True,
                }
            ]
        },
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/result.txt"]
