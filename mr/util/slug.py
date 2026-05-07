"""Slug normalization for filenames and identifiers.

Per spec §6.1: lowercase-kebab from title, ≤40 chars, ASCII-only.
"""
from __future__ import annotations

import re
import unicodedata

_MAX_LEN = 40
_FALLBACK = "untitled"


def slugify(text: str) -> str:
    """Normalize text into a kebab-case ASCII slug ≤40 chars."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    kebab = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")

    if not kebab:
        return _FALLBACK

    if len(kebab) <= _MAX_LEN:
        return kebab

    truncated = kebab[:_MAX_LEN]
    last_dash = truncated.rfind("-")
    if last_dash > 0:
        truncated = truncated[:last_dash]

    return truncated or _FALLBACK
