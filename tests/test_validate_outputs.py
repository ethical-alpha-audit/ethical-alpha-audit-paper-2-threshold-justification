import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_outputs.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_outputs", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_repo(tmp_path: Path, expected_files: list[dict]) -> Path:
    repo = tmp_path / "repo"
    write_json(repo / "config" / "expected_outputs.json", {"files": expected_files})
    write_json(
        repo / "logs" / "actual_manifest.json",
        {
            "files": [
                {"path": item["path"], "sha256": item.get("sha256", ""), "exists": True}
                for item in expected_files
            ]
        },
    )
    return repo


def test_validate_hashes_live_output_not_stale_manifest(tmp_path, monkeypatch):
    good_bytes = b"approved output\n"
    repo = make_repo(
        tmp_path,
        [
            {
                "path": "outputs/tables/table1.csv",
                "sha256": sha256_bytes(good_bytes),
                "required": True,
            }
        ],
    )
    output = repo / "outputs" / "tables" / "table1.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"corrupted output\n")

    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", repo)

    failures = validator.validate()

    assert len(failures) == 1
    assert failures[0].startswith("Hash mismatch for outputs/tables/table1.csv")


def test_validate_reports_missing_required_live_output(tmp_path, monkeypatch):
    repo = make_repo(
        tmp_path,
        [
            {
                "path": "outputs/tables/missing.csv",
                "sha256": sha256_bytes(b"expected\n"),
                "required": True,
            }
        ],
    )

    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", repo)

    assert validator.validate() == ["Missing required output: outputs/tables/missing.csv"]


def test_validate_allows_missing_optional_unpinned_output(tmp_path, monkeypatch):
    repo = make_repo(
        tmp_path,
        [
            {
                "path": "outputs/sensitivity/run_metadata.json",
                "sha256": "",
                "required": False,
            }
        ],
    )

    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", repo)

    assert validator.validate() == []


def test_validate_rejects_required_output_without_pinned_hash(tmp_path, monkeypatch):
    repo = make_repo(
        tmp_path,
        [
            {
                "path": "outputs/tables/table1.csv",
                "sha256": "",
                "required": True,
            }
        ],
    )
    output = repo / "outputs" / "tables" / "table1.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("content\n", encoding="utf-8")

    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", repo)

    assert validator.validate() == [
        "Missing pinned SHA-256 for required output: outputs/tables/table1.csv"
    ]


def test_validate_accepts_matching_live_output_without_manifest(tmp_path, monkeypatch):
    output_bytes = b"approved output\n"
    repo = tmp_path / "repo"
    write_json(
        repo / "config" / "expected_outputs.json",
        {
            "files": [
                {
                    "path": "outputs/tables/table1.csv",
                    "sha256": sha256_bytes(output_bytes),
                    "required": True,
                }
            ]
        },
    )
    output = repo / "outputs" / "tables" / "table1.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(output_bytes)

    validator = load_validator()
    monkeypatch.setattr(validator, "BASE_DIR", repo)

    assert validator.validate() == []
