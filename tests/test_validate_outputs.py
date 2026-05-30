import hashlib
import json
from pathlib import Path

from scripts import validate_outputs


def digest(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def configure_expected(tmp_path: Path, files: list[dict]) -> None:
    write_json(tmp_path / "config" / "expected_outputs.json", {"files": files})


def write_stale_manifest(tmp_path: Path, path: str, sha256: str) -> None:
    write_json(
        tmp_path / "logs" / "actual_manifest.json",
        {"files": [{"path": path, "sha256": sha256, "exists": True}]},
    )


def test_validate_hashes_live_output_instead_of_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/tables/table.csv"
    expected_bytes = b"expected\n"
    corrupt_bytes = b"corrupt\n"

    configure_expected(
        tmp_path,
        [{"path": output_path, "sha256": digest(expected_bytes), "required": True}],
    )
    live_output = tmp_path / output_path
    live_output.parent.mkdir(parents=True, exist_ok=True)
    live_output.write_bytes(corrupt_bytes)
    write_stale_manifest(tmp_path, output_path, digest(expected_bytes))
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    failures = validate_outputs.validate()

    assert failures == [
        (
            f"Hash mismatch for {output_path}: expected {digest(expected_bytes)}, "
            f"got {digest(corrupt_bytes)}"
        )
    ]


def test_validate_reports_missing_required_output_despite_stale_manifest(tmp_path, monkeypatch):
    output_path = "outputs/tables/missing.csv"
    expected_hash = digest(b"expected\n")

    configure_expected(
        tmp_path,
        [{"path": output_path, "sha256": expected_hash, "required": True}],
    )
    write_stale_manifest(tmp_path, output_path, expected_hash)
    monkeypatch.setattr(validate_outputs, "BASE_DIR", tmp_path)

    assert validate_outputs.validate() == [f"Missing required output: {output_path}"]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    configure_expected(
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
