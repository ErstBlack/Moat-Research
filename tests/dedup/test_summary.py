from mr.dedup.seen import SeenEntry
from mr.dedup.summary import build_summary_block


def _entry(slug: str, lane: str = "ephemeral_public", niche_key: str = "alerts_aviation",
           hosts: tuple[str, ...] = ("a.com",), disposition: str = "candidate",
           date_created: str = "2026-05-07") -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche=niche_key.replace("_", " "),
        niche_key=niche_key, thesis=f"{slug} thesis.",
        source_set=list(hosts), disposition=disposition,
        auto_reject_reason=None, date_created=date_created,
    )


def test_empty_corpus_yields_minimal_block():
    block = build_summary_block([])
    assert "Lane × niche frequency" in block
    assert "no briefs yet" in block.lower() or "none" in block.lower()


def test_small_corpus_uses_full_index():
    entries = [_entry(f"brief-{i:02d}") for i in range(5)]
    block = build_summary_block(entries)
    for i in range(5):
        assert f"brief-{i:02d}" in block


def test_large_corpus_uses_bounded_summary():
    entries = [_entry(f"brief-{i:03d}") for i in range(60)]
    block = build_summary_block(entries)
    # Bounded summary path: only 30 most-recent appear in the recent-briefs section
    assert "30 most-recent" in block.lower() or "most recent" in block.lower()


def test_lane_niche_freq_excludes_other_lane():
    entries = [
        _entry("a", lane="ephemeral_public", niche_key="alerts_aviation"),
        _entry("b", lane="other", niche_key="weird_thing"),
        _entry("c", lane="ephemeral_public", niche_key="alerts_aviation"),
    ]
    block = build_summary_block(entries)
    # Frequency table should count alerts_aviation = 2, NOT include weird_thing
    assert "alerts_aviation" in block
    assert "weird_thing" not in block.split("Lane × niche frequency")[1].split("\n##")[0]


def test_other_lane_rows_tagged_in_recent_list():
    entries = [_entry("a", lane="other", niche_key="weird")]
    block = build_summary_block(entries)
    assert "(exploration)" in block


def test_most_mined_hosts_split_solo_vs_fusion():
    entries = [
        _entry("a", hosts=("a.com",)),
        _entry("b", hosts=("a.com",)),
        _entry("c", hosts=("a.com", "b.com")),  # fusion
    ]
    block = build_summary_block(entries)
    # a.com: 2 solo + 1 fusion appearance (3 total)
    assert "a.com" in block
    # solo/fusion split should be visible
    assert "solo" in block.lower()
    assert "fusion" in block.lower()


def test_other_lane_only_hosts_tagged_exploration():
    entries = [
        _entry("a", lane="other", hosts=("explore.com",)),
        _entry("b", lane="other", hosts=("explore.com",)),
    ]
    block = build_summary_block(entries)
    assert "(exploration host)" in block
