"""Four-tier budget enforcement + cold-corpus preflight.

Spec §7. Tier 1: whole-invocation worst-case ceiling. Tier 2: per-turn
pre-call estimate. Tier 3: tool-turn cap. Tier 4: wallclock cap +
consecutive cache misses.
"""
from __future__ import annotations

import time
from pathlib import Path

import yaml

from mr.synth.pricing import get_pricing
from mr.util.config import Config

_MIN_WISHLIST_SOURCES = 5
_BUDGET_HEADROOM = 0.9  # abort at 90% of budget to leave headroom
_CACHE_MISS_GRACE_TURNS = 2  # turns 1-2 are exempt from cache-miss enforcement
_CONSECUTIVE_MISS_LIMIT = 2  # abort after this many consecutive re-write misses


class BudgetExceeded(Exception):  # noqa: N818
    """Raised when any budget tier or preflight fails."""


def worst_case_ceiling(cfg: Config, command: str, model: str) -> float:
    """Tier 1: cache-amortized worst-case ceiling for the entire invocation.

    Per §7: input is paid once per unique block (caching dedups across turns);
    each turn's fresh input is one tool result. Output is max_tokens × turns.
    """
    pricing = get_pricing(cfg, model)
    budgets = cfg.budgets
    max_turns = budgets["max_tool_turns"].get(command, budgets["max_tool_turns"]["default"])
    base = budgets["base_input_tokens"]
    avg_tool_result = budgets["avg_tool_result_tokens"]
    max_tokens = budgets["max_tokens_per_turn"]

    input_tokens = base + max_turns * avg_tool_result
    output_tokens = max_turns * max_tokens

    return (
        pricing.estimate_input_cost_usd(input_tokens)
        + pricing.estimate_output_cost_usd(output_tokens)
    )


def cold_corpus_preflight(wishlist_path: Path) -> None:
    """Refuse mr discover if WISHLIST.md has fewer than 5 sources.

    Per §7 cold-corpus preflight: discovering against an empty seed
    produces low-quality candidates from web search alone.
    """
    if not wishlist_path.exists():
        raise BudgetExceeded(
            f"WISHLIST.md not found at {wishlist_path}. "
            f"Run `mr wishlist expand --seed --budget 0.50` to bootstrap."
        )
    raw = yaml.safe_load(wishlist_path.read_text()) or {}
    sources = raw.get("sources", []) or []
    if len(sources) < _MIN_WISHLIST_SOURCES:
        raise BudgetExceeded(
            f"WISHLIST.md has {len(sources)} sources; minimum {_MIN_WISHLIST_SOURCES}. "
            f"Run `mr wishlist expand --seed --budget 0.50` first."
        )


class BudgetTracker:  # noqa: PLR0913
    """Per-invocation runtime tracking for tiers 2-4."""

    def __init__(
        self,
        cfg: Config,
        command: str,
        model: str,
        budget_usd: float,
        costs_path: Path | None,
    ):
        self.cfg = cfg
        self.command = command
        self.model = model
        self.budget_usd = budget_usd
        self.costs_path = costs_path
        self.pricing = get_pricing(cfg, model)
        self.budgets = cfg.budgets

        self._tool_turns = 0
        self._start_monotonic = time.monotonic()
        # Cache-miss tracking: turn index → (missed, fingerprint)
        self._turn_idx = 0
        self._consecutive_misses = 0
        self._seen_fingerprints: set[str] = set()

    def check_pre_call(self, input_tokens_estimate: int, max_output_tokens: int) -> None:
        """Tier 2: abort if running_tally + estimate > budget × 0.9."""
        running = 0.0

        estimate = (
            self.pricing.estimate_input_cost_usd(input_tokens_estimate)
            + self.pricing.estimate_output_cost_usd(max_output_tokens)
        )
        if running + estimate > self.budget_usd * _BUDGET_HEADROOM:
            raise BudgetExceeded(
                f"per-turn estimate would exceed budget × {_BUDGET_HEADROOM}: "
                f"running ${running:.2f} + estimate ${estimate:.2f} > "
                f"${self.budget_usd * _BUDGET_HEADROOM:.2f}"
            )

    def note_tool_turn(self) -> None:
        """Tier 3: increment turn counter; abort if exceeded max_tool_turns."""
        self._tool_turns += 1
        max_turns = self.budgets["max_tool_turns"].get(
            self.command, self.budgets["max_tool_turns"]["default"]
        )
        if self._tool_turns > max_turns:
            raise BudgetExceeded(
                f"tool-turn cap exceeded: {self._tool_turns} > {max_turns}"
            )

    def check_wallclock(self) -> None:
        """Tier 4a: abort if elapsed wallclock exceeds the cap."""
        elapsed = time.monotonic() - self._start_monotonic
        cap = self.budgets["max_wallclock_seconds"]
        if elapsed > cap:
            raise BudgetExceeded(
                f"wallclock cap exceeded: {elapsed:.1f}s > {cap}s"
            )

    def note_turn_cache_status(self, *, missed: bool, fingerprint: str) -> None:
        """Tier 4b: track consecutive cache misses (re-writes after turn 3)."""
        self._turn_idx += 1
        # Turns 1-2 are exempt (cache must be populated first)
        if self._turn_idx <= _CACHE_MISS_GRACE_TURNS:
            if missed:
                self._seen_fingerprints.add(fingerprint)
            return

        if missed and fingerprint in self._seen_fingerprints:
            # This is a *re-write* — block was previously cached and now invalidated
            self._consecutive_misses += 1
        elif missed:
            # First-time creation event for this fingerprint; not a miss-rewrite
            self._seen_fingerprints.add(fingerprint)
        else:
            self._consecutive_misses = 0

        if self._consecutive_misses >= _CONSECUTIVE_MISS_LIMIT:
            raise BudgetExceeded(
                f"consecutive cache misses (re-writes) at turn {self._turn_idx}: "
                f"working set exceeds 5-min TTL"
            )
