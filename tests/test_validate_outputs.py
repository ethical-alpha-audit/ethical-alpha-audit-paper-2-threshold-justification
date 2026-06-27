import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_outputs import validate  # noqa: E402


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _write_expected(base: Path, files: list[dict]) -> None:
    config = base / "config"
    config.mkdir()
    (config / "expected_outputs.json").write_text(
        json.dumps({"files": files}, indent=2),
        encoding="utf-8",
    )


def _write_file(base: Path, relative_path: str, content: bytes) -> Path:
    path = base / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_validate_hashes_live_output_not_stale_manifest(tmp_path: Path) -> None:
    good_content = b"canonical output\n"
    path = "outputs/tables/example.csv"
    expected_hash = _sha256(good_content)
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    _write_file(tmp_path, path, b"corrupted output\n")

    # A stale generated manifest must not mask corruption in the live artefact.
    _write_file(
        tmp_path,
        "logs/actual_manifest.json",
        json.dumps(
            {
                "files": [
                    {"path": path, "sha256": expected_hash, "exists": True},
                ],
            }
        ).encode("utf-8"),
    )

    failures = validate(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith(f"Hash mismatch for {path}:")


def test_validate_reports_missing_required_live_output(tmp_path: Path) -> None:
    path = "outputs/tables/missing.csv"
    expected_hash = _sha256(b"canonical output\n")
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": expected_hash, "required": True}],
    )
    _write_file(
        tmp_path,
        "logs/actual_manifest.json",
        json.dumps(
            {
                "files": [
                    {"path": path, "sha256": expected_hash, "exists": True},
                ],
            }
        ).encode("utf-8"),
    )

    assert validate(tmp_path) == [f"Missing required output: {path}"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path: Path) -> None:
    _write_expected(
        tmp_path,
        [{"path": "outputs/sensitivity/run_metadata.json", "sha256": "", "required": False}],
    )

    assert validate(tmp_path) == []


def test_validate_rejects_required_output_without_expected_hash(tmp_path: Path) -> None:
    path = "outputs/tables/unpinned.csv"
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": "", "required": True}],
    )
    _write_file(tmp_path, path, b"present but unpinned\n")

    assert validate(tmp_path) == [f"Missing expected SHA-256 for required output: {path}"]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path: Path) -> None:
    content = b"canonical output\n"
    path = "outputs/tables/example.csv"
    _write_expected(
        tmp_path,
        [{"path": path, "sha256": _sha256(content), "required": True}],
    )
    _write_file(tmp_path, path, content)

    assert validate(tmp_path) == []
