"""
Monte Carlo replicate harness for the TJS κ-sensitivity simulation.

Each scenario (κ, π) is simulated R times with independent random streams
seeded from a master seed. Per-replicate outcomes are aggregated to means
and Monte Carlo standard errors (MCSE = SD / sqrt(R)).

This module is purely orchestration; rater behaviour and outcome
computation are imported from rater_model and outcomes.

NON-VALIDATION DISCLAIMER
-------------------------
See ``docs/non_validation_disclaimer.md``.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

from .outcomes import Outcomes, compute_outcomes
from .rater_model import (
    PRIMARY,
    SECONDARY,
    simulate_raters,
    verify_kappa,
)


@dataclass(frozen=True)
class ScenarioSummary:
    """Aggregated outcome record across R replicates for one scenario."""

    target_kappa: float
    base_rate_primary: float
    n_thresholds: int
    n_replicates: int
    realised_kappa_mean: float
    realised_kappa_mcse: float
    misclass_primary_to_secondary_mean: float
    misclass_primary_to_secondary_mcse: float
    misclass_secondary_to_primary_mean: float
    misclass_secondary_to_primary_mcse: float
    net_primary_rate_mean: float
    net_primary_rate_mcse: float
    unsafe_secondary_rate_mean: float
    unsafe_secondary_rate_mcse: float
    over_escalation_rate_mean: float
    over_escalation_rate_mcse: float
    over_escalation_burden_hours_per_100_mean: float
    over_escalation_burden_hours_per_100_mcse: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _generate_latent_population(
    n_thresholds: int, base_rate_primary: float, rng: np.random.Generator
) -> np.ndarray:
    """Draw n latent-true tier labels from a Bernoulli(π_primary)."""
    draws = rng.random(n_thresholds)
    out = np.where(draws < base_rate_primary, PRIMARY, SECONDARY)
    return out.astype(object)


def run_scenario(
    target_kappa: float,
    base_rate_primary: float,
    n_thresholds: int,
    n_replicates: int,
    master_seed: int,
    scenario_id: int,
) -> tuple[ScenarioSummary, list[Outcomes]]:
    """Run a single (κ, π) scenario for n_replicates Monte Carlo replicates.

    Each replicate uses a deterministic substream derived from
    (master_seed, scenario_id, replicate_id). This makes the entire run
    reproducible from a single seed and the scenario index ordering.

    Parameters
    ----------
    target_kappa : float
    base_rate_primary : float
    n_thresholds : int
    n_replicates : int
    master_seed : int
    scenario_id : int
        Index used to derive deterministic substreams; must be unique per
        scenario in any given run.

    Returns
    -------
    ScenarioSummary, list[Outcomes]
        The aggregated summary plus the per-replicate records (for
        Monte Carlo log persistence).
    """
    replicates: list[Outcomes] = []
    seed_seq = np.random.SeedSequence(master_seed, spawn_key=(scenario_id,))
    child_seqs = seed_seq.spawn(n_replicates)
    for r, child in enumerate(child_seqs):
        rng = np.random.default_rng(child)
        latent = _generate_latent_population(
            n_thresholds, base_rate_primary, rng
        )
        rater_a, rater_b = simulate_raters(
            latent_true=latent,
            target_kappa=target_kappa,
            base_rate_primary=base_rate_primary,
            rng=rng,
        )
        realised = verify_kappa(rater_a, rater_b)
        outc = compute_outcomes(latent, rater_a, rater_b, realised)
        replicates.append(outc)

    summary = _aggregate(
        replicates,
        target_kappa=target_kappa,
        base_rate_primary=base_rate_primary,
        n_thresholds=n_thresholds,
        n_replicates=n_replicates,
    )
    return summary, replicates


def _aggregate(
    replicates: list[Outcomes],
    *,
    target_kappa: float,
    base_rate_primary: float,
    n_thresholds: int,
    n_replicates: int,
) -> ScenarioSummary:
    """Compute means and MCSEs from per-replicate outcomes."""
    arr_kappa = np.array([r.realised_kappa for r in replicates])
    arr_p2s = np.array(
        [r.misclass_primary_to_secondary for r in replicates]
    )
    arr_s2p = np.array(
        [r.misclass_secondary_to_primary for r in replicates]
    )
    arr_net = np.array([r.net_primary_rate for r in replicates])
    arr_unsafe = np.array([r.unsafe_secondary_rate for r in replicates])
    arr_over = np.array([r.over_escalation_rate for r in replicates])
    arr_burden = np.array(
        [r.over_escalation_burden_hours_per_100 for r in replicates]
    )

    def _mcse(arr: np.ndarray) -> float:
        # Monte Carlo SE = sample SD / sqrt(R). Use ddof=1.
        if arr.size <= 1:
            return 0.0
        return float(np.std(arr, ddof=1) / np.sqrt(arr.size))

    return ScenarioSummary(
        target_kappa=target_kappa,
        base_rate_primary=base_rate_primary,
        n_thresholds=n_thresholds,
        n_replicates=n_replicates,
        realised_kappa_mean=float(arr_kappa.mean()),
        realised_kappa_mcse=_mcse(arr_kappa),
        misclass_primary_to_secondary_mean=float(arr_p2s.mean()),
        misclass_primary_to_secondary_mcse=_mcse(arr_p2s),
        misclass_secondary_to_primary_mean=float(arr_s2p.mean()),
        misclass_secondary_to_primary_mcse=_mcse(arr_s2p),
        net_primary_rate_mean=float(arr_net.mean()),
        net_primary_rate_mcse=_mcse(arr_net),
        unsafe_secondary_rate_mean=float(arr_unsafe.mean()),
        unsafe_secondary_rate_mcse=_mcse(arr_unsafe),
        over_escalation_rate_mean=float(arr_over.mean()),
        over_escalation_rate_mcse=_mcse(arr_over),
        over_escalation_burden_hours_per_100_mean=float(arr_burden.mean()),
        over_escalation_burden_hours_per_100_mcse=_mcse(arr_burden),
    )
