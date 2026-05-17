import hashlib
import json

from scripts import validate_outputs


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _write_expected(base, path, digest, required=True):
    config = base / "config"
    config.mkdir()
    (config / "expected_outputs.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": path,
                        "sha256": digest,
                        "required": required,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_validate_hashes_live_output_file(monkeypatch, tmp_path):
    expected_content = b"expected\n"
    corrupted_content = b"corrupted\n"
    expected_hash = _sha256(expected_content)
    corrupted_hash = _sha256(corrupted_content)
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(corrupted_content)
    _write_expected(tmp_path, "outputs/table.csv", expected_hash)

    # A stale manifest with the expected digest must not make validation pass.
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "actual_manifest.json").write_text(
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

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        (
            "Hash mismatch for outputs/table.csv: "
            f"expected {expected_hash}, got {corrupted_hash}"
        )
    ]


def test_validate_passes_when_live_file_matches(monkeypatch, tmp_path):
    content = b"expected\n"
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    _write_expected(tmp_path, "outputs/table.csv", _sha256(content))
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
