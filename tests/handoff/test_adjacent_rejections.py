from mr.dedup.seen import SeenEntry
from mr.handoff.adjacent_rejections import build_appendix


def _entry(slug: str, lane: str, niche_key: str, reason: str) -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche=niche_key, niche_key=niche_key,
        thesis=f"{slug} thesis.", source_set=["a.com"],
        disposition="rejected", auto_reject_reason=reason,
        date_created="2026-05-07",
    )


def test_appendix_severity_ranks_hard_disqualifier_first():
    entries = [
        _entry("a", "ephemeral_public", "alerts_aviation", "manual: bad fit"),
        _entry("b", "ephemeral_public", "alerts_aviation", "single source"),
        _entry("c", "ephemeral_public", "alerts_aviation", "defensibility ≤ 4"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    assert out.index("single source") < out.index("defensibility ≤ 4")
    assert out.index("defensibility ≤ 4") < out.index("manual: bad fit")


def test_appendix_capped_at_3():
    entries = [
        _entry(f"a{i}", "ephemeral_public", "alerts_aviation", "single source")
        for i in range(5)
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    surfaces = [f"a{i}" for i in range(5) if f"a{i}" in out]
    assert len(surfaces) == 3


def test_appendix_filters_to_matching_lane_niche():
    entries = [
        _entry("a", "ephemeral_public", "alerts_aviation", "single source"),
        _entry("b", "ephemeral_public", "different_niche", "single source"),
        _entry("c", "niche_vertical", "alerts_aviation", "single source"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    assert "a" in out
    assert "b" not in out
    assert "c" not in out


def test_appendix_empty_when_no_matches():
    entries = [
        _entry("a", "ephemeral_public", "different", "single source"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    assert "(none)" in out.lower() or "no adjacent" in out.lower()
