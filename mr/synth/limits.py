"""Runtime limits (wallclock + tool-turn cap) and cold-corpus preflight.

Replaces the financial parts of mr.synth.budget for the Max-subscription
port. No financial tracking; SDK enforces tool turns via max_turns;
wallclock is enforced in mr.synth.session via asyncio.wait_for.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_MIN_WISHLIST_SOURCES = 5


class LimitExceeded(Exception):  # noqa: N818
    """Raised when any limit or preflight check fails."""


@dataclass
class RunLimits:
    max_tool_turns: int
    max_wallclock_seconds: int
    max_output_tokens: int


def run_limits_from_config(cfg: dict[str, Any], *, command: str) -> RunLimits:
    """Resolve per-command tool turn cap; flat values for the rest."""
    turns = cfg["max_tool_turns"]
    return RunLimits(
        max_tool_turns=turns.get(command, turns["default"]),
        max_wallclock_seconds=cfg["max_wallclock_seconds"],
        max_output_tokens=cfg["max_output_tokens"],
    )


def cold_corpus_preflight(wishlist_path: Path) -> None:
    """Refuse mr discover if WISHLIST.md has fewer than 5 sources."""
    if not wishlist_path.exists():
        raise LimitExceeded(
            f"WISHLIST.md not found at {wishlist_path}. "
            f"Run `mr wishlist expand --seed` to bootstrap."
        )
    raw = yaml.safe_load(wishlist_path.read_text()) or {}
    sources = raw.get("sources", []) or []
    if len(sources) < _MIN_WISHLIST_SOURCES:
        raise LimitExceeded(
            f"WISHLIST.md has {len(sources)} sources; minimum {_MIN_WISHLIST_SOURCES}. "
            f"Run `mr wishlist expand --seed` first."
        )
