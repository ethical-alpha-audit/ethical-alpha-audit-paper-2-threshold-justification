import hashlib
import json

from scripts.validate_outputs import validate


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_expected_outputs(base_dir, path, digest, required=True):
    config_dir = base_dir / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
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


def test_validate_hashes_live_output_file(tmp_path):
    output_path = tmp_path / "outputs" / "tables" / "result.csv"
    output_path.parent.mkdir(parents=True)
    output_bytes = b"column\nvalue\n"
    output_path.write_bytes(output_bytes)
    _write_expected_outputs(
        tmp_path,
        "outputs/tables/result.csv",
        _sha256(output_bytes),
    )

    assert validate(tmp_path) == []


def test_validate_does_not_trust_stale_manifest(tmp_path):
    expected_bytes = b"column\nexpected\n"
    corrupt_bytes = b"column\ncorrupt\n"
    output_path = tmp_path / "outputs" / "tables" / "result.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(corrupt_bytes)
    expected_hash = _sha256(expected_bytes)
    _write_expected_outputs(tmp_path, "outputs/tables/result.csv", expected_hash)

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/tables/result.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    failures = validate(tmp_path)

    assert failures == [
        "Hash mismatch for outputs/tables/result.csv: "
        f"expected {expected_hash}, got {_sha256(corrupt_bytes)}"
    ]
