"""Pre-execution checks: verify all data, schema, notebook, and manuscript files exist."""
import json
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
