import hashlib
import json

import scripts.validate_outputs as validator


def _write_expected(root, files):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_file_when_manifest_is_stale(tmp_path, monkeypatch):
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    (outputs_dir / "table.csv").write_bytes(b"corrupted\n")

    expected_hash = _sha256_bytes(b"expected\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": expected_hash,
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
                        "path": "outputs/table.csv",
                        "sha256": expected_hash,
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
    assert failures[0].startswith("Hash mismatch for outputs/table.csv:")


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256_bytes(b"expected\n"),
                "required": True,
            }
        ],
    )

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    (outputs_dir / "required.csv").write_bytes(b"expected\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/required.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == [
        "Missing expected SHA-256 for required output: outputs/required.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"expected\n"
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    (outputs_dir / "table.csv").write_bytes(content)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
                "sha256": _sha256_bytes(content),
                "required": True,
            }
        ],
    )

    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
