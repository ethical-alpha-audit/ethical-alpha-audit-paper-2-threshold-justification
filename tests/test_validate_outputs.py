import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def _write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted\n")

    expected_hash = _sha256_bytes(b"original\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/critical.csv",
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
                        "path": "outputs/critical.csv",
                        "exists": True,
                        "sha256": expected_hash,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        "Hash mismatch for outputs/critical.csv: "
        f"expected {expected_hash}, got {_sha256_bytes(b'corrupted\n')}"
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256_bytes(b"original\n"),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


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
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"original\n")
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/critical.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Missing expected SHA-256 for required output: outputs/critical.csv"
    ]


def test_validate_passes_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"original\n"
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/critical.csv",
                "sha256": _sha256_bytes(content),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
