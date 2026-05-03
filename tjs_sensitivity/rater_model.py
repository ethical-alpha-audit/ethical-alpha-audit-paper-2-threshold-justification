"""
Rater model for the TJS κ-sensitivity simulation.

Two simulated raters classify each synthetic threshold as one of
{"Primary", "Secondary", "Uncertain"}. The rater behaviour is parameterised
to target a specified Cohen's κ on the binary collapse (Uncertain → Primary,
i.e., the default-to-Primary rule).

This file contains:
    - kappa_to_error_rate: analytical mapping for a symmetric error model
    - simulate_raters: produce two rater outputs per threshold given target κ
    - verify_kappa: empirical κ check against target
    - cohen_kappa_binary: Cohen's κ for binary classifications

NON-VALIDATION DISCLAIMER
-------------------------
This module is part of a computational sensitivity analysis. The κ values
parameterising the rater model are NOT empirical estimates of inter-rater
agreement in any clinical AI governance setting. They are scenario inputs
for a sensitivity analysis. See ``docs/non_validation_disclaimer.md``.
"""
from __future__ import annotations

import numpy as np


# Rater outputs
PRIMARY = "Primary"
SECONDARY = "Secondary"
UNCERTAIN = "Uncertain"

# Internal numeric encoding for κ computation
# Under the default-to-Primary rule, Uncertain collapses to Primary for κ.
_PRIMARY_INT = 1
_SECONDARY_INT = 0


def _binary_collapse(label: str) -> int:
    """Collapse rater output to binary under default-to-Primary rule.

    Uncertain → Primary (1); Secondary → Secondary (0); Primary → Primary (1).
    """
    if label == SECONDARY:
        return _SECONDARY_INT
    return _PRIMARY_INT


def cohen_kappa_binary(rater_a: np.ndarray, rater_b: np.ndarray) -> float:
    """Cohen's κ for two binary classification arrays.

    Parameters
    ----------
    rater_a, rater_b : np.ndarray of int (0 or 1), same shape

    Returns
    -------
    float : Cohen's κ. Returns 0.0 when chance agreement equals 1.0
            (degenerate case where one class is absent from both raters).
    """
    if rater_a.shape != rater_b.shape:
        raise ValueError("rater_a and rater_b must have the same shape")
    n = rater_a.size
    if n == 0:
        return 0.0
    po = float(np.mean(rater_a == rater_b))
    p_a1 = float(np.mean(rater_a == 1))
    p_b1 = float(np.mean(rater_b == 1))
    pe = p_a1 * p_b1 + (1.0 - p_a1) * (1.0 - p_b1)
    if pe >= 1.0:
        return 0.0
    return (po - pe) / (1.0 - pe)


def _expected_kappa_from_error(
    error_rate: float,
    base_rate_primary: float,
    uncertain_prob: float,
) -> float:
    """Analytical expected κ given a per-rater error model and base rate.

    Under independent raters, each producing:
        Uncertain with prob u (any latent)
        else correct with prob (1-e), wrong with prob e

    With Uncertain → Primary in binary collapse, the per-rater
    P(rater_binary = Primary | latent = X) is:

        latent Primary:   p_pp = u + (1-u)(1-e)
        latent Secondary: p_sp = u + (1-u)e

    Joint agreement probabilities (independent raters):

        P(agree | latent Primary)   = p_pp^2 + (1-p_pp)^2
        P(agree | latent Secondary) = p_sp^2 + (1-p_sp)^2

    Marginal P(rater = Primary) = π·p_pp + (1-π)·p_sp.

    Po and Pe are then computed and κ = (Po - Pe) / (1 - Pe).
    """
    e = error_rate
    u = uncertain_prob
    pi = base_rate_primary

    p_pp = u + (1.0 - u) * (1.0 - e)
    p_sp = u + (1.0 - u) * e

    p_agree_p = p_pp ** 2 + (1.0 - p_pp) ** 2
    p_agree_s = p_sp ** 2 + (1.0 - p_sp) ** 2
    po = pi * p_agree_p + (1.0 - pi) * p_agree_s

    p_marg_primary = pi * p_pp + (1.0 - pi) * p_sp
    pe = p_marg_primary ** 2 + (1.0 - p_marg_primary) ** 2

    if pe >= 1.0:
        return 0.0
    return (po - pe) / (1.0 - pe)


