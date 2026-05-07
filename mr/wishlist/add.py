"""Append a source to WISHLIST.md after validation."""
from __future__ import annotations

from pathlib import Path

import yaml

from mr.wishlist.schema import (
    WishlistError,
    load_wishlist,
    save_wishlist,
)


def add_source(wishlist_path: Path, yaml_fragment: str) -> None:
    """Parse yaml_fragment, validate, and append to WISHLIST.md."""
    parsed = yaml.safe_load(yaml_fragment)
    if not isinstance(parsed, dict):
        raise WishlistError("yaml fragment must be a mapping")

    # Build a synthetic single-source Wishlist to leverage validator
    proposed_yaml = {"sources": [parsed]}
    tmp_text = yaml.safe_dump(proposed_yaml)

    # Validate by writing to a temp Wishlist
    tmp_path = wishlist_path.parent / ".wishlist-add.tmp.yaml"
    tmp_path.write_text(tmp_text)
    try:
        new_wishlist = load_wishlist(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    new_source = new_wishlist.sources[0]

    existing = load_wishlist(wishlist_path)
    if any(s.id == new_source.id for s in existing.sources):
        raise WishlistError(f"duplicate source id: {new_source.id!r}")

    existing.sources.append(new_source)
    save_wishlist(wishlist_path, existing)
