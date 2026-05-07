from datetime import date
from pathlib import Path
from unittest.mock import patch

from mr.tools.head import HeadResult
from mr.wishlist.refresh import refresh_wishlist
from mr.wishlist.schema import Wishlist, WishlistSource, load_wishlist, save_wishlist


def _fake_head_ok(_url: str, **_kwargs):
    return HeadResult(status=200, content_type="text/html", last_modified=None, error=None)


def _fake_head_404(_url: str, **_kwargs):
    return HeadResult(status=404, content_type=None, last_modified=None, error=None)


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_ok)
def test_2xx_updates_last_verified(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1), dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].last_verified == date(2026, 5, 7)
    assert w.sources[0].dead_link is False


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_4xx_does_not_update_last_verified(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1), dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].last_verified == date(2025, 1, 1)
    assert w.sources[0].last_attempted == date(2026, 5, 7)
    assert w.sources[0].dead_link is False


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_two_consecutive_failures_within_window_marks_dead(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1),
        last_attempted=date(2026, 5, 1),
        dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].dead_link is True


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_failures_outside_window_reset_counter(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1),
        last_attempted=date(2025, 12, 1),
        dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].dead_link is False
