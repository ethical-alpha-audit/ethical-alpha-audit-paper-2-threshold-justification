# Simulation design

This document mirrors the manuscript Methods §"Computational sensitivity
analysis: design" sub-section and provides additional implementation detail
for reviewers and reproducers.

## Analytical question

The simulation answers a single analytical question:

> *Under stated modelling assumptions, how does variation in inter-rater
> agreement (κ) on the Negative Harm Test propagate to four governance
> outcomes — misclassification rates, net-Primary classification rate,
> unsafe-Secondary rate, and over-escalation burden — given the
> default-to-Primary adjudication rule specified in the manuscript?*

The simulation does not answer the empirical question of what κ obtains in
any real institution. That question is the subject of the proposed pilot
described in the manuscript Supplementary Appendix C addendum.

## Design

- **Synthetic threshold population:** *n* = 1,000 thresholds per scenario.
- **Rater model:** two independent raters per threshold; output alphabet
  {Primary, Secondary, Uncertain}; Uncertain rate held constant at 2%;
  per-rater error rate calibrated by numerical inversion to achieve the
  target κ at the given base rate.
- **Adjudication:** default-to-Primary on disagreement or Uncertain.
- **κ grid:** {0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80}.
- **Base-rate grid:** π_Primary ∈ {0.05, 0.10, 0.20, 0.50}.
- **Monte Carlo:** R = 100 replicates per scenario.
- **Total scenarios:** 7 × 4 = 28; total replicate runs: 2,800.
- **Determinism:** master seed in `inputs/seed.txt`; per-scenario substreams
  via `numpy.random.SeedSequence.spawn`.

## Outputs

For each scenario:

- realised κ (mean and MCSE) — verification check against target;
- misclassification rates pre-adjudication;
- net-Primary, unsafe-Secondary, over-escalation rates post-adjudication;
- documentation burden in additional hours per 100 thresholds.

The full κ × π grid is reported in `outputs/tables/sensitivity_full_grid.csv`.
The π = 0.10 sub-grid (used in the manuscript main-text figure and table) is
reported in `outputs/tables/sensitivity_main_pi_010.csv`.

Per-replicate logs are persisted in `outputs/monte_carlo_logs/` for
adversarial reproduction inspection.

## Figures

- `outputs/figures/figure_main_kappa_outcomes.png` — main-text figure: the
  four governance outcomes vs target κ at π = 0.10, with MCSE error bars
  and visual markers at κ = 0.40 (manuscript falsification condition) and
  κ = 0.60 (manuscript illustrative target).
- `outputs/figures/figure_supp_kappa_pi_grid.png` — supplement figure:
  unsafe-Secondary rate vs κ across the four base-rate scenarios.

## What the design does not do

See `non_validation_disclaimer.md` and `modelling_assumptions.md`.

## Reproducing the run

```bash
pip install -r requirements.txt
python -m tjs_sensitivity.simulation
python -m tjs_sensitivity.figures
pytest tests/
```

Expected runtime on commodity hardware: under 10 seconds for the simulation;
under 5 seconds for the figures; under 1 second for the tests.

## Verification

The `outputs/tables/rater_model_verification.csv` file reports realised κ
(mean across replicates and MCSE) against the target κ for every scenario.
At π = 0.10, realised κ matches target within 0.003 across the full grid.
At π = 0.05, the model's analytical maximum κ is approximately 0.71 (with
u = 0.02), so the κ = 0.80 target at π = 0.05 converges to the ceiling.
This is a transparent property of the rater model documented in
`modelling_assumptions.md` §2.
