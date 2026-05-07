"""Wayback Machine CDX API wrapper.

Spec §8.3: waybackpy → CDX → {first, last, count}.
Used by mr discover, mr score (host-driven verification), mr wishlist refresh.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from waybackpy import WaybackMachineCDXServerAPI


@dataclass
class WaybackResult:
    count: int
    first: date | None
    last: date | None

    @property
    def years(self) -> float:
        if self.first is None or self.last is None:
            return 0.0
        return (self.last - self.first).days / 365.25


def wayback_check(url: str, user_agent: str = "moat-research/0.1") -> WaybackResult:
    """Query Wayback CDX for snapshot count and date range.

    Returns count=0 / first=None / last=None when no snapshots exist.
    """
    cdx = WaybackMachineCDXServerAPI(url=url, user_agent=user_agent)
    snapshots = list(cdx.snapshots())

    if not snapshots:
        return WaybackResult(count=0, first=None, last=None)

    timestamps = [_parse_ts(s.timestamp) for s in snapshots]
    return WaybackResult(
        count=len(snapshots),
        first=min(timestamps),
        last=max(timestamps),
    )


def _parse_ts(ts: str) -> date:
    """CDX timestamps are 'yyyymmddHHMMSS'; we keep only the date."""
    return date(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]))
