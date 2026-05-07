from mr.wishlist.expand import format_proposal


def test_format_proposal_renders_yaml_blocks():
    proposals = [
        {"id": "foo-bar", "url": "https://example.com/",
         "lane": "niche_vertical", "rationale": "Foo bar baz."},
        {"id": "another-thing", "url": "https://other.com/",
         "lane": "ephemeral_public", "rationale": "Disappears nightly."},
    ]
    out = format_proposal(proposals)
    assert "id: foo-bar" in out
    assert "id: another-thing" in out
    # YAML-block boundaries between proposals
    assert "---" in out


def test_format_proposal_empty():
    out = format_proposal([])
    assert "no proposals" in out.lower()
