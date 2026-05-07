"""Adjacent-rejection appendix for hand-off prompts.

Spec §13.3: matching (lane, niche_key) tuple, capped at 3, severity-ranked
(tier 1 hard disqualifier > tier 2 floor > tier 3 manual).
"""
from __future__ import annotations

from collections.abc import Sequence

from mr.dedup.seen import SeenEntry
from mr.scoring.auto_reject import severity_tier

_CAP = 3


def build_appendix(
    entries: Sequence[SeenEntry],
    *,
    target_lane: str,
    target_niche_key: str,
) -> str:
    """Render the adjacent-rejection appendix for a graduating brief."""
    matching = [
        e for e in entries
        if e.disposition == "rejected"
        and e.lane == target_lane
        and e.niche_key == target_niche_key
        and e.auto_reject_reason is not None
    ]

    def _rank(e: SeenEntry) -> int:
        tier = severity_tier(e.auto_reject_reason)
        return tier if tier is not None else 99

    matching.sort(key=lambda e: (_rank(e), e.date_created))
    top = matching[:_CAP]

    if not top:
        return "## Adjacent rejections (same lane, same niche)\n\n(none)\n"

    lines = ["## Adjacent rejections (same lane, same niche — known dead-ends)", ""]
    for e in top:
        lines.append(f"- **{e.slug}** — `{e.auto_reject_reason}` — {e.thesis}")
    lines.append("")
    return "\n".join(lines)
