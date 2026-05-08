"""Tests for mr.synth.mcp_server tool factories."""
import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from mr.synth import mcp_server


def _text_payload(result: dict) -> dict:
    """Extract and JSON-decode the text content from a @tool return."""
    assert "content" in result
    assert result["content"][0]["type"] == "text"
    return json.loads(result["content"][0]["text"])


@pytest.mark.anyio
async def test_seen_lookup_returns_matches(tmp_path: Path):
    seen_path = tmp_path / "seen.jsonl"
    seen_path.write_text("")
    fn = mcp_server._make_seen_lookup(seen_path)
    result = await fn({"slug": "foo"})
    payload = _text_payload(result)
    assert "matches" in payload
    assert "near_matches" in payload


@pytest.mark.anyio
@patch("mr.tools.wayback.wayback_check")
async def test_wayback_returns_count(mock_wayback):
    from mr.tools.wayback import WaybackResult
    mock_wayback.return_value = WaybackResult(count=42, first=date(2023, 1, 1), last=date(2026, 4, 30))
    result = await mcp_server._wayback({"url": "https://example.com/"})
    payload = _text_payload(result)
    assert payload["count"] == 42
    assert payload["first"] == "2023-01-01"


@pytest.mark.anyio
@patch("mr.tools.robots.robots_check")
async def test_robots_returns_allowed(mock_robots):
    from mr.tools.robots import RobotsResult
    mock_robots.return_value = RobotsResult(
        allowed=True, robots_url="https://example.com/robots.txt", error=None,
    )
    result = await mcp_server._robots({"url": "https://example.com/", "user_agent": "test"})
    payload = _text_payload(result)
    assert payload["allowed"] is True


@pytest.mark.anyio
@patch("mr.tools.head.head_check")
async def test_head_returns_status(mock_head):
    from mr.tools.head import HeadResult
    mock_head.return_value = HeadResult(
        status=200, content_type="text/html", last_modified=None, error=None,
    )
    result = await mcp_server._head({"url": "https://example.com/"})
    payload = _text_payload(result)
    assert payload["status"] == 200
    assert payload["content_type"] == "text/html"
