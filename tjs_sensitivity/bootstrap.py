"""Resolve repository root and convenience paths for the TJS sensitivity notebooks and scripts.

Mirrors the pattern of P4's ``p4_replay.bootstrap`` (P4 is the reference
structural pattern per the cursor-rules ``prior-portfolio/reproducibility.mdc``).

Usage from a notebook (canonical pattern for the sensitivity notebooks 05-08)::

    from tjs_sensitivity.bootstrap import prepare_notebook
    REPO_ROOT = prepare_notebook()

After this, ``tjs_sensitivity.simulation``, ``tjs_sensitivity.figures``, etc.
import correctly regardless of the notebook's working directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HARNESS = Path("config") / "harness_settings.json"

# Repo-relative directory layout for the sensitivity work
SENSITIVITY_INPUTS_DIR = Path("inputs") / "sensitivity"
SENSITIVITY_OUTPUTS_DIR = Path("outputs") / "sensitivity"
SENSITIVITY_FIGURES_DIR = SENSITIVITY_OUTPUTS_DIR / "figures"
SENSITIVITY_TABLES_DIR = SENSITIVITY_OUTPUTS_DIR / "tables"
SENSITIVITY_MC_LOGS_DIR = SENSITIVITY_OUTPUTS_DIR / "monte_carlo_logs"


def get_repo_root(start: Path | None = None) -> Path:
    """Walk upward from *start* (default: cwd) until ``config/harness_settings.json`` exists.

    Returns the repository root path. Falls back to *start* if no anchor is found
    (allows the function to be importable in test contexts where the harness
    settings may be absent).
    """
    base = (start or Path.cwd()).resolve()
    for candidate in (base, *base.parents):
        if (candidate / _HARNESS).is_file():
            return candidate
    return base


def prepare_notebook() -> Path:
    """Ensure the repo root is on ``sys.path`` so ``tjs_sensitivity`` imports work.

    Returns the repo root path. Notebooks call this once at the top.

    Note: differs from P4's ``p4_replay.prepare_notebook(*, engine_on_path: bool = False)``
    by omitting the parameter — P3's sensitivity code lives in ``tjs_sensitivity/``
    itself and there is no separate ``engine/`` directory to gate.
    """
    root = get_repo_root()
    r = str(root)
    if r not in sys.path:
        sys.path.insert(0, r)
    return root


def load_seed(repo_root: Path | None = None) -> int:
    """Read the master seed from ``inputs/sensitivity/seed.txt``.

    The simulation is fully deterministic given this seed. Returns the integer
    seed value. Raises FileNotFoundError if the seed file is absent.
    """
    root = repo_root or get_repo_root()
    seed_path = root / SENSITIVITY_INPUTS_DIR / "seed.txt"
    return int(seed_path.read_text(encoding="utf-8").strip())
