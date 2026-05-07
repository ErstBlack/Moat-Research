"""seen_lookup custom tool: query seen.jsonl for matches and near-matches.

Spec §12.3: returns {matches, near_matches}. Set semantics on source_set.
~100 LOC, no LLM, host-side Python.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mr.dedup.seen import read_seen


@dataclass
class SeenLookupResult:
    matches: list[dict[str, Any]] = field(default_factory=list)
    near_matches: list[dict[str, Any]] = field(default_factory=list)


def seen_lookup(
    seen_path: Path,
    slug: str | None = None,
    source_set: list[str] | None = None,
    lane_niche: tuple[str, str] | None = None,
) -> SeenLookupResult:
    """Look up matches in seen.jsonl. Returns matches + near-matches.

    See spec §12.4 for match-type definitions:
    - matches: exact_slug, exact_source_set, exact_lane_niche
    - near_matches: source_set_subset/superset, single_host_overlap, partial_niche
    """
    out = SeenLookupResult()
    if all(arg is None for arg in (slug, source_set, lane_niche)):
        return out

    entries = read_seen(seen_path)
    query_set = frozenset(source_set) if source_set else None

    for e in entries:
        info = {"file": e.slug, "slug": e.slug, "thesis": e.thesis}

        if slug is not None and e.slug == slug:
            out.matches.append({**info, "match_reason": "exact_slug"})
            continue

        if query_set is not None and query_set == frozenset(e.source_set):
            out.matches.append({**info, "match_reason": "exact_source_set"})
            continue

        if lane_niche is not None and (e.lane, e.niche_key) == lane_niche:
            out.matches.append({**info, "match_reason": "exact_lane_niche"})
            continue

        # Near-match analysis on source_set
        if query_set is not None:
            entry_set = frozenset(e.source_set)
            if query_set < entry_set:
                out.near_matches.append({**info, "match_reason": "source_set_subset"})
                continue
            if query_set > entry_set:
                out.near_matches.append({**info, "match_reason": "source_set_superset"})
                continue
            if query_set & entry_set:
                out.near_matches.append({**info, "match_reason": "single_host_overlap"})
                continue

        # Partial niche match
        if lane_niche is not None and lane_niche[0] == e.lane:
            out.near_matches.append({**info, "match_reason": "partial_niche"})

    return out
