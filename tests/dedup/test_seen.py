import os
import time
from datetime import date
from pathlib import Path

import pytest

from mr.dedup.seen import (
    LifecycleViolation,
    is_stale,
    read_seen,
    regenerate_seen,
)
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout


def _make_brief(layout: RepoLayout, dirname: str, slug: str, niche: str = "aviation alerts") -> Path:
    target = layout.root / dirname
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"20260507-{slug}.md"
    brief = Brief(
        schema_version=1,
        title=slug,
        slug=slug,
        lane="ephemeral_public",
        niche=niche,
        niche_key="alerts_aviation",
        delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": f"https://{slug}.example.com/", "role": "primary", "archive_status": "none"}],
    )
    body = f"# {slug}\n\n## Thesis\n{slug} thesis sentence.\n"
    write_brief(path, brief, body=body)
    return path


def test_regenerate_empty_repo(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    regenerate_seen(layout, niche_aliases={})
    entries = read_seen(layout.seen_path)
    assert entries == []


def test_regenerate_with_one_brief(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    entries = read_seen(layout.seen_path)
    assert len(entries) == 1
    assert entries[0].slug == "foo"
    assert entries[0].disposition == "candidate"
    assert entries[0].source_set == ["foo.example.com"]
    assert entries[0].auto_reject_reason is None


def test_regenerate_recomputes_niche_key_from_aliases(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo", niche="aviation alerts")
    aliases = {"new_canonical_key": ["aviation alerts"]}
    regenerate_seen(layout, niche_aliases=aliases)
    entries = read_seen(layout.seen_path)
    assert entries[0].niche_key == "new_canonical_key"


def test_partial_move_recovery(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout, "candidates", "foo")
    # Simulate partial move: copy to scored/ with newer mtime
    dst = layout.scored / "07221-20260507-foo.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text())
    # Make dst newer than src
    now = time.time()
    os.utime(src, (now - 30, now - 30))
    os.utime(dst, (now, now))

    regenerate_seen(layout, niche_aliases={})
    # Recovery: dst (forward) kept, src (earlier) deleted
    assert dst.exists()
    assert not src.exists()


def test_operator_error_fallback_cp_in_candidates(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout, "candidates", "foo")
    # Simulate cp from scored/: candidates/ copy is newer
    dst = layout.scored / "07221-20260507-foo.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text())
    now = time.time()
    os.utime(dst, (now - 30, now - 30))
    os.utime(src, (now, now))

    regenerate_seen(layout, niche_aliases={})
    # Both copies left alone for operator's mr score to consume.
    assert src.exists()
    assert dst.exists()
    # seen.jsonl records candidates/ as canonical disposition
    entries = read_seen(layout.seen_path)
    assert len(entries) == 1
    assert entries[0].disposition == "candidate"


def test_unrelated_branches_fatal(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    a = _make_brief(layout, "rejected", "foo")
    b = layout.approved / "08412-20260507-foo.md"
    b.parent.mkdir(parents=True, exist_ok=True)
    b.write_text(a.read_text())

    with pytest.raises(LifecycleViolation, match="rejected.*approved|approved.*rejected"):
        regenerate_seen(layout, niche_aliases={})


def test_atomic_write_via_tmp(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    # No leftover .tmp files
    assert not any(p.name.endswith(".tmp") for p in layout.state_dir.iterdir())


def test_is_stale_when_seen_missing(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    assert is_stale(layout) is True


def test_is_stale_when_dir_mtime_newer(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    layout.seen_path.write_text("")
    old = time.time() - 100
    os.utime(layout.seen_path, (old, old))
    # Touch a lifecycle dir to update mtime
    _make_brief(layout, "candidates", "foo")
    assert is_stale(layout) is True


def test_is_stale_false_when_seen_newer(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    assert is_stale(layout) is False
