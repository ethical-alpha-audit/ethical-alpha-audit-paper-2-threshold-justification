"""Pre-execution checks: verify all data, schema, notebook, and manuscript files exist."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_data_table_files_exist():
    expected = [
        "table1_failure_mechanisms.json",
        "table2_tjs_specification.json",
        "table3_framework_comparison.json",
        "glossary.json",
        "nhs_governance_mapping.json",
        "gaming_resistance_pathways.json",
    ]
    for fname in expected:
        path = ROOT / "data" / "tables" / fname
        assert path.exists(), f"Missing data file: {fname}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"Invalid JSON structure in {fname}"


def test_schema_files_exist():
    expected = [
        "tjs_record_primary_safety.json",
        "tjs_record_secondary_operational.json",
    ]
    for fname in expected:
        path = ROOT / "data" / "schemas" / fname
        assert path.exists(), f"Missing schema file: {fname}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "_epistemic_status" in data, f"Missing _epistemic_status in {fname}"


def test_notebooks_exist():
    for nb in [
        "01_tjs_framework_and_failure_mechanisms",
        "02_framework_comparison_and_mappings",
        "03_tjs_record_schema_demonstration",
        "04_release_validation",
    ]:
        assert (ROOT / "notebooks" / f"{nb}.ipynb").exists(), f"Missing {nb}.ipynb"


def test_manuscript_files_exist():
    """Portfolio inputs contract (attachment_requirements.json paper-3) + local manuscript copies."""
    inputs = ROOT / "inputs"
    assert (inputs / "supplementary.pdf").exists(), "Missing inputs/supplementary.pdf"
    assert (inputs / "manuscript.pdf").exists() or (inputs / "manuscript.docx").exists(), (
        "Missing inputs/manuscript.pdf or inputs/manuscript.docx"
    )
    assert (ROOT / "manuscript" / "Paper3_Manuscript.docx").exists()
    assert (ROOT / "manuscript" / "Paper3_Supplementary_Materials.docx").exists()


def test_config_exists():
    assert (ROOT / "config" / "notebook_plan.json").exists()
    assert (ROOT / "config" / "harness_settings.json").exists()
    assert (ROOT / "config" / "expected_outputs.json").exists()
    assert (ROOT / "config" / "trace_map.json").exists()


def test_repro_manifest_uses_canonical_repository_name():
    manifest = json.loads((ROOT / "repro_manifest.json").read_text(encoding="utf-8"))
    canonical = (ROOT / "canonical_documents.yaml").read_text(encoding="utf-8")
    repo_directory = re.search(r"^  repo_directory: (\S+)$", canonical, re.MULTILINE)

    assert repo_directory, "canonical_documents.yaml has no paper.repo_directory"
    assert manifest["repo_name"] == repo_directory.group(1)


def test_canonical_notebook_metadata_matches_live_files():
    canonical = (ROOT / "canonical_documents.yaml").read_text(encoding="utf-8")
    records = re.findall(
        r"      - filename: (notebooks/[^\n]+)\n"
        r"        canonical_path: [^\n]+\n"
        r"        source_location: [^\n]+\n"
        r"        canonical_sha256: ([0-9a-f]{64})\n"
        r"        size_bytes: (\d+)",
        canonical,
    )

    assert len(records) == 8, "Expected canonical metadata for all eight notebooks"
    for relative_path, expected_hash, expected_size in records:
        notebook = ROOT / relative_path
        assert notebook.stat().st_size == int(expected_size), f"Size drift: {relative_path}"
        assert hashlib.sha256(notebook.read_bytes()).hexdigest() == expected_hash, (
            f"SHA-256 drift: {relative_path}"
        )
