"""WISHLIST.md schema and loader.

Spec §11: top-level YAML with sources: list of {id, url, lane, rationale,
last_verified, last_attempted?, dead_link}.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VALID_LANES = frozenset({
    "ephemeral_public", "soon_to_be_restricted", "cross_source_fusion",
    "derived_artifact", "niche_vertical", "other",
})


class WishlistError(Exception):
    pass


@dataclass
class WishlistSource:
    id: str
    url: str
    lane: str
    rationale: str
    last_verified: date
    dead_link: bool = False
    last_attempted: date | None = None


@dataclass
class Wishlist:
    sources: list[WishlistSource] = field(default_factory=list)


def load_wishlist(path: Path) -> Wishlist:
    if not path.exists():
        return Wishlist()
    raw = yaml.safe_load(path.read_text()) or {}
    sources_raw = raw.get("sources") or []
    if not isinstance(sources_raw, list):
        raise WishlistError("sources: must be a list")

    seen_ids: set[str] = set()
    sources: list[WishlistSource] = []
    for s in sources_raw:
        if not isinstance(s, dict):
            raise WishlistError(f"source must be a mapping: {s!r}")
        for required in ("id", "url", "lane", "rationale", "last_verified"):
            if required not in s:
                raise WishlistError(f"source missing required key {required!r}: {s.get('id')}")
        sid = s["id"]
        if not _KEBAB_RE.match(sid):
            raise WishlistError(f"source id {sid!r} is not lowercase-kebab")
        if sid in seen_ids:
            raise WishlistError(f"duplicate source id: {sid!r}")
        seen_ids.add(sid)
        if s["lane"] not in _VALID_LANES:
            raise WishlistError(f"source {sid!r}: lane {s['lane']!r} not in {sorted(_VALID_LANES)}")

        last_verified = s["last_verified"]
        if isinstance(last_verified, str):
            last_verified = date.fromisoformat(last_verified)

        last_attempted = s.get("last_attempted")
        if isinstance(last_attempted, str):
            last_attempted = date.fromisoformat(last_attempted)

        sources.append(WishlistSource(
            id=sid, url=s["url"], lane=s["lane"], rationale=s["rationale"],
            last_verified=last_verified, dead_link=bool(s.get("dead_link", False)),
            last_attempted=last_attempted,
        ))

    return Wishlist(sources=sources)


def save_wishlist(path: Path, wishlist: Wishlist) -> None:
    """Write wishlist back to disk in canonical format."""
    payload: dict = {"sources": []}
    for s in wishlist.sources:
        entry = {
            "id": s.id,
            "url": s.url,
            "lane": s.lane,
            "rationale": s.rationale,
            "last_verified": s.last_verified.isoformat(),
            "dead_link": s.dead_link,
        }
        if s.last_attempted:
            entry["last_attempted"] = s.last_attempted.isoformat()
        payload["sources"].append(entry)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, default_flow_style=False))
