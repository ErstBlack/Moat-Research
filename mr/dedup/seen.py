"""seen.jsonl canonical dedup artifact.

Spec §12.1: regenerated when stale (dir mtime > artifact mtime).
Lifecycle-violation recovery: partial-move artifacts auto-heal,
operator-error (cp instead of mv) leaves duplicates alone, unrelated
branches abort fatally.
"""
from __future__ import annotations

import contextlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mr.dedup.niche_key import resolve_niche_key
from mr.lifecycle.filename import parse_filename
from mr.lifecycle.frontmatter import extract_thesis_first_sentence, read_brief, source_set
from mr.lifecycle.paths import LIFECYCLE_DIRS, RepoLayout, disposition_for_dir

# §12.1: forward-direction order of lifecycle dirs (canonical chain)
_FORWARD_ORDER = list(LIFECYCLE_DIRS)
_DIR_INDEX = {name: i for i, name in enumerate(_FORWARD_ORDER)}

# Adjacent pairs along the canonical chain (for partial-move recovery)
_ADJACENT_PAIRS = {
    frozenset({"candidates", "scored"}),
    frozenset({"candidates", "rejected"}),
    frozenset({"scored", "rejected"}),
    frozenset({"scored", "approved"}),
    frozenset({"approved", "graduated"}),
}

_PARTIAL_MOVE_MTIME_DELTA_SECONDS = 60.0


class LifecycleViolation(Exception):  # noqa: N818
    """Raised when same slug appears in unrelated lifecycle branches."""


@dataclass
class SeenEntry:
    slug: str
    lane: str
    niche: str
    niche_key: str
    thesis: str
    source_set: list[str]              # sorted list for stable JSON
    disposition: str
    auto_reject_reason: str | None
    date_created: str                  # ISO yyyy-mm-dd

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "lane": self.lane,
            "niche": self.niche,
            "niche_key": self.niche_key,
            "thesis": self.thesis,
            "source_set": self.source_set,
            "disposition": self.disposition,
            "auto_reject_reason": self.auto_reject_reason,
            "date_created": self.date_created,
        }


def is_stale(layout: RepoLayout) -> bool:
    """True iff seen.jsonl is missing or older than any lifecycle dir mtime."""
    if not layout.seen_path.exists():
        return True
    seen_mtime = layout.seen_path.stat().st_mtime
    for d in layout.lifecycle_dirs():
        if not d.exists():
            continue
        if d.stat().st_mtime > seen_mtime:
            return True
    return False


def regenerate_seen(layout: RepoLayout, niche_aliases: dict[str, list[str]]) -> None:
    """Walk all lifecycle dirs, rebuild seen.jsonl atomically.

    Applies §12.1 recovery rules to handle duplicate slugs:
    - Adjacent dirs + forward-newer → keep forward, delete earlier.
    - Adjacent dirs + earlier-newer (candidates/ newer) → leave alone.
    - Non-adjacent dirs → raise LifecycleViolation.
    """
    by_slug: dict[str, list[tuple[Path, str]]] = {}
    for d in layout.lifecycle_dirs():
        if not d.exists():
            continue
        for f in d.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            try:
                parsed = parse_filename(f.name)
            except ValueError:
                continue
            by_slug.setdefault(parsed.slug, []).append((f, d.name))

    entries: list[SeenEntry] = []

    for slug, copies in by_slug.items():
        if len(copies) == 1:
            path, dirname = copies[0]
            entries.append(_brief_to_entry(path, dirname, niche_aliases))
            continue

        # Duplicate slug — apply §12.1 recovery rules
        chosen = _resolve_duplicate(slug, copies)
        path, dirname = chosen
        entries.append(_brief_to_entry(path, dirname, niche_aliases))

    _atomic_write(layout.seen_path, entries)


def _resolve_duplicate(slug: str, copies: list[tuple[Path, str]]) -> tuple[Path, str]:
    """§12.1 recovery decision. Returns the (path, dirname) to use as canonical.

    Side effect: deletes the earlier copy on partial-move recovery.
    Raises LifecycleViolation for unrelated-branch duplicates.
    """
    if len(copies) > 2:
        dirs = sorted({d for _, d in copies})
        raise LifecycleViolation(
            f"slug {slug!r} appears in {len(copies)} dirs: {dirs}"
        )

    (path_a, dir_a), (path_b, dir_b) = copies
    pair_set = frozenset({dir_a, dir_b})

    if pair_set not in _ADJACENT_PAIRS:
        raise LifecycleViolation(
            f"slug {slug!r} in unrelated branches {dir_a!r} and {dir_b!r} — "
            f"requires manual resolution via mr doctor (deferred to §15.2)"
        )

    # Identify the forward-direction dir
    forward, earlier = (dir_b, dir_a) if _DIR_INDEX[dir_b] > _DIR_INDEX[dir_a] else (dir_a, dir_b)
    forward_path = path_b if forward == dir_b else path_a
    earlier_path = path_a if forward == dir_b else path_b

    fwd_mtime = forward_path.stat().st_mtime
    ear_mtime = earlier_path.stat().st_mtime

    if forward == "candidates":
        # Should be impossible given _ADJACENT_PAIRS construction
        return forward_path, forward

    if fwd_mtime >= ear_mtime and (fwd_mtime - ear_mtime) <= _PARTIAL_MOVE_MTIME_DELTA_SECONDS:
        # Partial-move artifact: keep forward, delete earlier
        earlier_path.unlink()
        return forward_path, forward

    # Operator-error fallback: candidates/ newer → leave alone, record candidates/ as canonical
    if earlier == "candidates" and ear_mtime > fwd_mtime:
        return earlier_path, earlier

    # Anything else with mtime delta > 60s: fatal
    raise LifecycleViolation(
        f"slug {slug!r} duplicate in {dir_a!r} and {dir_b!r} with mtime "
        f"delta {abs(fwd_mtime - ear_mtime):.0f}s — requires manual resolution"
    )


def _brief_to_entry(path: Path, dirname: str, niche_aliases: dict[str, list[str]]) -> SeenEntry:
    brief = read_brief(path)
    return SeenEntry(
        slug=brief.slug,
        lane=brief.lane,
        niche=brief.niche,
        niche_key=resolve_niche_key(brief.niche, niche_aliases),
        thesis=extract_thesis_first_sentence(path),
        source_set=sorted(source_set(brief.sources)),
        disposition=disposition_for_dir(dirname),
        auto_reject_reason=(brief.scores or {}).get("auto_reject_reason") if dirname == "rejected" else None,
        date_created=brief.date_created.isoformat(),
    )


def _atomic_write(path: Path, entries: list[SeenEntry]) -> None:
    """Write seen.jsonl via tmpfile + os.replace for atomicity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".seen.", suffix=".jsonl.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            for e in entries:
                f.write(json.dumps(e.to_json_obj(), separators=(",", ":")) + "\n")
        os.replace(tmp_name, path)
    except Exception:  # noqa: BLE001
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_name)
        raise


def read_seen(path: Path) -> list[SeenEntry]:
    """Read seen.jsonl. Returns empty list if absent."""
    if not path.exists():
        return []
    entries: list[SeenEntry] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        entries.append(SeenEntry(**d))
    return entries
