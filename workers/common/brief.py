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


from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml

LANE_VALUES = {1, 2, 3, 4, 5}
STATUS_VALUES = {"candidate", "scored", "rejected", "approved", "graduated"}


@dataclass
class Brief:
    id: str
    title: str
    lane: int
    status: str
    created: str
    source_signals: list
    description: str
    proposed_capture: dict
    estimated_resources: dict
    disqualifiers_checked: dict
    monetization_hypotheses: list
    last_scored: str | None = None
    last_reviewed: str | None = None
    secondary_lanes: list = field(default_factory=list)
    feasibility_scores: dict | None = None
    composite_score: float | None = None
    graduated_to: str | None = None
    body: str = ""


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


_BRIEF_FIELDS = {f.name for f in __import__("dataclasses").fields(Brief)} if False else None


def parse_brief(path: "Path | str") -> Brief:
    """Parse a brief markdown file with YAML frontmatter into a Brief dataclass."""
    from dataclasses import fields as _fields
    text = Path(path).read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"no YAML frontmatter found in {path}")
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    fm["body"] = body
    allowed = {f.name for f in _fields(Brief)}
    filtered = {k: v for k, v in fm.items() if k in allowed}
    return Brief(**filtered)


def write_brief(b: Brief, path: "Path | str") -> None:
    """Serialize a Brief back to disk as YAML frontmatter + body."""
    if b.lane not in LANE_VALUES:
        raise ValueError(f"lane must be one of {sorted(LANE_VALUES)}, got {b.lane}")
    if b.status not in STATUS_VALUES:
        raise ValueError(f"status must be one of {sorted(STATUS_VALUES)}, got {b.status}")
    data = asdict(b)
    body = data.pop("body", "") or ""
    fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    Path(path).write_text(f"---\n{fm}---\n{body}", encoding="utf-8")


def failed_axis(b: Brief) -> str | None:
    """
    Return the name of the failed axis ('financial' | 'implementation' | 'hardware')
    if any axis composite is 0, else None. Returns None for unscored briefs.
    """
    fs = b.feasibility_scores
    if not fs:
        return None
    for axis in ("financial", "implementation", "hardware"):
        sub = fs.get(axis) or {}
        composite = sub.get("composite", None)
        if composite == 0 or composite == 0.0:
            return axis
    return None


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
