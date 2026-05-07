from unittest.mock import patch

from mr.tools.robots import RobotsResult, robots_check


def test_allowed_when_no_robots(monkeypatch):
    """Missing robots.txt → assumed allowed per RFC."""
    class FakeParser:
        def set_url(self, _url): pass
        def read(self): pass
        def can_fetch(self, _ua, url): return True
    with patch("mr.tools.robots.RobotFileParser", return_value=FakeParser()):
        r = robots_check("https://example.com/some/path", user_agent="moat-research/0.1")
        assert r.allowed is True


def test_disallowed_path(monkeypatch):
    class FakeParser:
        def set_url(self, _url): pass
        def read(self): pass
        def can_fetch(self, _ua, url): return False
    with patch("mr.tools.robots.RobotFileParser", return_value=FakeParser()):
        r = robots_check("https://example.com/private", user_agent="moat-research/0.1")
        assert r.allowed is False


def test_robots_url_constructed_from_origin():
    r = RobotsResult(allowed=True, robots_url="https://example.com/robots.txt", error=None)
    assert r.robots_url == "https://example.com/robots.txt"


def test_returns_error_on_unreachable(monkeypatch):
    class BrokenParser:
        def set_url(self, _url): pass
        def read(self): raise OSError("network down")
        def can_fetch(self, _ua, url): return False
    with patch("mr.tools.robots.RobotFileParser", return_value=BrokenParser()):
        r = robots_check("https://offline.example/", user_agent="moat-research/0.1")
        assert r.allowed is True  # fail open per RFC convention
        assert r.error is not None
