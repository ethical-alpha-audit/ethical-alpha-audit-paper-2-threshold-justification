# Reproducibility Statement

## How to reproduce

From the repository root, with dependencies installed per `requirements.txt`:

```bash
python reproduce_all.py
```

This executes 4 notebooks in sequence, computes SHA-256 hashes of all 8 output files, and validates them against `config/expected_outputs.json`. A passing result (`ALL STEPS PASSED`) confirms bitwise-identical reproduction.

## Determinism guarantees

- `PYTHONHASHSEED=0` enforced by harness
- No randomness in any notebook (no `random`, no `numpy.random`, no Monte Carlo)
- No external data fetching (all inputs are checked-in JSON files)
- No system-dependent operations (no timestamps, no PIDs in outputs)
- All CSV output uses `index=False, encoding='utf-8'`
- All JSON output uses `indent=2, sort_keys=True, ensure_ascii=False`
- `.gitattributes` prevents line-ending conversion for output files

## Validation without execution

```bash
python scripts/validate_outputs.py
```

Requires only Python stdlib. Verifies checked-in outputs match expected hashes.

## Nature of this repository

This is a **conceptual framework repository**. Notebooks render structured data extracted from the manuscript — they do not perform computational experiments, statistical analyses, or simulations. All outputs are deterministic transformations of static JSON inputs derived from the published text.

## WS-2.6 sensitivity-extension addendum

> The framing above describes the original framework-comparison scope (notebooks 01–04). At WS-2.6 the κ-sensitivity simulation was integrated, adding notebooks 05–08, the `tjs_sensitivity/` package, and the `inputs/sensitivity/` + `outputs/sensitivity/` namespaces. The combined repository contains 8 notebooks and ~120 deterministic outputs (see `MANIFEST.sha256`). The sensitivity simulation does use Monte Carlo, but its outputs are bit-exactly reproducible via `numpy.random.SeedSequence` with explicit `spawn_key` per scenario (verified at `notebooks/06_sensitivity_primary_results.ipynb` §06.5 assert 3, `|diff| < 1e-09`).

### Figure-validation discipline

Figure validation (`outputs/sensitivity/figures/figure_main_kappa_outcomes.png` and `figure_supp_kappa_pi_grid.png`) uses byte-equality. The canonical reference is the execution environment recorded in `outputs/sensitivity/run_metadata.json`. If reviewers re-execute on different `matplotlib` / font / backend configurations and observe hash mismatches, that is a finding worth surfacing rather than silenced — investigate environment drift first; relax to `required: false` only if cross-platform variation is empirically confirmed.

### Intentional non-deterministic flag

`outputs/sensitivity/run_metadata.json` is the **only** sensitivity output marked `required: false` in `config/expected_outputs.json`. It contains a wall-clock elapsed-time field (`elapsed_seconds` in the simulation's `run_metadata` write) that genuinely varies between runs. Its `required: false` flag is documented intentional defensive flagging, not a hedge against unmeasured environment variation.
