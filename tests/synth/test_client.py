"""Tests for mr.synth.client — SynthClient and build_cached_blocks.

Spec §8.1: mandatory prompt caching with separate cache slots.
Spec §10: usage extraction for costs.jsonl recording.
"""
from unittest.mock import MagicMock, patch

from mr.synth.client import SynthClient, build_cached_blocks
from mr.util.config import DEFAULT_CONFIG, Config


def test_build_cached_blocks_separates_system_wishlist_seen():
    blocks = build_cached_blocks(
        system_text="System prompt here.",
        wishlist_text="WISHLIST yaml here.",
        seen_summary="seen summary here.",
    )
    assert len(blocks) == 3
    for block in blocks:
        assert block["type"] == "text"
        assert block["cache_control"] == {"type": "ephemeral"}
    assert "System prompt here" in blocks[0]["text"]
    assert "WISHLIST yaml here" in blocks[1]["text"]
    assert "seen summary here" in blocks[2]["text"]


@patch("mr.synth.client.Anthropic")
def test_synth_client_uses_correct_model(mock_anthropic_cls, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    assert client.model == "claude-opus-4-7"


@patch("mr.synth.client.Anthropic")
def test_synth_client_per_command_override(mock_anthropic_cls, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="wishlist_expand")
    assert client.model == "claude-sonnet-4-6"


@patch("mr.synth.client.Anthropic")
def test_create_message_passes_through(mock_anthropic_cls, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_anthropic = MagicMock()
    mock_response = MagicMock(
        usage=MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_input_tokens=200,
            cache_creation_input_tokens=0,
        ),
        content=[MagicMock(type="text", text="hello")],
        stop_reason="end_turn",
    )
    mock_anthropic.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_anthropic

    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    response = client.create_message(
        system_blocks=[{"type": "text", "text": "sys", "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "hi"}],
        tools=[],
        max_tokens=1500,
    )
    assert response is mock_response
    assert mock_anthropic.messages.create.called


@patch("mr.synth.client.Anthropic")
def test_extract_usage_returns_cost_record_fields(mock_anthropic_cls, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    response = MagicMock(
        usage=MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_input_tokens=300,
            cache_creation_input_tokens=0,
        ),
    )
    fields = client.extract_usage(response)
    assert fields["input_tokens"] == 100
    assert fields["output_tokens"] == 50
    assert fields["cache_hits"] == 300
    assert fields["cache_misses"] == 0
