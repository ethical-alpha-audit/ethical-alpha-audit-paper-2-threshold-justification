"""Tests for code/outcomes.py."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tjs_sensitivity.outcomes import (  # noqa: E402
    PRIMARY,
    SECONDARY,
    UNCERTAIN,
    compute_outcomes,
    BURDEN_DELTA_MIN,
)


def _arr(seq: list[str]) -> np.ndarray:
    return np.array(seq, dtype=object)


def test_perfect_agreement_with_truth() -> None:
    latent = _arr([PRIMARY, PRIMARY, SECONDARY, SECONDARY])
    a = latent.copy()
    b = latent.copy()
    out = compute_outcomes(latent, a, b, realised_kappa=1.0)
    assert out.misclass_primary_to_secondary == 0.0
    assert out.misclass_secondary_to_primary == 0.0
    assert out.unsafe_secondary_rate == 0.0
    assert out.over_escalation_rate == 0.0


def test_default_to_primary_escalates_disagreement() -> None:
    # Latent: all Secondary; rater_a says Secondary, rater_b says Primary
    # → disagreement → adjudicated Primary → over-escalation = 1.0
    latent = _arr([SECONDARY, SECONDARY, SECONDARY, SECONDARY])
    a = _arr([SECONDARY, SECONDARY, SECONDARY, SECONDARY])
    b = _arr([PRIMARY, PRIMARY, PRIMARY, PRIMARY])
    out = compute_outcomes(latent, a, b, realised_kappa=0.0)
    assert out.over_escalation_rate == 1.0
    assert out.unsafe_secondary_rate == 0.0
    assert out.net_primary_rate == 1.0


def test_uncertain_treated_as_primary() -> None:
    latent = _arr([SECONDARY, SECONDARY])
    a = _arr([SECONDARY, SECONDARY])
    b = _arr([UNCERTAIN, UNCERTAIN])
    out = compute_outcomes(latent, a, b, realised_kappa=0.0)
    # Uncertain → escalation
    assert out.over_escalation_rate == 1.0


def test_unsafe_secondary_requires_both_raters_secondary() -> None:
    # Latent Primary; both raters say Secondary → unsafe
    latent = _arr([PRIMARY, PRIMARY])
    a = _arr([SECONDARY, SECONDARY])
    b = _arr([SECONDARY, SECONDARY])
    out = compute_outcomes(latent, a, b, realised_kappa=0.0)
    assert out.unsafe_secondary_rate == 1.0
    assert out.misclass_primary_to_secondary == 1.0


def test_burden_calculation() -> None:
    # 4 thresholds; 2 latent Secondary; both escalated → 2/2 over-escalation
    # Population secondary share = 0.5; over_esc = 1.0
    # extra minutes per 100 = 100 * 0.5 * 1.0 * 50 = 2500 → 41.67 hours
    latent = _arr([PRIMARY, PRIMARY, SECONDARY, SECONDARY])
    a = _arr([PRIMARY, PRIMARY, PRIMARY, PRIMARY])
    b = _arr([PRIMARY, PRIMARY, PRIMARY, PRIMARY])
    out = compute_outcomes(latent, a, b, realised_kappa=1.0)
    expected = 100.0 * 0.5 * 1.0 * BURDEN_DELTA_MIN / 60.0
    assert abs(out.over_escalation_burden_hours_per_100 - expected) < 1e-9


def test_zero_primary_population_does_not_divide_by_zero() -> None:
    latent = _arr([SECONDARY, SECONDARY])
    a = _arr([SECONDARY, SECONDARY])
    b = _arr([SECONDARY, SECONDARY])
    out = compute_outcomes(latent, a, b, realised_kappa=1.0)
    assert out.unsafe_secondary_rate == 0.0
    assert out.misclass_primary_to_secondary == 0.0


def test_zero_secondary_population_does_not_divide_by_zero() -> None:
    latent = _arr([PRIMARY, PRIMARY])
    a = _arr([PRIMARY, PRIMARY])
    b = _arr([PRIMARY, PRIMARY])
    out = compute_outcomes(latent, a, b, realised_kappa=1.0)
    assert out.over_escalation_rate == 0.0
    assert out.misclass_secondary_to_primary == 0.0
