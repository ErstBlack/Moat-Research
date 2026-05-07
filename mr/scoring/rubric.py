"""4-axis weighted geometric mean composite.

Spec §5: composite = d^0.35 × f^0.30 × i^0.20 × h^0.15.
Per-axis elasticity equals weight (§5.6).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

_MIN_SCORE = 0
_MAX_SCORE = 10


@dataclass
class Scores:
    defensibility: float
    financial: float
    implementation: float
    hardware: float


def default_weights() -> dict[str, float]:
    """Spec §5 default weights."""
    return {
        "defensibility": 0.35,
        "financial": 0.30,
        "implementation": 0.20,
        "hardware": 0.15,
    }


def composite(scores: Scores, weights: dict[str, float] | None = None) -> float:
    """Compute the weighted geometric mean composite score.

    Returns 0.0 if any axis is 0 (consistent with §5.5 auto-reject force-to-0).
    Raises ValueError if scores are outside [0, 10] or weights don't sum to 1.
    """
    w = weights or default_weights()

    if not math.isclose(sum(w.values()), 1.0, abs_tol=1e-6):
        raise ValueError(f"weights must sum to 1.0; got {sum(w.values())}")

    axes = {
        "defensibility": scores.defensibility,
        "financial": scores.financial,
        "implementation": scores.implementation,
        "hardware": scores.hardware,
    }

    for name, val in axes.items():
        if val < _MIN_SCORE or val > _MAX_SCORE:
            raise ValueError(f"{name} score {val} outside [0, 10]")

    if any(v == 0 for v in axes.values()):
        return 0.0

    out = 1.0
    for name, val in axes.items():
        out *= val ** w[name]
    return out
