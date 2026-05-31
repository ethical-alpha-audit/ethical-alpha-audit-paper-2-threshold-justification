import hashlib
import json

from scripts import validate_outputs


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def configure_expected(tmp_path, files):
    write_json(tmp_path / "config" / "expected_outputs.json", {"files": files})


def configure_stale_manifest(tmp_path, files):
    write_json(tmp_path / "logs" / "actual_manifest.json", {"files": files})


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_content = b"authorised output\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b"corrupted output\n")
    expected_hash = sha256_bytes(expected_content)

    configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    configure_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert "Hash mismatch for outputs/table.csv" in failures[0]


def test_validate_checks_live_missing_required_outputs(tmp_path, monkeypatch):
    expected_hash = sha256_bytes(b"authorised output\n")
    configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    configure_stale_manifest(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_outputs(tmp_path, monkeypatch):
    configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )
    configure_stale_manifest(tmp_path, [])
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
