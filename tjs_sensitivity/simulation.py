"""
Main simulation runner.

Reads:
    inputs/kappa_grid.json
    inputs/base_rate_grid.json
    inputs/seed.txt

Writes:
    outputs/tables/sensitivity_full_grid.csv
    outputs/tables/sensitivity_main_pi_010.csv
    outputs/tables/rater_model_verification.csv
    outputs/monte_carlo_logs/replicates_scenario_<id>.csv  (one file per scenario)
    outputs/run_metadata.json

Run with:
    python -m tjs_sensitivity.simulation
or:
    python tjs_sensitivity/simulation.py     (when invoked from repo root)

NON-VALIDATION DISCLAIMER
-------------------------
See ``docs/non_validation_disclaimer.md``.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

# Allow running as both `python -m tjs_sensitivity.simulation` and `python tjs_sensitivity/simulation.py`
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tjs_sensitivity.monte_carlo import run_scenario, ScenarioSummary  # noqa: E402
    from tjs_sensitivity.outcomes import Outcomes  # noqa: E402
else:
    from .monte_carlo import run_scenario, ScenarioSummary
    from .outcomes import Outcomes


REPO_ROOT = Path(__file__).resolve().parent.parent
INPUTS_DIR = REPO_ROOT / "inputs"
OUTPUTS_DIR = REPO_ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
MC_LOG_DIR = OUTPUTS_DIR / "monte_carlo_logs"


def _load_inputs() -> tuple[list[float], list[float], int]:
    with open(INPUTS_DIR / "kappa_grid.json") as f:
        kappa_grid = json.load(f)["kappa_values"]
    with open(INPUTS_DIR / "base_rate_grid.json") as f:
        pi_grid = json.load(f)["base_rate_primary_values"]
    with open(INPUTS_DIR / "seed.txt") as f:
        seed = int(f.read().strip())
    return kappa_grid, pi_grid, seed


def _summary_to_row(s: ScenarioSummary) -> dict[str, object]:
    return s.as_dict()


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_replicate_log(
    scenario_id: int, replicates: list[Outcomes]
) -> None:
    rows = []
    for i, r in enumerate(replicates):
        rows.append(
            {
                "scenario_id": scenario_id,
                "replicate_id": i,
                "realised_kappa": r.realised_kappa,
                "misclass_primary_to_secondary": (
                    r.misclass_primary_to_secondary
                ),
                "misclass_secondary_to_primary": (
                    r.misclass_secondary_to_primary
                ),
                "net_primary_rate": r.net_primary_rate,
                "unsafe_secondary_rate": r.unsafe_secondary_rate,
                "over_escalation_rate": r.over_escalation_rate,
                "over_escalation_burden_hours_per_100": (
                    r.over_escalation_burden_hours_per_100
                ),
                "n_latent_primary": r.n_latent_primary,
                "n_latent_secondary": r.n_latent_secondary,
            }
        )
    _write_csv(MC_LOG_DIR / f"replicates_scenario_{scenario_id:02d}.csv", rows)


def main(
    n_thresholds: int = 1000,
    n_replicates: int = 100,
) -> None:
    kappa_grid, pi_grid, master_seed = _load_inputs()

    started = time.time()
    print(
        f"[simulation] κ grid = {kappa_grid}\n"
        f"[simulation] π grid = {pi_grid}\n"
        f"[simulation] n_thresholds = {n_thresholds}\n"
        f"[simulation] n_replicates = {n_replicates}\n"
        f"[simulation] master seed = {master_seed}"
    )

    # Build scenario list with deterministic ordering
    scenarios: list[tuple[int, float, float]] = []
    sid = 0
    for pi in pi_grid:
        for k in kappa_grid:
            scenarios.append((sid, k, pi))
            sid += 1

    full_rows: list[dict[str, object]] = []
    main_rows: list[dict[str, object]] = []  # π = 0.10 only
    verify_rows: list[dict[str, object]] = []

    for scenario_id, kappa, pi in scenarios:
        summary, replicates = run_scenario(
            target_kappa=kappa,
            base_rate_primary=pi,
            n_thresholds=n_thresholds,
            n_replicates=n_replicates,
            master_seed=master_seed,
            scenario_id=scenario_id,
        )
        row = _summary_to_row(summary)
        row["scenario_id"] = scenario_id
        full_rows.append(row)
        if abs(pi - 0.10) < 1e-9:
            main_rows.append(row)
        verify_rows.append(
            {
                "scenario_id": scenario_id,
                "target_kappa": kappa,
                "realised_kappa_mean": summary.realised_kappa_mean,
                "realised_kappa_mcse": summary.realised_kappa_mcse,
                "abs_diff": abs(
                    summary.realised_kappa_mean - kappa
                ),
                "base_rate_primary": pi,
            }
        )
        _write_replicate_log(scenario_id, replicates)
        print(
            f"  scenario {scenario_id:02d}: κ_target={kappa:.2f} "
            f"π={pi:.2f} κ_realised={summary.realised_kappa_mean:.4f} "
            f"unsafe_sec={summary.unsafe_secondary_rate_mean:.4f} "
            f"over_esc={summary.over_escalation_rate_mean:.4f}"
        )

    _write_csv(TABLES_DIR / "sensitivity_full_grid.csv", full_rows)
    _write_csv(TABLES_DIR / "sensitivity_main_pi_010.csv", main_rows)
    _write_csv(TABLES_DIR / "rater_model_verification.csv", verify_rows)

    elapsed = time.time() - started
    metadata = {
        "n_thresholds": n_thresholds,
        "n_replicates": n_replicates,
        "master_seed": master_seed,
        "kappa_grid": kappa_grid,
        "base_rate_grid": pi_grid,
        "n_scenarios": len(scenarios),
    }
    with open(OUTPUTS_DIR / "run_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[simulation] complete: {len(scenarios)} scenarios in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
