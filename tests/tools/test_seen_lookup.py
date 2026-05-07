import json
from pathlib import Path

from mr.dedup.seen import SeenEntry
from mr.tools.seen_lookup import seen_lookup


def _write_seen(path: Path, entries: list[SeenEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for e in entries:
            f.write(json.dumps(e.to_json_obj()) + "\n")


def _entry(slug: str, hosts: list[str], lane: str = "ephemeral_public",
           niche_key: str = "alerts_aviation") -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche="x", niche_key=niche_key,
        thesis=f"{slug} thesis.", source_set=hosts,
        disposition="candidate", auto_reject_reason=None,
        date_created="2026-05-07",
    )


def test_exact_slug_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen, slug="foo")
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_slug"


def test_exact_source_set_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "b.com"])])
    r = seen_lookup(seen, source_set=["b.com", "a.com"])  # order-independent
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_source_set"


def test_exact_lane_niche_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"], lane="cross_source_fusion", niche_key="abc")])
    r = seen_lookup(seen, lane_niche=("cross_source_fusion", "abc"))
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_lane_niche"


def test_near_match_source_set_subset(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "b.com"])])
    r = seen_lookup(seen, source_set=["a.com"])
    assert len(r.matches) == 0
    assert any(nm["match_reason"] == "source_set_subset" for nm in r.near_matches)


def test_near_match_source_set_superset(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen, source_set=["a.com", "b.com"])
    assert any(nm["match_reason"] == "source_set_superset" for nm in r.near_matches)


def test_near_match_single_host_overlap(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "x.com"])])
    r = seen_lookup(seen, source_set=["a.com", "y.com"])
    assert any(nm["match_reason"] == "single_host_overlap" for nm in r.near_matches)


def test_no_args_returns_empty(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen)
    assert r.matches == []
    assert r.near_matches == []


def test_missing_seen_file_returns_empty(tmp_path: Path):
    r = seen_lookup(tmp_path / "absent.jsonl", slug="foo")
    assert r.matches == []
    assert r.near_matches == []
