"""TJS κ-sensitivity simulation package.

This is the paper-specific module for Paper 3's sensitivity-analysis work,
authored at WS-2.6 (the sensitivity-zip integration). It mirrors P4's
``p4_replay/`` pattern: a top-level paper-specific module that hosts
simulation source code (``simulation.py``, ``rater_model.py``, ``outcomes.py``,
``monte_carlo.py``, ``figures.py``) plus a ``bootstrap`` helper that the
sensitivity notebooks (05-08) call to resolve the repo root.

Public surface:

- ``get_repo_root`` / ``prepare_notebook`` / ``load_seed`` from ``bootstrap``

Per Walter Decision A (Phase 0/Phase 3.3 ack), this module sits at top-level
``tjs_sensitivity/`` rather than ``code/`` (the zip's name) or ``src/``
(the agent prompt's canonical name); the choice mirrors P4's per-paper
module pattern.

The simulation source modules import each other with relative imports
(``from .monte_carlo import …``, ``from .outcomes import …`` etc.); namespace
references that originally said ``code.X`` were patched to ``tjs_sensitivity.X``
during WS-2.6 Phase 4 ADD application (see phase4_substitution_log.txt in the
operations worktree scratch for the substitution audit trail).
"""

from tjs_sensitivity.bootstrap import (
    get_repo_root,
    load_seed,
    prepare_notebook,
)

__all__ = [
    "get_repo_root",
    "load_seed",
    "prepare_notebook",
]
