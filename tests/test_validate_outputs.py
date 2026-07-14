import hashlib
import json

from scripts import validate_outputs


def _configure(monkeypatch, tmp_path, files):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)


def test_validate_hashes_live_output_instead_of_stale_manifest(monkeypatch, tmp_path):
    expected_bytes = b"authoritative output\n"
    expected_hash = hashlib.sha256(expected_bytes).hexdigest()
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"corrupted output\n")

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.csv",
                        "sha256": expected_hash,
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _configure(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": expected_hash,
                "required": True,
            }
        ],
    )

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv:")


def test_validate_reports_missing_required_live_output(monkeypatch, tmp_path):
    _configure(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": hashlib.sha256(b"expected").hexdigest(),
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == [
        "Missing required output: outputs/missing.csv"
    ]


def test_validate_rejects_unpinned_required_output(monkeypatch, tmp_path):
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(b"present but unpinned\n")
    _configure(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == [
        "Missing pinned SHA-256 for required output: outputs/result.csv"
    ]


def test_validate_allows_missing_optional_unpinned_output(monkeypatch, tmp_path):
    _configure(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "outputs/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    assert validate_outputs.validate() == []


def test_validate_accepts_matching_live_output_without_manifest(monkeypatch, tmp_path):
    content = b"authoritative output\n"
    output_path = tmp_path / "outputs" / "result.csv"
    output_path.parent.mkdir()
    output_path.write_bytes(content)
    _configure(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": hashlib.sha256(content).hexdigest(),
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == []
