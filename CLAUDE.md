# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Paper 3 of the Ethical Alpha Audit research programme — *"Beyond 'Magic Numbers': A Threshold Justification Stack for Clinical AI Governance"* (target journal: *BMJ Health & Care Informatics*). The repository combines two scopes that share one harness:

1. **Framework-comparison** (notebooks 01–04) — renders manuscript Tables 1–3, TJS record schemas, governance crosswalks, and release validation from structured JSON in `data/`. Deterministic transformations of static inputs; no randomness, no external data.
2. **κ-sensitivity simulation** (notebooks 05–08, package `tjs_sensitivity/`, added WS-2.6 on 2026-05-03) — Monte Carlo simulation of how inter-rater agreement (κ) on the Negative Harm Test propagates to governance outcomes. 7 κ values × 4 base rates × 100 replicates × 1,000 thresholds = 2,800 replicate runs. Bit-exactly reproducible via `numpy.random.SeedSequence.spawn` with master seed in [inputs/sensitivity/seed.txt](inputs/sensitivity/seed.txt).

The sensitivity simulation is a **computational sensitivity analysis under stated modelling assumptions** — not a validation of TJS, not an estimate of κ for any real institution. See [docs/sensitivity/non_validation_disclaimer.md](docs/sensitivity/non_validation_disclaimer.md).

## Common commands

```bash
# Reviewer quick validation (no execution; stdlib only) — verifies checked-in
# outputs match pinned SHA-256 digests in config/expected_outputs.json
python scripts/validate_outputs.py     # expects: VALIDATION PASSED

# Full pipeline (sensitivity simulation + figures + pytest + notebooks 01-08 +
# manifest + validation + HTML export). <60s on commodity hardware.
pip install -r requirements.txt
python reproduce_all.py

# Sensitivity simulation only (regenerates outputs/sensitivity/tables/*,
# monte_carlo_logs/*, run_metadata.json)
python -m tjs_sensitivity.simulation

# Sensitivity figures only
python -m tjs_sensitivity.figures

# Notebook execution only (clears outputs, runs 01-08 in declared order)
python scripts/notebook_runner.py

# Rebuild SHA-256 manifest of all outputs → logs/actual_manifest.json
python scripts/hash_manifest.py

# Tests (both top-level and sensitivity-specific)
pytest tests/ -v
pytest tests/sensitivity/test_outcomes.py -v       # single file
pytest tests/sensitivity/test_rater_model.py::test_name -v   # single test
```

`reproduce_all.py` runs sensitivity steps first, then notebooks, then manifest/validation/HTML — order matters because notebooks 06–08 read sensitivity outputs.

## Architecture

### Two scopes, one harness

The harness ([scripts/notebook_runner.py](scripts/notebook_runner.py), [scripts/hash_manifest.py](scripts/hash_manifest.py), [scripts/validate_outputs.py](scripts/validate_outputs.py)) is driven by three config files and is scope-agnostic:

- [config/harness_settings.json](config/harness_settings.json) — global determinism settings (`python_hash_seed: "0"`, `random_seed: 42`, fail-fast, clear-outputs)
- [config/notebook_plan.json](config/notebook_plan.json) — ordered list of notebooks to execute and their declared outputs
- [config/expected_outputs.json](config/expected_outputs.json) — every output file path with its pinned SHA-256 digest; the source of truth for `validate_outputs.py`
- [config/trace_map.json](config/trace_map.json) — claim-to-artefact traceability

To add a new output: add the file to `expected_outputs.json` with its SHA-256, and (if produced by a notebook) to that notebook's `expected_outputs` entry in `notebook_plan.json`.

### Path namespacing — important

When the sensitivity zip was integrated at WS-2.6, its original `inputs/` and `outputs/` paths collided with the framework-comparison's `inputs/` and `outputs/`. The fix (WS-2.6 Phase 11) was to namespace sensitivity content:

- Framework-comparison: `data/tables/`, `data/schemas/` → `outputs/tables/`, `outputs/schemas/`
- Sensitivity: `inputs/sensitivity/` → `outputs/sensitivity/{tables,figures,monte_carlo_logs}/`

