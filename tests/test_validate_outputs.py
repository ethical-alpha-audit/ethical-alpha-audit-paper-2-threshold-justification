import hashlib
import json

import scripts.validate_outputs as validate_outputs


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _configure_expected(tmp_path, files):
    _write_json(tmp_path / "config" / "expected_outputs.json", {"files": files})


def test_validate_hashes_live_file_not_stale_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    expected_bytes = b"authorised output\n"
    corrupted_bytes = b"corrupted output\n"
    output_path = tmp_path / "outputs" / "tables" / "table1_failure_mechanisms.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(corrupted_bytes)

    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/table1_failure_mechanisms.csv",
                "sha256": _sha256_bytes(expected_bytes),
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/table1_failure_mechanisms.csv",
                    "sha256": _sha256_bytes(expected_bytes),
                    "exists": True,
                }
            ]
        },
    )

    failures = validate_outputs.validate()

    assert failures == [
        "Hash mismatch for outputs/tables/table1_failure_mechanisms.csv: "
        f"expected {_sha256_bytes(expected_bytes)}, got {_sha256_bytes(corrupted_bytes)}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/table1_failure_mechanisms.csv",
                "sha256": _sha256_bytes(b"authorised output\n"),
                "required": True,
            }
        ],
    )
    _write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {
            "files": [
                {
                    "path": "outputs/tables/table1_failure_mechanisms.csv",
                    "sha256": _sha256_bytes(b"authorised output\n"),
                    "exists": True,
                }
            ]
        },
    )

    assert validate_outputs.validate() == [
        "Missing required output: outputs/tables/table1_failure_mechanisms.csv"
    ]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
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

    assert validate_outputs.validate() == []


def test_validate_requires_hash_for_required_output(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)
    output_path = tmp_path / "outputs" / "tables" / "table1_failure_mechanisms.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"authorised output\n")
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/tables/table1_failure_mechanisms.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == [
        "Missing expected SHA-256 for required output: outputs/tables/table1_failure_mechanisms.csv"
    ]
