"""Filename convention for briefs.

Per spec §6.1:
- scored:    <composite_padded>-<yyyymmdd>-<slug>.md
- candidate: <yyyymmdd>-<slug>.md (no score yet)
- collision: append -02, -03, … (zero-padded to 2 digits, max 99)

Known limitation: a slug that ends in `-NN` (where NN is exactly two
digits) is indistinguishable from a slug + collision suffix when
parsed back. parse_filename treats trailing `-NN` as a collision
suffix in that case. Slugs ending in `-NN` are uncommon (slugify
truncates at word boundaries and the corpus has historically been
verbal-named) but operators should avoid topics that naturally
slugify to `something-12` style names if precise round-trip parsing
matters.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_MAX_COLLISION = 99
_SCORED_RE = re.compile(
    r"^(?P<composite>\d{5})-"
    r"(?P<date>\d{8})-"
    r"(?P<slug>[a-z0-9-]+?)"
    r"(?:-(?P<suffix>\d{2}))?"
    r"\.md$"
)
_CANDIDATE_RE = re.compile(
    r"^(?P<date>\d{8})-"
    r"(?P<slug>[a-z0-9-]+?)"
    r"(?:-(?P<suffix>\d{2}))?"
    r"\.md$"
)


def composite_padded(composite: float) -> str:
    """Render a composite score as a 5-digit zero-padded integer (×1000)."""
    return f"{int(round(composite * 1000)):05d}"


def candidate_filename(date_created: date, slug: str) -> str:
    """Filename for a fresh candidate (no score yet)."""
    return f"{date_created:%Y%m%d}-{slug}.md"


def scored_filename(composite: float, date_created: date, slug: str) -> str:
    """Filename for a scored brief (or 00000- for auto-rejected)."""
    return f"{composite_padded(composite)}-{date_created:%Y%m%d}-{slug}.md"


def resolve_collision(target_dir: Path, desired_name: str) -> str:
    """Return a non-colliding filename in target_dir.

    If desired_name is free, returns it as-is. Otherwise appends -02, -03,
    ..., -99 to the base (before .md). Raises ValueError if overflow.
    """
    if not (target_dir / desired_name).exists():
        return desired_name

    base = desired_name.removesuffix(".md")
    # Strip trailing collision suffix if present so we re-suffix cleanly.
    base = re.sub(r"-\d{2}$", "", base)

    for n in range(2, _MAX_COLLISION + 1):
        candidate = f"{base}-{n:02d}.md"
        if not (target_dir / candidate).exists():
            return candidate

    raise ValueError(f"collision overflow: >{_MAX_COLLISION} duplicates of {desired_name}")


@dataclass
class ParsedFilename:
    composite: float | None        # None for candidate-stage filenames
    date: date
    slug: str
    collision_suffix: int | None   # 2-99, or None if no suffix


def parse_filename(name: str) -> ParsedFilename:
    """Parse a brief filename into composite, date, slug, and optional suffix."""
    m = _SCORED_RE.match(name)
    if m:
        return ParsedFilename(
            composite=int(m["composite"]) / 1000.0,
            date=_yyyymmdd(m["date"]),
            slug=m["slug"],
            collision_suffix=int(m["suffix"]) if m["suffix"] else None,
        )
    m = _CANDIDATE_RE.match(name)
    if m:
        return ParsedFilename(
            composite=None,
            date=_yyyymmdd(m["date"]),
            slug=m["slug"],
            collision_suffix=int(m["suffix"]) if m["suffix"] else None,
        )
    raise ValueError(f"unrecognized brief filename: {name!r}")


def _yyyymmdd(s: str) -> date:
    return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
