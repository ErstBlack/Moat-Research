"""Anthropic SDK client wrapper with mandatory prompt caching.

Spec §8.1: cached blocks for system prompt, WISHLIST, seen-summary.
Spec §10: post-call usage recorded in costs.jsonl.
"""
from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

from mr.synth.pricing import get_pricing
from mr.util.config import Config


def build_cached_blocks(
    system_text: str,
    wishlist_text: str | None = None,
    seen_summary: str | None = None,
) -> list[dict[str, Any]]:
    """Build a list of cache-controlled system blocks.

    Each unique chunk of repeated content gets its own cache slot so
    additions to one don't invalidate others (e.g., adding to WISHLIST
    doesn't bust the system prompt cache). Empty pieces are skipped.
    """
    blocks: list[dict[str, Any]] = []
    blocks.append({
        "type": "text",
        "text": system_text,
        "cache_control": {"type": "ephemeral"},
    })
    if wishlist_text:
        blocks.append({
            "type": "text",
            "text": wishlist_text,
            "cache_control": {"type": "ephemeral"},
        })
    if seen_summary:
        blocks.append({
            "type": "text",
            "text": seen_summary,
            "cache_control": {"type": "ephemeral"},
        })
    return blocks


class SynthClient:
    """Wrapper around Anthropic API enforcing cache-controlled blocks."""

    def __init__(self, cfg: Config, command: str):
        self.cfg = cfg
        self.command = command
        self.model = self._resolve_model()
        self.pricing = get_pricing(cfg, self.model)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = Anthropic(api_key=api_key)

    def _resolve_model(self) -> str:
        models = self.cfg.models
        per_command = models.get("per_command", {})
        if self.command in per_command:
            return per_command[self.command]
        return models.get("default", "claude-opus-4-7")

    def create_message(
        self,
        *,
        system_blocks: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int,
        tool_choice: dict[str, Any] | None = None,
    ) -> Any:
        """Make a single API call. Returns the raw response object."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_blocks,
            "messages": messages,
            "tools": tools,
        }
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
        return self._client.messages.create(**kwargs)

    def extract_usage(self, response: Any) -> dict[str, int]:
        """Pull token counts from the response's usage block."""
        usage = response.usage
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "cache_hits": getattr(usage, "cache_read_input_tokens", 0) or 0,
            "cache_misses": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        }

    def compute_cost_usd(self, usage: dict[str, int]) -> float:
        """Compute USD cost from extracted usage fields per spec §10."""
        mtok = 1_000_000
        return (
            self.pricing.estimate_input_cost_usd(usage["input_tokens"])
            + self.pricing.estimate_output_cost_usd(usage["output_tokens"])
            + (usage["cache_hits"] / mtok) * self.pricing.cache_read_per_mtok
            + (usage["cache_misses"] / mtok) * self.pricing.cache_write_per_mtok
        )
