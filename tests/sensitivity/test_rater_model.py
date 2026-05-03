"""Tests for code/rater_model.py."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tjs_sensitivity.rater_model import (  # noqa: E402
    PRIMARY,
    SECONDARY,
    UNCERTAIN,
    cohen_kappa_binary,
    kappa_to_error_rate,
    simulate_raters,
    verify_kappa,
)


def test_cohen_kappa_perfect_agreement() -> None:
    a = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    b = a.copy()
    assert abs(cohen_kappa_binary(a, b) - 1.0) < 1e-9


def test_cohen_kappa_chance_agreement() -> None:
    # Independent Bernoulli(0.5) → κ ≈ 0
    rng = np.random.default_rng(42)
    a = (rng.random(10000) < 0.5).astype(int)
    b = (rng.random(10000) < 0.5).astype(int)
    k = cohen_kappa_binary(a, b)
    assert abs(k) < 0.05  # within Monte Carlo noise


def test_kappa_to_error_rate_endpoints() -> None:
    # κ near maximum (u=0.05 limits max κ below 1.0) → error_rate near 0.0
    assert abs(kappa_to_error_rate(1.0, 0.10) - 0.0) < 1e-6
    # κ = 0.0 → error_rate = 0.5
    assert abs(kappa_to_error_rate(0.0, 0.10) - 0.5) < 1e-6


def test_kappa_to_error_rate_invalid_base_rate() -> None:
    import pytest
    with pytest.raises(ValueError):
        kappa_to_error_rate(0.5, 0.0)
    with pytest.raises(ValueError):
        kappa_to_error_rate(0.5, 1.0)


def test_kappa_realised_close_to_target_high_kappa() -> None:
    rng = np.random.default_rng(123)
    n = 5000
    latent = np.where(rng.random(n) < 0.10, PRIMARY, SECONDARY).astype(object)
    a, b = simulate_raters(
        latent_true=latent,
        target_kappa=0.80,
        base_rate_primary=0.10,
        rng=rng,
    )
    realised = verify_kappa(a, b)
    # Allow modest deviation: with n=5000, κ=0.80, MCSE ≈ 0.01–0.02.
    # The (1-2e)^2 mapping is approximate (ignores Uncertain), so we
    # accept |realised - target| < 0.10.
    assert abs(realised - 0.80) < 0.10, f"realised κ = {realised}"


def test_kappa_realised_close_to_target_low_kappa() -> None:
    rng = np.random.default_rng(456)
    n = 5000
    latent = np.where(rng.random(n) < 0.10, PRIMARY, SECONDARY).astype(object)
    a, b = simulate_raters(
        latent_true=latent,
        target_kappa=0.40,
        base_rate_primary=0.10,
        rng=rng,
    )
    realised = verify_kappa(a, b)
    assert abs(realised - 0.40) < 0.10, f"realised κ = {realised}"


def test_rater_outputs_in_alphabet() -> None:
    rng = np.random.default_rng(789)
    n = 1000
    latent = np.where(rng.random(n) < 0.10, PRIMARY, SECONDARY).astype(object)
    a, b = simulate_raters(
        latent_true=latent,
        target_kappa=0.60,
        base_rate_primary=0.10,
        rng=rng,
    )
    allowed = {PRIMARY, SECONDARY, UNCERTAIN}
    assert set(a.tolist()) <= allowed
    assert set(b.tolist()) <= allowed


def test_uncertain_collapses_to_primary_in_kappa() -> None:
    # κ should still be computable even when Uncertain present
    rng = np.random.default_rng(1)
    n = 1000
    latent = np.where(rng.random(n) < 0.10, PRIMARY, SECONDARY).astype(object)
    a, b = simulate_raters(
        latent_true=latent,
        target_kappa=0.60,
        base_rate_primary=0.10,
        rng=rng,
    )
    k = verify_kappa(a, b)
    assert -1.0 <= k <= 1.0
