import hashlib
import json

from scripts import validate_outputs


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _configure_expected(base, files):
    _write_json(base / "config" / "expected_outputs.json", {"files": files})


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "table.csv"
    output_path.parent.mkdir(parents=True)
    original = b"column\nexpected\n"
    output_path.write_bytes(original)
    expected_hash = _sha256(original)
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/table.csv",
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
                    "path": "outputs/table.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )
    output_path.write_bytes(b"column\ncorrupted\n")
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/table.csv:")


def test_validate_checks_live_required_file_presence(tmp_path, monkeypatch):
    expected_hash = _sha256(b"expected\n")
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
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
                    "path": "outputs/missing.csv",
                    "sha256": expected_hash,
                    "exists": True,
                }
            ]
        },
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == []


def test_validate_requires_hash_for_required_outputs(tmp_path, monkeypatch):
    output_path = tmp_path / "outputs" / "unpinned.csv"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("content\n", encoding="utf-8")
    _configure_expected(
        tmp_path,
        [
            {
                "path": "outputs/unpinned.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [
        "Required output has no pinned sha256: outputs/unpinned.csv"
    ]