This is why [tjs_sensitivity/simulation.py](tjs_sensitivity/simulation.py) reads from `inputs/sensitivity/` and writes to `outputs/sensitivity/` — do not "simplify" these paths back to the zip's original layout.

### Sensitivity package layout

[tjs_sensitivity/](tjs_sensitivity/) follows P4's `p4_replay/` per-paper-module pattern (chosen at WS-2.6 Phase 0 over `code/` and `src/`):

- `rater_model.py` — two-rater model; per-rater error rate calibrated by numerical inversion to hit target κ at given base rate
- `outcomes.py` — four governance outcomes computed from adjudicated decisions
- `monte_carlo.py` — single-scenario harness; uses `SeedSequence.spawn` for per-scenario substreams
- `simulation.py` — orchestrator; reads `inputs/sensitivity/`, writes `outputs/sensitivity/tables/` + `monte_carlo_logs/`
- `figures.py` — regenerates the two PNG figures
- `bootstrap.py` — `prepare_notebook()` helper; notebooks 05–08 call this to resolve repo root and put it on `sys.path`

Internal imports are relative (`from .monte_carlo import …`). When patching code that originated from the zip, references that say `code.X` should be `tjs_sensitivity.X` (the WS-2.6 Phase 4 substitution).

### Determinism

- `PYTHONHASHSEED=0` is set by both `reproduce_all.py` and `scripts/notebook_runner.py` before any notebook executes
- Framework-comparison notebooks (01–04) have **no randomness whatsoever** — outputs are deterministic transformations of static JSON in `data/`
- Sensitivity simulation determinism is verified at [notebooks/06_sensitivity_primary_results.ipynb](notebooks/06_sensitivity_primary_results.ipynb) §06.5 assert 3 with `|diff| < 1e-09`
- CSV output convention: `index=False, encoding='utf-8'`. JSON: `indent=2, sort_keys=True, ensure_ascii=False`. `.gitattributes` prevents EOL conversion on output files.
- `outputs/sensitivity/run_metadata.json` is the **only** output marked `required: false` in `expected_outputs.json` (it contains a wall-clock `elapsed_seconds` field that varies between runs). This is intentional; don't promote it to `required: true`.

## Repository policies

### No-commit-manuscripts policy

Manuscript and supplementary `.docx`/`.pdf` files are working-tree-only — they live on disk for PowerShell readiness gates and Jupyter workflows, but must NOT enter git history. The [.gitignore](.gitignore) enforces this with `inputs/*.docx`, `inputs/*.pdf`, `manuscript/*.docx`, `manuscript/*.pdf`. Do not `git add -f` these files.

### Canonical document tracking

[canonical_documents.yaml](canonical_documents.yaml) tracks the SHA-256 of every canonical manuscript/notebook artefact and is the source of truth for drift detection (WS-CANONICAL-SOURCE-AUTOMATION). When notebooks or the manuscript change, this file is the authoritative record of the new SHAs — keep it consistent with on-disk state.

### Hash mismatches on figures

Figure validation (`figure_main_kappa_outcomes.png`, `figure_supp_kappa_pi_grid.png`) uses byte-equality. If a reviewer re-execution produces a hash mismatch, the discipline (per [docs/reproducibility_statement.md](docs/reproducibility_statement.md)) is to surface it as a finding and investigate environment drift (matplotlib/font/backend) first; do not silently relax to `required: false`.

### Claim traceability

The manuscript's 56 claims (P3-C01..P3-C56) are mapped to artefacts in [docs/claim_traceability.md](docs/claim_traceability.md). Framework-comparison claims are P3-C01..P3-C35; sensitivity-extension claims are P3-C36..P3-C56. The boundary of what this repo does and does not reproduce (vs. companion papers P1, P4, P5) lives in [docs/claim_boundary_statement.md](docs/claim_boundary_statement.md).

## Environment

Python 3.10+ (3.11 in the conda env). Notebook-runtime deps are exact-pinned (`==`); simulation deps are range-pinned (`>=,<`) — this dual convention is intentional, see the comment block at the top of [requirements.txt](requirements.txt). A frozen [requirements.lock.txt](requirements.lock.txt) exists for byte-exact environment reproduction.
