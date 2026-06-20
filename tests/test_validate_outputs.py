import hashlib
import json
from pathlib import Path

import scripts.validate_outputs as validate_outputs


def write_expected(root: Path, files: list[dict]) -> None:
    config_dir = root / "config"
    config_dir.mkdir()
    (config_dir / "expected_outputs.json").write_text(
        json.dumps({"files": files}),
        encoding="utf-8",
    )


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_validate(root: Path, monkeypatch) -> list[str]:
    monkeypatch.setattr(validate_outputs, "BASE_DIR", root)
    return validate_outputs.validate()


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    approved = b"approved output\n"
    corrupted = b"corrupted output\n"
    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir()
    output.write_bytes(corrupted)
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": digest(approved),
                "required": True,
            }
        ],
    )

    failures = run_validate(tmp_path, monkeypatch)

    assert len(failures) == 1
    assert "Hash mismatch for outputs/result.csv" in failures[0]
    assert digest(corrupted) in failures[0]


def test_validate_reports_missing_required_output(tmp_path, monkeypatch):
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/missing.csv",
                "sha256": digest(b"expected\n"),
                "required": True,
            }
        ],
    )

    assert run_validate(tmp_path, monkeypatch) == [
        "Missing required output: outputs/missing.csv"
    ]


def test_validate_allows_missing_optional_output(tmp_path, monkeypatch):
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/optional.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    assert run_validate(tmp_path, monkeypatch) == []


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    content = b"approved output\n"
    output = tmp_path / "outputs" / "result.csv"
    output.parent.mkdir()
    output.write_bytes(content)
    write_expected(
        tmp_path,
        [
            {
                "path": "outputs/result.csv",
                "sha256": digest(content),
                "required": True,
            }
        ],
    )

    assert run_validate(tmp_path, monkeypatch) == []
