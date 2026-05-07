from pathlib import Path

import pytest

from mr.wishlist.schema import (
    WishlistError,
    load_wishlist,
)


def test_load_empty(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    w = load_wishlist(p)
    assert w.sources == []


def test_load_with_sources(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: faa-notams
    url: https://notams.aim.faa.gov/
    lane: ephemeral_public
    rationale: NOTAMs expire.
    last_verified: 2026-05-07
    dead_link: false
""")
    w = load_wishlist(p)
    assert len(w.sources) == 1
    assert w.sources[0].id == "faa-notams"
    assert w.sources[0].lane == "ephemeral_public"
    assert w.sources[0].dead_link is False


def test_invalid_id_kebab(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: "not_kebab_case_with_underscores"
    url: https://example.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="id"):
        load_wishlist(p)


def test_duplicate_id_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: dup
    url: https://a.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
  - id: dup
    url: https://b.com/
    lane: niche_vertical
    rationale: y
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="duplicate"):
        load_wishlist(p)


def test_invalid_lane(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: foo
    url: https://example.com/
    lane: bogus
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="lane"):
        load_wishlist(p)


def test_missing_file_returns_empty(tmp_path: Path):
    w = load_wishlist(tmp_path / "absent.md")
    assert w.sources == []
