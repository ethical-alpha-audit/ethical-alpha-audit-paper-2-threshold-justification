import hashlib
import json

from scripts import validate_outputs


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def configure(tmp_path, files):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )
    validate_outputs.BASE_DIR = tmp_path


def test_validate_hashes_live_output_instead_of_stale_manifest(tmp_path):
    expected_content = b"canonical output"
    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir()
    output.write_bytes(b"corrupted output")
    configure(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": sha256(expected_content),
                "required": True,
            }
        ],
    )

    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "actual_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "outputs/result.csv",
                        "sha256": sha256(expected_content),
                        "exists": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    failures = validate_outputs.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/result.csv")


def test_validate_reports_missing_required_live_output(tmp_path):
    configure(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": sha256(b"canonical output"),
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == [
        "Missing required output: outputs/missing.csv"
    ]


def test_validate_allows_missing_optional_unpinned_output(tmp_path):
    configure(
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


def test_validate_rejects_required_output_without_pinned_hash(tmp_path):
    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir()
    output.write_bytes(b"output")
    configure(
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
        "Required output has no pinned SHA-256: outputs/result.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path):
    content = b"canonical output"
    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir()
    output.write_bytes(content)
    configure(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": sha256(content),
                "required": True,
            }
        ],
    )

    assert validate_outputs.validate() == []
