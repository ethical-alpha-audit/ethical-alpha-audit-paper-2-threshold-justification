import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def write_json(path: Path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def write_validation_bundle(tmp_path: Path, files, manifest_files=None):
    (tmp_path / "config").mkdir()
    (tmp_path / "logs").mkdir()
    for item in files:
        output_path = tmp_path / item["path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if "contents" in item:
            output_path.write_bytes(item["contents"])

    expected_files = [
        {
            "path": item["path"],
            "sha256": item.get("sha256", hashlib.sha256(item.get("contents", b"")).hexdigest()),
            "required": item.get("required", True),
        }
        for item in files
    ]
    write_json(tmp_path / "config" / "expected_outputs.json", {"files": expected_files})

    if manifest_files is None:
        manifest_files = [
            {
                "path": item["path"],
                "sha256": item.get("sha256", hashlib.sha256(item.get("contents", b"")).hexdigest()),
                "exists": "contents" in item,
            }
            for item in files
        ]
    write_json(tmp_path / "logs" / "actual_manifest.json", {"files": manifest_files})


def run_validate_against(tmp_path: Path):
    old_base = validate_outputs.BASE_DIR
    validate_outputs.BASE_DIR = tmp_path
    try:
        return validate_outputs.validate()
    finally:
        validate_outputs.BASE_DIR = old_base


def test_validate_hashes_live_output_not_stale_manifest(tmp_path):
    expected_contents = b"expected output\n"
    expected_hash = hashlib.sha256(expected_contents).hexdigest()
    write_validation_bundle(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "contents": b"corrupted output\n",
                "sha256": expected_hash,
            }
        ],
        manifest_files=[
            {
                "path": "outputs/result.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )

    failures = run_validate_against(tmp_path)

    assert failures == [
        "Hash mismatch for outputs/result.csv: "
        f"expected {expected_hash}, got {hashlib.sha256(b'corrupted output\n').hexdigest()}"
    ]


def test_validate_reports_missing_required_output_despite_stale_manifest(tmp_path):
    expected_hash = hashlib.sha256(b"expected output\n").hexdigest()
    write_validation_bundle(
        tmp_path,
        [{"path": "outputs/missing.csv", "sha256": expected_hash}],
        manifest_files=[
            {
                "path": "outputs/missing.csv",
                "sha256": expected_hash,
                "exists": True,
            }
        ],
    )

    assert run_validate_against(tmp_path) == ["Missing required output: outputs/missing.csv"]


def test_validate_allows_missing_optional_output(tmp_path):
    write_validation_bundle(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "required": False,
                "sha256": "",
            }
        ],
    )

    assert run_validate_against(tmp_path) == []


def test_validate_accepts_matching_live_output(tmp_path):
    write_validation_bundle(
        tmp_path,
        [{"path": "outputs/result.csv", "contents": b"expected output\n"}],
    )

    assert run_validate_against(tmp_path) == []
