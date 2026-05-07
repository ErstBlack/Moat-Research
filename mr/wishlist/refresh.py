"""mr wishlist refresh — deterministic re-verification of WISHLIST sources.

Spec §11: HEAD + robots + Wayback; last_verified only on 2xx;
last_attempted always; dead_link on consecutive failures within window.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from mr.tools.head import head_check
from mr.wishlist.schema import load_wishlist, save_wishlist

_HTTP_OK_MIN = 200
_HTTP_OK_MAX = 300


def refresh_wishlist(
    wishlist_path: Path,
    today: date,
    dead_link_window_days: int,
) -> None:
    """Re-verify every source. Update last_verified/last_attempted/dead_link."""
    w = load_wishlist(wishlist_path)

    for src in w.sources:
        result = head_check(src.url)
        is_ok = result.status is not None and _HTTP_OK_MIN <= result.status < _HTTP_OK_MAX

        prev_attempted = src.last_attempted
        src.last_attempted = today

        if is_ok:
            src.last_verified = today
            src.dead_link = False
            continue

        if prev_attempted and prev_attempted >= today - timedelta(days=dead_link_window_days):
            src.dead_link = True

    save_wishlist(wishlist_path, w)
