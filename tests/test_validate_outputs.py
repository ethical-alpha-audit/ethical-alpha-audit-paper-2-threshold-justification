import hashlib
import json

import scripts.validate_outputs as validator


def _write_expected(root, files):
    (root / "config").mkdir()
    (root / "config" / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_bytes = b"authorised output\n"
    live_bytes = b"corrupted live output\n"
    output_path = tmp_path / "outputs" / "critical.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(live_bytes)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/critical.csv",
                "sha256": _sha256(expected_bytes),
                "required": True,
            }
        ],
    )

    # A stale manifest that still matches the expected digest must not mask live corruption.
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/critical.csv",
                        "sha256": _sha256(expected_bytes),
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    failures = validator.validate()

    assert failures == [
        (
            "Hash mismatch for outputs/critical.csv: "
            f"expected {_sha256(expected_bytes)}, got {_sha256(live_bytes)}"
        )
    ]


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": _sha256(b"expected\n"),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/optional.json",
                "sha256": "",
                "required": False,
            }
        ],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []


def test_validate_accepts_live_output_with_expected_digest(tmp_path, monkeypatch):
    output_bytes = b"stable output\n"
    output_path = tmp_path / "outputs" / "stable.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(output_bytes)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/stable.csv",
                "sha256": _sha256(output_bytes),
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validator, "BASE_DIR", tmp_path)

    assert validator.validate() == []
