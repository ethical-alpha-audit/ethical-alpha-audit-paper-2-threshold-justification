import hashlib
import json

from scripts import validate_outputs


def _write_expected(root, files):
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _validate_with_base(monkeypatch, root):
    monkeypatch.setattr(validate_outputs, "BASE_DIR", root)
    return validate_outputs.validate()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "critical.csv"
    output.parent.mkdir()
    expected_bytes = b"authorised,correct\n"
    corrupted_bytes = b"corrupted,wrong\n"
    output.write_bytes(corrupted_bytes)
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

    failures = _validate_with_base(monkeypatch, tmp_path)

    assert failures == [
        (
            "Hash mismatch for outputs/critical.csv: "
            f"expected {_sha256(expected_bytes)}, got {_sha256(corrupted_bytes)}"
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

    assert _validate_with_base(monkeypatch, tmp_path) == [
        "Missing required output: outputs/missing.csv"
    ]


def test_validate_allows_missing_optional_live_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/optional.json",
                "sha256": _sha256(b"optional\n"),
                "required": False,
            }
        ],
    )

    assert _validate_with_base(monkeypatch, tmp_path) == []


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output = tmp_path / "outputs" / "valid.csv"
    output.parent.mkdir()
    content = b"valid\n"
    output.write_bytes(content)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/valid.csv",
                "sha256": _sha256(content),
                "required": True,
            }
        ],
    )

    assert _validate_with_base(monkeypatch, tmp_path) == []
