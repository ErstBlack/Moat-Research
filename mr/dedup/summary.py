"""Bounded pre-pended summary block for mr discover and mr wishlist expand.

Spec §12.2: lane×niche freq + 30 most-recent + top-20 mined hosts (solo/fusion split).
§8.4.1 other-lane treatment: exempt from frequency table; tagged in recent + hosts blocks.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from mr.dedup.seen import SeenEntry

_COLD_CORPUS_THRESHOLD = 50
_RECENT_LIMIT = 30
_TOP_HOSTS = 20


def build_summary_block(entries: Sequence[SeenEntry]) -> str:
    """Render the §12.2 bounded summary block as markdown."""
    if not entries:
        return _empty_block()

    if len(entries) <= _COLD_CORPUS_THRESHOLD:
        return _full_index_block(entries)

    return _bounded_summary_block(entries)


def _empty_block() -> str:
    return (
        "## Lane × niche frequency\n"
        "(no briefs yet — corpus is empty)\n\n"
        "## 30 most-recent briefs\n"
        "(none)\n\n"
        "## Most-mined hosts\n"
        "(none)\n"
    )


def _full_index_block(entries: Sequence[SeenEntry]) -> str:
    return _bounded_summary_block(entries)


def _bounded_summary_block(entries: Sequence[SeenEntry]) -> str:
    parts: list[str] = []
    parts.append(_freq_table(entries))
    parts.append(_recent_briefs(entries))
    parts.append(_mined_hosts(entries))
    return "\n\n".join(parts)


def _freq_table(entries: Sequence[SeenEntry]) -> str:
    """Lane × niche frequency excluding lane=other (§8.4.1 exemption)."""
    pairs = Counter(
        (e.lane, e.niche_key) for e in entries if e.lane != "other"
    )
    lines = ["## Lane × niche frequency (excl. lane: other — exploration channel)"]
    if not pairs:
        lines.append("(no canonical-lane briefs yet)")
    else:
        lines.append("| lane | niche_key | count |")
        lines.append("|---|---|---|")
        for (lane, niche_key), count in pairs.most_common():
            lines.append(f"| {lane} | {niche_key} | {count} |")
    return "\n".join(lines)


def _recent_briefs(entries: Sequence[SeenEntry]) -> str:
    """30 most-recent briefs, with `(exploration)` tag for lane=other."""
    sorted_recent = sorted(entries, key=lambda e: e.date_created, reverse=True)[:_RECENT_LIMIT]
    lines = ["## 30 most-recent briefs"]
    if not sorted_recent:
        lines.append("(none)")
        return "\n".join(lines)

    lines.append("| slug | lane | niche_key | thesis | source_set |")
    lines.append("|---|---|---|---|---|")
    for e in sorted_recent:
        lane_display = f"{e.lane} (exploration)" if e.lane == "other" else e.lane
        hosts = ", ".join(e.source_set) if e.source_set else "—"
        thesis = (e.thesis or "—").replace("|", "\\|").strip()
        lines.append(f"| {e.slug} | {lane_display} | {e.niche_key} | {thesis} | {hosts} |")
    return "\n".join(lines)


def _mined_hosts(entries: Sequence[SeenEntry]) -> str:
    """Top-20 hosts by appearance count, split solo vs. fusion."""
    solo: Counter[str] = Counter()
    fusion: Counter[str] = Counter()
    other_only: set[str] = set()
    canonical_seen: set[str] = set()

    for e in entries:
        is_fusion = len(e.source_set) > 1
        for host in e.source_set:
            if is_fusion:
                fusion[host] += 1
            else:
                solo[host] += 1
            if e.lane == "other":
                other_only.add(host)
            else:
                canonical_seen.add(host)

    totals: Counter[str] = Counter()
    for host, c in solo.items():
        totals[host] += c
    for host, c in fusion.items():
        totals[host] += c

    lines = ["## Most-mined hosts (top 20, solo vs. fusion split)"]
    top = totals.most_common(_TOP_HOSTS)
    if not top:
        lines.append("(none)")
        return "\n".join(lines)

    lines.append("| host | total | solo | fusion |")
    lines.append("|---|---|---|---|")
    for host, total in top:
        tag = " (exploration host)" if host in other_only and host not in canonical_seen else ""
        lines.append(f"| {host}{tag} | {total} | {solo.get(host, 0)} | {fusion.get(host, 0)} |")
    return "\n".join(lines)
