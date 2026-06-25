import hashlib
import json

from scripts import validate_outputs


def _write_expected(base, files):
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def _write_output(base, relative_path, content):
    output_path = base / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def test_validate_hashes_live_outputs_not_stale_manifest(tmp_path, monkeypatch):
    expected_hash = hashlib.sha256(b"authorised output\n").hexdigest()
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/result.txt",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    _write_output(tmp_path, "outputs/result.txt", b"corrupted output\n")

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.txt",
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

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.txt")


def test_validate_reports_missing_required_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.txt",
                "sha256": "0" * 64,
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.txt"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/optional.txt",
                "sha256": "0" * 64,
                "required": False,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_passes_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"expected output\n"
    expected_hash = _write_output(tmp_path, "outputs/result.txt", content)
    _write_expected(
        tmp_path,
        [
            {
                "path": "outputs/result.txt",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []
