"""Reproduce all Paper 3 outputs from source data.

Usage:
    python reproduce_all.py

Steps (extended at WS-2.6 to include sensitivity orchestration):

Sensitivity simulation (added at WS-2.6 Phase 10):
    1. Re-execute the κ-sensitivity Monte Carlo simulation
       (regenerates outputs/sensitivity/tables/*, monte_carlo_logs/*, run_metadata.json)
    2. Re-render the sensitivity figures
       (regenerates outputs/sensitivity/figures/*)
    3. Run pytest (covers tests/ and tests/sensitivity/)

Framework comparison (P3 v1.0.0 baseline):
    4. Execute all notebooks in declared order (notebooks 01-08; clearing outputs first)
    5. Generate SHA-256 hash manifest of all outputs (framework + sensitivity)
    6. Validate output hashes against expected baselines
    7. Export code-collapsed HTML for academic readers

Determinism: seeded by config/harness_settings.json's python_hash_seed and by the
master seed in inputs/sensitivity/seed.txt. The sensitivity simulation produces
bit-exact reproducible outputs (verified at notebook 06 assert 3 with diff = 0.0).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_step(label, cmd):
    print(f"=== {label} ===")
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True)
    if result.returncode != 0:
        print(f"FAIL: {label}")
        sys.exit(result.returncode)
    print(f"OK: {label}")


def main():
    settings = json.loads(
        (BASE_DIR / "config" / "harness_settings.json").read_text(encoding="utf-8")
    )
    os.environ["PYTHONHASHSEED"] = str(settings["python_hash_seed"])

    # Sensitivity orchestration (WS-2.6 Phase 10 additions)
    run_step("Sensitivity simulation re-execution", [sys.executable, "-m", "tjs_sensitivity.simulation"])
    run_step("Sensitivity figure regeneration", [sys.executable, "-m", "tjs_sensitivity.figures"])
    run_step("pytest (tests/ + tests/sensitivity/)", [sys.executable, "-m", "pytest", "tests/", "-v"])

    # Framework-comparison orchestration (P3 v1.0.0 baseline)
    run_step("Notebook execution (01-08)", [sys.executable, "scripts/notebook_runner.py"])
    run_step("Manifest generation", [sys.executable, "scripts/hash_manifest.py"])
    run_step("Output validation", [sys.executable, "scripts/validate_outputs.py"])
    run_step("HTML export", [sys.executable, "scripts/export_html.py"])

    print("ALL STEPS PASSED")


if __name__ == "__main__":
    main()
