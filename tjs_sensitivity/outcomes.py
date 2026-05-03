"""
Governance outcomes for the TJS κ-sensitivity simulation.

Given:
    - latent_true: array of true tiers ("Primary"/"Secondary")
    - rater_a, rater_b: simulated rater outputs ({"Primary","Secondary","Uncertain"})

The default-to-Primary adjudication rule:
    - If both raters say "Secondary": adjudicated = "Secondary"
    - Otherwise (any "Primary" or "Uncertain", or disagreement): adjudicated = "Primary"

This produces the four governance outcomes reported in the manuscript:

    misclass_primary_to_secondary
        P(rater pool classifies Secondary | latent-true Primary), pre-adjudication
        — proportion of latent-true Primary thresholds where BOTH raters
        independently said Secondary.

    misclass_secondary_to_primary
        P(rater pool classifies Primary | latent-true Secondary), pre-adjudication
        — proportion of latent-true Secondary thresholds where AT LEAST ONE
        rater said Primary or Uncertain (i.e., adjudicated will escalate).

    net_primary_rate
        P(adjudicated classification = Primary), post default-to-Primary

    unsafe_secondary_rate
        P(adjudicated classification = Secondary | latent-true Primary)
        — the residual safety failure: latent-true Primary thresholds that
        survive both raters and the default-to-Primary rule still classified
        Secondary. This requires BOTH raters to say Secondary on a Primary
        threshold; under the default-to-Primary rule that is the only path
        to a Secondary adjudication.

    over_escalation_rate
        P(adjudicated classification = Primary | latent-true Secondary)
        — burden imposed: latent-true Secondary thresholds escalated to
        Primary documentation.

    over_escalation_burden_hours_per_100
        Same as over_escalation_rate × n × (Primary - Secondary indicative
        time) per 100 thresholds. Indicative times from main-text
        Supplementary Appendix C: Primary 45–90 min midpoint = 67.5;
        Secondary 10–25 min midpoint = 17.5. Burden delta = 50 min/threshold.

NON-VALIDATION DISCLAIMER
-------------------------
All outcomes are computed under stated modelling assumptions. They do NOT
estimate any real-world institutional κ, misclassification rate, or
documentation burden. See ``docs/non_validation_disclaimer.md``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


PRIMARY = "Primary"
SECONDARY = "Secondary"
UNCERTAIN = "Uncertain"

# Indicative documentation-time figures from manuscript Supplementary Appendix C
# Primary Safety record: 45–90 min (midpoint 67.5)
# Secondary Operational record: 10–25 min (midpoint 17.5)
PRIMARY_MIN_MIDPOINT = 67.5
SECONDARY_MIN_MIDPOINT = 17.5
BURDEN_DELTA_MIN = PRIMARY_MIN_MIDPOINT - SECONDARY_MIN_MIDPOINT  # 50.0


@dataclass(frozen=True)
class Outcomes:
    """Single-replicate outcome record."""

    misclass_primary_to_secondary: float
    misclass_secondary_to_primary: float
    net_primary_rate: float
    unsafe_secondary_rate: float
    over_escalation_rate: float
    over_escalation_burden_hours_per_100: float
    realised_kappa: float
    n_latent_primary: int
    n_latent_secondary: int


def _adjudicate(rater_a: np.ndarray, rater_b: np.ndarray) -> np.ndarray:
    """Apply default-to-Primary adjudication to rater output arrays."""
    n = rater_a.size
    out = np.empty(n, dtype=object)
    for i in range(n):
        if rater_a[i] == SECONDARY and rater_b[i] == SECONDARY:
            out[i] = SECONDARY
        else:
            out[i] = PRIMARY
    return out


def compute_outcomes(
    latent_true: np.ndarray,
    rater_a: np.ndarray,
    rater_b: np.ndarray,
    realised_kappa: float,
) -> Outcomes:
    """Compute all governance outcomes for a single replicate.

    Parameters
    ----------
    latent_true : np.ndarray of object ("Primary" or "Secondary"), shape (n,)
    rater_a, rater_b : np.ndarray of object, shape (n,)
    realised_kappa : float
        The empirical κ realised by the rater pair on this replicate
        (computed once by the caller via verify_kappa for efficiency).

    Returns
    -------
    Outcomes
    """
    if not (latent_true.shape == rater_a.shape == rater_b.shape):
        raise ValueError("latent_true, rater_a, rater_b must have same shape")
    n = latent_true.size

    is_primary = latent_true == PRIMARY
    is_secondary = latent_true == SECONDARY
    n_p = int(is_primary.sum())
    n_s = int(is_secondary.sum())

    adjudicated = _adjudicate(rater_a, rater_b)

    # Pre-adjudication misclassification:
    # for latent Primary: both raters say Secondary
    if n_p > 0:
        both_secondary_on_primary = (
            (rater_a == SECONDARY) & (rater_b == SECONDARY) & is_primary
        )
        misclass_p_to_s = float(both_secondary_on_primary.sum() / n_p)
    else:
        misclass_p_to_s = 0.0

    # for latent Secondary: at least one rater says Primary or Uncertain
    # (i.e., adjudicated will be Primary)
    if n_s > 0:
        any_escalation_on_secondary = (
            ((rater_a != SECONDARY) | (rater_b != SECONDARY)) & is_secondary
        )
        misclass_s_to_p = float(any_escalation_on_secondary.sum() / n_s)
    else:
        misclass_s_to_p = 0.0

    # Post-adjudication
    net_primary = float((adjudicated == PRIMARY).sum() / n)

    if n_p > 0:
        unsafe_secondary = float(
            ((adjudicated == SECONDARY) & is_primary).sum() / n_p
        )
    else:
        unsafe_secondary = 0.0

    if n_s > 0:
        over_escalation = float(
            ((adjudicated == PRIMARY) & is_secondary).sum() / n_s
        )
    else:
        over_escalation = 0.0

    # Burden in additional hours per 100 thresholds, using indicative times.
    # over_escalation × proportion of population that is Secondary × n=100
    # × delta in minutes → hours
    secondary_share = n_s / n if n > 0 else 0.0
    extra_minutes_per_100 = (
        100.0 * secondary_share * over_escalation * BURDEN_DELTA_MIN
    )
    burden_hours_per_100 = extra_minutes_per_100 / 60.0

    return Outcomes(
        misclass_primary_to_secondary=misclass_p_to_s,
        misclass_secondary_to_primary=misclass_s_to_p,
        net_primary_rate=net_primary,
        unsafe_secondary_rate=unsafe_secondary,
        over_escalation_rate=over_escalation,
        over_escalation_burden_hours_per_100=burden_hours_per_100,
        realised_kappa=realised_kappa,
        n_latent_primary=n_p,
        n_latent_secondary=n_s,
    )
