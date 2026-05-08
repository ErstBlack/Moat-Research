"""Shared fixtures for synth tests."""
from __future__ import annotations

from typing import Any, Callable
from unittest.mock import patch

import pytest


def _make_async_iter(messages: list[Any]):
    async def _iter(*_args, **_kwargs):
        for m in messages:
            yield m
    return _iter


@pytest.fixture
def mock_query() -> Callable:
    """Patch claude_agent_sdk.query to yield a fixed list of messages."""
    def _factory(messages: list[Any]):
        return patch(
            "mr.synth.session.query",
            side_effect=_make_async_iter(messages),
        )
    return _factory
