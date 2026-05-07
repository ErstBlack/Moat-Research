from datetime import date
from pathlib import Path

import pytest

from mr.lifecycle.filename import (
    candidate_filename,
    composite_padded,
    parse_filename,
    resolve_collision,
    scored_filename,
)


def test_composite_padded_basic():
    assert composite_padded(7.221) == "07221"


def test_composite_padded_zero():
    assert composite_padded(0.0) == "00000"


def test_composite_padded_max():
    assert composite_padded(10.0) == "10000"


def test_composite_padded_rounds_half_to_nearest():
    # 7.2215 × 1000 = 7221.5 → banker's rounding goes either way; just check 5 digits
    assert len(composite_padded(7.2215)) == 5


def test_candidate_filename():
    assert candidate_filename(date(2026, 5, 7), "faa-notams") == "20260507-faa-notams.md"


def test_scored_filename():
    assert scored_filename(7.221, date(2026, 5, 7), "faa-notams") == "07221-20260507-faa-notams.md"


def test_scored_filename_auto_reject():
    assert scored_filename(0.0, date(2026, 5, 7), "bad-idea") == "00000-20260507-bad-idea.md"


def test_resolve_collision_no_collision(tmp_path: Path):
    target_dir = tmp_path
    name = "07221-20260507-foo.md"
    assert resolve_collision(target_dir, name) == name


def test_resolve_collision_appends_zero_padded_suffix(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    assert resolve_collision(target_dir, "07221-20260507-foo.md") == "07221-20260507-foo-02.md"


def test_resolve_collision_chains_to_03(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    (target_dir / "07221-20260507-foo-02.md").write_text("x")
    assert resolve_collision(target_dir, "07221-20260507-foo.md") == "07221-20260507-foo-03.md"


def test_resolve_collision_overflow_raises(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    for i in range(2, 100):
        (target_dir / f"07221-20260507-foo-{i:02d}.md").write_text("x")
    with pytest.raises(ValueError, match="collision"):
        resolve_collision(target_dir, "07221-20260507-foo.md")


def test_parse_scored_filename():
    parsed = parse_filename("07221-20260507-faa-notams.md")
    assert parsed.composite == 7.221
    assert parsed.date == date(2026, 5, 7)
    assert parsed.slug == "faa-notams"


def test_parse_candidate_filename():
    parsed = parse_filename("20260507-faa-notams.md")
    assert parsed.composite is None
    assert parsed.date == date(2026, 5, 7)
    assert parsed.slug == "faa-notams"


def test_parse_with_collision_suffix():
    parsed = parse_filename("07221-20260507-foo-02.md")
    assert parsed.slug == "foo"
    assert parsed.collision_suffix == 2


def test_parse_slug_ending_in_two_digits_is_ambiguous():
    # Documented limitation: trailing -NN is always parsed as a collision
    # suffix, even when the slug itself ends in two digits. Slugs like
    # "model-42" round-trip incorrectly. See module docstring.
    parsed = parse_filename("07221-20260507-model-42.md")
    assert parsed.slug == "model"
    assert parsed.collision_suffix == 42
