"""niche_key normalization with alias resolution.

Spec §6.4: niche_key = lowercase, alphanumerics+underscore, tokens sorted alphabetically.
Spec §12.5: aliases resolve at seen.jsonl regen time using current mr.yaml.
"""
from __future__ import annotations

import re
import unicodedata

_FALLBACK = "untagged"


def normalize_niche(text: str) -> str:
    """Canonicalize a free-text niche tag into a stable key.

    Rules:
    - NFKD normalize + strip non-ASCII
    - lowercase
    - non-alphanumeric → underscore
    - collapse repeated underscores
    - split on underscore, sort tokens alphabetically, rejoin with `_`
    - empty → "untagged"
    """
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")

    if not normalized:
        return _FALLBACK

    tokens = [t for t in normalized.split("_") if t]
    tokens.sort()
    return "_".join(tokens) or _FALLBACK


def resolve_niche_key(niche: str, aliases: dict[str, list[str]]) -> str:
    """Compute the canonical niche_key, applying aliases from mr.yaml.

    `aliases` maps canonical key → list of synonym strings (the synonyms
    are matched after normalization). If the input's normalized form
    matches a synonym, the canonical key is returned; otherwise the
    normalized form itself is returned.
    """
    normalized = normalize_niche(niche)
    for canonical, synonyms in aliases.items():
        for syn in synonyms:
            if normalize_niche(syn) == normalized:
                return canonical
    return normalized
