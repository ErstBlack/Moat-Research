"""Tests for mr.synth.session.run."""
import asyncio
from types import SimpleNamespace

import pytest

from mr.synth import session
from mr.synth.limits import LimitExceeded


def _assistant_msg(*texts: str) -> SimpleNamespace:
    """Stand-in for AssistantMessage with TextBlock content."""
    blocks = [SimpleNamespace(text=t) for t in texts]
    msg = SimpleNamespace(content=blocks)
    return msg


@pytest.mark.anyio
async def test_session_run_returns_concatenated_text(mock_query):
    msgs = [_assistant_msg("Part 1. "), _assistant_msg("Part 2.")]
    with mock_query(msgs):
        out = await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            wallclock_seconds=60,
        )
    assert "Part 1." in out
    assert "Part 2." in out


@pytest.mark.anyio
async def test_session_run_wallclock_timeout(monkeypatch):
    async def _slow(*_a, **_kw):
        await asyncio.sleep(5)
        if False:
            yield

    monkeypatch.setattr("mr.synth.session.query", _slow)
    with pytest.raises(LimitExceeded, match="wallclock cap exceeded"):
        await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            wallclock_seconds=1,
        )


@pytest.mark.anyio
async def test_session_run_propagates_sdk_errors(monkeypatch):
    async def _boom(*_a, **_kw):
        raise RuntimeError("sdk down")
        yield

    monkeypatch.setattr("mr.synth.session.query", _boom)
    with pytest.raises(RuntimeError, match="sdk down"):
        await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            wallclock_seconds=60,
        )
