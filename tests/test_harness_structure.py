from pathlib import Path


def test_harness_files_exist():
    base = Path(__file__).resolve().parents[1]
    required = [
        base / "reproduce_all.py",
        base / "config" / "notebook_plan.json",
        base / "config" / "expected_outputs.json",
        base / "config" / "harness_settings.json",
        base / "config" / "trace_map.json",
    ]
    for path in required:
        assert path.exists(), f"Missing required file: {path}"
