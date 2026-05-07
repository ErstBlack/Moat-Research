from pathlib import Path
from unittest.mock import patch

from mr.synth.dispatch import dispatch_tool_call


def test_seen_lookup_dispatched(tmp_path: Path):
    seen_path = tmp_path / "seen.jsonl"
    seen_path.write_text("")  # empty
    result = dispatch_tool_call(
        name="seen_lookup",
        args={"slug": "foo"},
        seen_path=seen_path,
    )
    assert "matches" in result
    assert "near_matches" in result


@patch("mr.synth.dispatch.wayback_check")
def test_wayback_dispatched(mock_wayback, tmp_path: Path):
    from datetime import date

    from mr.tools.wayback import WaybackResult
    mock_wayback.return_value = WaybackResult(count=42, first=date(2023, 1, 1), last=date(2026, 4, 30))
    result = dispatch_tool_call(
        name="wayback_check",
        args={"url": "https://example.com/"},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert result["count"] == 42
    assert result["first"] == "2023-01-01"


@patch("mr.synth.dispatch.robots_check")
def test_robots_dispatched(mock_robots, tmp_path: Path):
    from mr.tools.robots import RobotsResult
    mock_robots.return_value = RobotsResult(
        allowed=True, robots_url="https://example.com/robots.txt", error=None
    )
    result = dispatch_tool_call(
        name="robots_check",
        args={"url": "https://example.com/", "user_agent": "test"},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert result["allowed"] is True


def test_unknown_tool_returns_error(tmp_path: Path):
    result = dispatch_tool_call(
        name="bogus_tool",
        args={},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert "error" in result
