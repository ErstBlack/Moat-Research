"""HTTP HEAD wrapper for liveness checks.

Spec §8.3: httpx HEAD → {status, content_type, last_modified}.
Used by mr wishlist refresh (§11).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx

_DEFAULT_TIMEOUT_S = 10.0


@dataclass
class HeadResult:
    status: int | None
    content_type: str | None
    last_modified: datetime | None
    error: str | None


def head_check(url: str, timeout_s: float = _DEFAULT_TIMEOUT_S) -> HeadResult:
    """HTTP HEAD a URL. Returns status, content-type, last-modified.

    Network errors are reported via `error`; status is None in that case.
    """
    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            resp = client.head(url)
    except httpx.HTTPError as e:
        return HeadResult(status=None, content_type=None, last_modified=None, error=str(e))

    content_type = resp.headers.get("content-type")
    last_mod_raw = resp.headers.get("last-modified")
    last_modified = None
    if last_mod_raw:
        try:
            last_modified = parsedate_to_datetime(last_mod_raw)
        except (TypeError, ValueError):
            last_modified = None

    return HeadResult(
        status=resp.status_code,
        content_type=content_type,
        last_modified=last_modified,
        error=None,
    )
