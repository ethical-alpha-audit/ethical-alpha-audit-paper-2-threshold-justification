# Beyond 'Magic Numbers': A Threshold Justification Stack for Clinical AI Governance

[![DOI](https://zenodo.org/badge/1194630564.svg)](https://doi.org/10.5281/zenodo.19499798)

> **Paper 3** of the Ethical Alpha Audit research programme
>
> Author: Walter Brown — Ethical Alpha Audit
> ORCID: [0000-0002-6050-8522](https://orcid.org/0000-0002-6050-8522)
>
> Target journal: *BMJ Health & Care Informatics*

This repository combines two complementary scopes for Paper 3:

1. **Framework-comparison work** (notebooks 01–04, repository v1.0.0 baseline) — renders manuscript Tables 1–3, TJS record schemas, and release validation.
2. **Computational sensitivity analysis** (notebooks 05–08, package `tjs_sensitivity/`, added 2026-05-03) — models how variation in inter-rater agreement (κ) on the Negative Harm Test propagates to four governance outcomes under stated modelling assumptions.

> ## Non-validation disclaimer (sensitivity work)
>
> The κ-sensitivity simulation in `tjs_sensitivity/` is a **computational sensitivity analysis** under stated modelling assumptions. **It is not a validation of the Threshold Justification Stack. It does not estimate κ values for any real institutional setting. It does not substitute for human inter-rater validation.** The κ tolerance regime derived from the simulation is *normative-from-analysis* and is replaceable by empirical pilot data when available. See [`docs/sensitivity/non_validation_disclaimer.md`](docs/sensitivity/non_validation_disclaimer.md) for the full statement and [`docs/sensitivity/modelling_assumptions.md`](docs/sensitivity/modelling_assumptions.md) for full assumption disclosure.

## Reviewer quick validation (no execution required)

```bash
python scripts/validate_outputs.py
```

**Expected result:** `VALIDATION PASSED`

This checks every output file (framework-comparison **and** sensitivity) against its pinned SHA-256 digest. No notebook execution, no dependencies beyond Python stdlib. A passing result confirms the checked-in outputs are byte-identical to those produced by the deterministic pipeline.

## Reproducing the full pipeline

Requires Python 3.10 or later.

```bash
pip install -r requirements.txt
python reproduce_all.py
```

`reproduce_all.py` runs the full 4-step orchestration covering both scopes:

1. **Notebook execution** — all 8 notebooks (01–04 framework + 05–08 sensitivity), fresh-kernel, in declared order
2. **Sensitivity simulation re-execution** — `python -m tjs_sensitivity.simulation` (regenerates `outputs/sensitivity/tables/*` + `outputs/sensitivity/monte_carlo_logs/*`); `python -m tjs_sensitivity.figures` (regenerates `outputs/sensitivity/figures/*`)
3. **Manifest generation** — SHA-256 hash manifest of all outputs
4. **Output validation** — verify hashes match expected baselines

Expected total runtime on commodity hardware: under 60 seconds (sensitivity simulation runs in under 15 seconds; notebook execution dominates).

## What this repository contains

| Scope | Component | Description |
|---|---|---|
| Framework-comparison | 3 manuscript tables | Structured renderings of Tables 1–3 (failure mechanisms, TJS specification, framework comparison) |
| Framework-comparison | 2 governance mappings | TJS-to-NHS artefact crosswalk and gaming resistance pathways |
| Framework-comparison | 1 glossary | Consolidated key term definitions from the manuscript |
| Framework-comparison | 2 illustrative TJS records | Proposed JSON schema for Primary Safety (6-layer) and Secondary Operational (3-layer) threshold documentation |
| Framework-comparison | 4 Jupyter notebooks (01–04) | Explanatory notebooks rendering the above from structured JSON source data |
| Sensitivity | 6-module simulation package | `tjs_sensitivity/` — rater model, outcome computation, Monte Carlo harness, simulation runner, figure generator |
| Sensitivity | κ × π scenario grid | 7 κ values × 4 base-rate scenarios = 28 scenarios; 100 replicates × 1,000 thresholds per scenario |
| Sensitivity | 4 Jupyter notebooks (05–08) | Narrative-first notebooks covering simulation design, primary results, robustness checks, discussion |
| Sensitivity | 2 publication figures | Main κ-outcomes figure + supplementary κ × π grid figure |
| Sensitivity | 3 result tables | `sensitivity_full_grid.csv`, `sensitivity_main_pi_010.csv`, `rater_model_verification.csv` |
| Sensitivity | 28 per-replicate CSV logs | One file per scenario, persisted for adversarial reproduction inspection |
| Both scopes | Deterministic harness | Full execution, hashing, validation, HTML export pipeline |
| Both scopes | Comprehensive test suite | Structural and reproducibility tests for both scopes |

## Repository structure

```
manuscript/                    Canonical manuscript and supplementary materials (.docx)
data/tables/                   Structured JSON for framework-comparison tables
data/schemas/                  Illustrative TJS record structures (proposed, not validated)
inputs/sensitivity/            κ grid, base-rate grid, master seed for simulation
tjs_sensitivity/               Sensitivity simulation source modules (rater model,
                               outcomes, Monte Carlo, simulation runner, figures,
                               bootstrap helpers)
notebooks/                     8 Jupyter notebooks (01–04 framework, 05–08 sensitivity)
scripts/                       Execution harness (notebook runner, hash validator,
                               HTML export, sensitivity orchestration)
config/                        Determinism settings, expected outputs, trace map
outputs/tables/                Framework-comparison output tables (CSV)
outputs/schemas/               Rendered TJS record JSON examples
outputs/sensitivity/           Sensitivity outputs:
  ├── tables/                  Sensitivity result tables (CSV)
  ├── figures/                 Main + supplementary figures (PNG)
  ├── monte_carlo_logs/        Per-replicate simulation logs (28 CSVs)
  └── run_metadata.json        Run parameters and timing
docs/                          Methods note, provenance, reproducibility statement,
                               claim boundary statement, claim traceability matrix
docs/sensitivity/              Sensitivity-specific documentation:
  ├── simulation_design.md     Design parameters and analytical question
  ├── modelling_assumptions.md Full assumption disclosure
  └── non_validation_disclaimer.md  Epistemic positioning
docs/html/                     Static HTML exports for reading without code
tests/                         Structural and reproducibility tests
tests/sensitivity/             Sensitivity-specific unit tests
```

## Notebooks

| # | Notebook | Scope | Purpose |
|---|----------|-------|---------|
| 01 | `01_tjs_framework_and_failure_mechanisms.ipynb` | framework | Render Table 1 (failure mechanisms), Table 2 (TJS specification), tier classification logic |
| 02 | `02_framework_comparison_and_mappings.ipynb` | framework | Render Table 3 (comparison matrix), NHS governance mapping, glossary |
| 03 | `03_tjs_record_schema_demonstration.ipynb` | framework | Load and display illustrative JSON TJS records for both tiers |
| 04 | `04_release_validation.ipynb` | framework | Verify repository structure, data integrity, output presence |
| 05 | `05_sensitivity_setup_and_methodology.ipynb` | sensitivity | Bridge from framework to sensitivity; model setup; parameter ranges; Monte Carlo configuration |
| 06 | `06_sensitivity_primary_results.ipynb` | sensitivity | Main sensitivity sweep results; primary tables; central findings (κ regimes) |
| 07 | `07_sensitivity_robustness_checks.ipynb` | sensitivity | Alternative model specifications; parameter-range extensions; robustness tables |
| 08 | `08_sensitivity_discussion_and_implications.ipynb` | sensitivity | Result interpretation under non-compensatory framing; implications for tier classification; limitations |

For code-free reading, see [`docs/html/`](docs/html/).

> Notebooks 05–08 will be authored at WS-2.6 Phase 8 (in flight). Until they are placed, this README's "Notebooks" table is forward-looking; the simulation source code, inputs, outputs, tests, and docs are all in place and the simulation can be run via `python -m tjs_sensitivity.simulation` independently of the notebook narrative.

## Sensitivity simulation: design summary

The simulation answers a single analytical question: *under stated modelling assumptions, how does variation in inter-rater agreement (κ) on the Negative Harm Test propagate to four governance outcomes given the default-to-Primary adjudication rule?*

- **Synthetic threshold population:** *n* = 1,000 thresholds per scenario
- **Rater model:** two independent raters per threshold; output alphabet {Primary, Secondary, Uncertain}; Uncertain rate held constant at 2%; per-rater error rate calibrated by numerical inversion to achieve target κ at given base rate
- **Adjudication:** default-to-Primary on disagreement or Uncertain
- **κ grid:** {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}
- **Base-rate grid:** π_Primary ∈ {0.05, 0.10, 0.20, 0.50}
- **Monte Carlo:** R = 100 replicates per scenario; total scenarios 7 × 4 = 28; total replicate runs 2,800
- **Determinism:** master seed in `inputs/sensitivity/seed.txt`; per-scenario substreams via `numpy.random.SeedSequence.spawn`

Three κ regimes follow analytically from the simulation outputs (under the stated modelling assumptions; not estimates of real-world performance):

- **κ < 0.40 — falsification regime.** Simulated unsafe-Secondary rate ≈ 1.5%–2.8% at π = 0.10. Negative Harm Test insufficient for unsupervised use under stated assumptions.
- **0.40 ≤ κ < 0.60 — caution regime.** Simulated unsafe-Secondary rate ≈ 0.3%–0.6% at π = 0.10.
- **κ ≥ 0.60 — operational regime.** Simulated unsafe-Secondary rate ≤ 0.07% at π = 0.10.

Full design detail: [`docs/sensitivity/simulation_design.md`](docs/sensitivity/simulation_design.md).
Full assumption disclosure: [`docs/sensitivity/modelling_assumptions.md`](docs/sensitivity/modelling_assumptions.md).

## What this repository does NOT contain

- No primary data were generated (Paper 3 is conceptual synthesis + computational sensitivity analysis)
- No empirical κ estimates for any real institutional setting (the simulation uses scenario-input κ values, not measurements)
- No companion-paper numerical results (Papers 1, 4, 5 results live in their own repositories — see [`docs/claim_boundary_statement.md`](docs/claim_boundary_statement.md))

## Claim traceability and boundary

This repository renders the Paper 3 manuscript and computationally explores its sensitivity claims. The full claim-to-artefact register lives in [`docs/claim_traceability.md`](docs/claim_traceability.md) (56 claims P3-C01..P3-C56 as of 2026-05-03; framework-comparison claims P3-C01..P3-C35 + sensitivity-extension claims P3-C36..P3-C56).

It does **not** reproduce numerical results from companion papers. The Discussion section of the manuscript cross-references companion findings (e.g. historical replay sensitivity, perturbation stability); these results belong to their respective repositories. See [`docs/claim_boundary_statement.md`](docs/claim_boundary_statement.md) for the full exclusion register.

## Citation

See [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata. If you reference this artefact, please cite both the manuscript and the Zenodo deposit.

## Licence

MIT — see [`LICENSE`](LICENSE).