def kappa_to_error_rate(
    target_kappa: float,
    base_rate_primary: float,
    uncertain_prob: float = 0.02,
) -> float:
    """Numerical inversion: find error rate e such that expected κ = target.

    Uses bisection on the analytical kappa-from-error mapping, which is
    monotonically decreasing in e on [0, 0.5].

    Parameters
    ----------
    target_kappa : float in [0, 1]
    base_rate_primary : float in (0, 1)
    uncertain_prob : float in [0, 1), default 0.05
        Marginal Uncertain rate held constant across scenarios.

    Returns
    -------
    float : per-rater error rate in [0, 0.5]
    """
    if not 0.0 <= target_kappa <= 1.0:
        target_kappa = max(0.0, min(1.0, target_kappa))
    if not 0.0 < base_rate_primary < 1.0:
        raise ValueError("base_rate_primary must be in (0, 1)")
    if not 0.0 <= uncertain_prob < 1.0:
        raise ValueError("uncertain_prob must be in [0, 1)")

    # κ at e = 0.5 is 0; κ at e = 0 is at its maximum (less than 1 due to u > 0).
    lo, hi = 0.0, 0.5
    k_at_lo = _expected_kappa_from_error(lo, base_rate_primary, uncertain_prob)
    if target_kappa >= k_at_lo:
        # Target exceeds the achievable maximum (caused by u > 0). Return e = 0.
        return 0.0

    # Bisection
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        k_mid = _expected_kappa_from_error(
            mid, base_rate_primary, uncertain_prob
        )
        if k_mid > target_kappa:
            lo = mid
        else:
            hi = mid
    return float(0.5 * (lo + hi))


def simulate_raters(
    latent_true: np.ndarray,
    target_kappa: float,
    base_rate_primary: float,
    uncertain_prob: float = 0.02,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate two simulated rater output arrays.

    Each rater independently:
        1. With probability uncertain_prob, returns "Uncertain".
        2. Otherwise, with probability (1 - error_rate), returns the
           latent true tier; with probability error_rate, returns the
           opposite tier.

    The Uncertain rate is held constant across κ scenarios so that κ
    variation is driven purely by classification-error variation.

    Parameters
    ----------
    latent_true : np.ndarray of object (entries "Primary" or "Secondary")
    target_kappa : float
        Target Cohen's κ on the binary-collapsed classifications.
    base_rate_primary : float
        Used for validation; the rater error model is symmetric and does
        not depend on the base rate beyond validation.
    uncertain_prob : float, default 0.05
        Marginal probability a rater returns "Uncertain". Held constant
        across scenarios.
    rng : np.random.Generator, optional

    Returns
    -------
    rater_a, rater_b : np.ndarray of object, same shape as latent_true
    """
    if rng is None:
        rng = np.random.default_rng()
    n = latent_true.size
    error_rate = kappa_to_error_rate(
        target_kappa, base_rate_primary, uncertain_prob=uncertain_prob
    )

    def _one_rater() -> np.ndarray:
        out = np.empty(n, dtype=object)
        u_draws = rng.random(n)
        e_draws = rng.random(n)
        for i in range(n):
            if u_draws[i] < uncertain_prob:
                out[i] = UNCERTAIN
            else:
                truth = latent_true[i]
                if e_draws[i] < error_rate:
                    out[i] = SECONDARY if truth == PRIMARY else PRIMARY
                else:
                    out[i] = truth
        return out

    return _one_rater(), _one_rater()


def verify_kappa(rater_a: np.ndarray, rater_b: np.ndarray) -> float:
    """Compute empirical Cohen's κ from rater output arrays.

    Applies the default-to-Primary binary collapse before computing κ.
    """
    a_bin = np.array([_binary_collapse(x) for x in rater_a], dtype=int)
    b_bin = np.array([_binary_collapse(x) for x in rater_b], dtype=int)
    return cohen_kappa_binary(a_bin, b_bin)
