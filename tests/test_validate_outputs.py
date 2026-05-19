import hashlib
import json

from scripts import validate_outputs


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _configure_expected(root, entries):
    _write_json(root / "config" / "expected_outputs.json", {"files": entries})
    # A stale manifest must not affect validation; live files are authoritative.
    _write_json(root / "logs" / "actual_manifest.json", {"files": []})


def test_validate_hashes_live_output_files(monkeypatch, tmp_path):
    corrupted_payload = b"corrupted output\n"
    output_path = tmp_path / "outputs" / "tables" / "table.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(corrupted_payload)
    expected_hash = _sha256(b"canonical output\n")
    corrupted_hash = _sha256(corrupted_payload)
    stale_manifest_hash = expected_hash
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/table.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/table.csv",
                    "sha256": stale_manifest_hash,
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        (
            "Hash mismatch for outputs/tables/table.csv: expected "
            f"{expected_hash}, got {corrupted_hash}"
        )
    ]


def test_validate_reports_missing_required_live_file(monkeypatch, tmp_path):
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/missing.csv",
                "sha256": _sha256(b"canonical output\n"),
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/missing.csv",
                    "sha256": _sha256(b"canonical output\n"),
                    "exists": True,
                }
            ]
        },
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Missing required output: outputs/tables/missing.csv"
    ]


def test_validate_allows_missing_optional_file(monkeypatch, tmp_path):
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
