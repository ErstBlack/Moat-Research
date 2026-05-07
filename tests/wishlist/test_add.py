from pathlib import Path

import pytest

from mr.wishlist.add import add_source
from mr.wishlist.schema import WishlistError, load_wishlist


def test_add_to_empty(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    yaml_fragment = """id: faa-notams
url: https://notams.aim.faa.gov/
lane: ephemeral_public
rationale: NOTAMs expire.
last_verified: 2026-05-07
dead_link: false
"""
    add_source(p, yaml_fragment)
    w = load_wishlist(p)
    assert len(w.sources) == 1
    assert w.sources[0].id == "faa-notams"


def test_add_duplicate_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: foo
    url: https://a.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="duplicate"):
        add_source(p, """id: foo
url: https://b.com/
lane: niche_vertical
rationale: y
last_verified: 2026-05-07
dead_link: false
""")


def test_add_invalid_kebab_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    with pytest.raises(WishlistError, match="kebab"):
        add_source(p, """id: BadID
url: https://a.com/
lane: niche_vertical
rationale: x
last_verified: 2026-05-07
dead_link: false
""")
