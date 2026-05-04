"""
Single source of truth for the brief schema, score formula, and filename convention.

Every worker imports from this module. If the schema changes, only this file and its
tests change. See docs/superpowers/specs/2026-05-04-moat-research-design.md §5, §7.
"""
from __future__ import annotations

import re


def composite_score(financial: float, implementation: float, hardware: float) -> float:
    """
    Composite feasibility score per spec §5.4.

    Formula: financial^0.4 * implementation^0.3 * hardware^0.3.
    Any axis = 0 short-circuits to 0 (auto-reject).

    Inputs must be in [0, 10]; raises ValueError otherwise.
    """
    for name, value in (
        ("financial", financial),
        ("implementation", implementation),
        ("hardware", hardware),
    ):
        if value < 0 or value > 10:
            raise ValueError(f"{name} must be in [0, 10], got {value}")
    if financial == 0 or implementation == 0 or hardware == 0:
        return 0.0
    return (financial ** 0.4) * (implementation ** 0.3) * (hardware ** 0.3)


_SCORED_RE = re.compile(r"^(\d{2}\.\d{3})-")
_UNSCORED_PREFIX = "--.---"


def format_score_prefix(score: float) -> str:
    """Format a score in [0, 10] as a 6-char zero-padded string (e.g. 8.031 -> '08.031')."""
    if score < 0 or score > 10:
        raise ValueError(f"score must be in [0, 10], got {score}")
    return f"{score:06.3f}"


def filename_for(
    score: float | None,
    date: str,
    slug: str,
    *,
    failed_axis: str | None = None,
) -> str:
    """
    Build a brief filename per spec §7.1.

    - score is None -> unscored candidate prefix '--.---'.
    - failed_axis set -> rejected file; score must be 0.0.
    - otherwise -> scored file with score prefix.
    """
    if failed_axis is not None:
        if score != 0.0:
            raise ValueError("failed_axis requires score == 0.0")
        return f"00.000-{failed_axis}-{date}-{slug}.md"
    if score is None:
        return f"{_UNSCORED_PREFIX}-{date}-{slug}.md"
    return f"{format_score_prefix(score)}-{date}-{slug}.md"


def parse_score_prefix(filename: str) -> float | None:
    """
    Extract the leading score from a brief filename.

    Returns None for unscored candidates ('--.---' prefix).
    Returns 0.0 for rejected files (also leading '00.000-').
    Raises ValueError on anything else.
    """
    if filename.startswith(_UNSCORED_PREFIX):
        return None
    m = _SCORED_RE.match(filename)
    if not m:
        raise ValueError(f"no score prefix in filename: {filename}")
    return float(m.group(1))
