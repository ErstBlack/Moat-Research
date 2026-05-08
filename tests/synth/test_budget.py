from pathlib import Path

import pytest

from mr.synth.budget import (
    BudgetExceeded,
    BudgetTracker,
    cold_corpus_preflight,
    worst_case_ceiling,
)
from mr.util.config import DEFAULT_CONFIG, Config


def test_worst_case_ceiling_for_discover_fits_5usd_budget():
    """Discover defaults: 25 turns × (6000 + 25×1500) input + 25 × 1500 output."""
    cfg = Config(**DEFAULT_CONFIG)
    ceiling = worst_case_ceiling(cfg, command="discover", model="claude-opus-4-7")
    # input: (6000 + 25*1500) * $15/M = 43500 * 15e-6 = $0.65
    # output: 25 * 1500 * $75/M = 37500 * 75e-6 = $2.81
    # total ≈ $3.47
    assert ceiling < 5.0
    assert ceiling > 3.0


def test_worst_case_ceiling_for_score_fits_3usd():
    cfg = Config(**DEFAULT_CONFIG)
    ceiling = worst_case_ceiling(cfg, command="score", model="claude-opus-4-7")
    assert ceiling < 3.0


def test_per_turn_estimate_aborts_at_90pct(tmp_path: Path):
    cfg = Config(**DEFAULT_CONFIG)
    # Use a tiny budget so that a single estimate exceeds 90% of it
    tracker = BudgetTracker(cfg=cfg, command="discover", model="claude-opus-4-7",
                            budget_usd=0.001, costs_path=tmp_path / "costs.jsonl")
    # Estimate on 200k input + 1500 output tokens >> 0.001 × 0.9 → abort
    with pytest.raises(BudgetExceeded, match="per-turn"):
        tracker.check_pre_call(input_tokens_estimate=200_000, max_output_tokens=1500)


def test_tool_turn_cap_aborts(tmp_path: Path):
    cfg = Config(**DEFAULT_CONFIG)
    tracker = BudgetTracker(cfg=cfg, command="score", model="claude-opus-4-7",
                            budget_usd=10.00, costs_path=tmp_path / "costs.jsonl")
    # score default max_tool_turns is 15
    for _ in range(15):
        tracker.note_tool_turn()
    with pytest.raises(BudgetExceeded, match="tool-turn"):
        tracker.note_tool_turn()


def test_wallclock_cap_aborts():
    cfg = Config(**DEFAULT_CONFIG)
    tracker = BudgetTracker(cfg=cfg, command="discover", model="claude-opus-4-7",
                            budget_usd=10.00, costs_path=None)
    # Force start time backward
    tracker._start_monotonic -= 9999  # type: ignore[attr-defined]
    with pytest.raises(BudgetExceeded, match="wallclock"):
        tracker.check_wallclock()


def test_consecutive_cache_misses_after_turn_3_abort():
    cfg = Config(**DEFAULT_CONFIG)
    tracker = BudgetTracker(cfg=cfg, command="discover", model="claude-opus-4-7",
                            budget_usd=10.00, costs_path=None)
    # Turns 1-2 cache misses are exempt
    tracker.note_turn_cache_status(missed=True, fingerprint="block-a")
    tracker.note_turn_cache_status(missed=True, fingerprint="block-b")
    # Turn 3+ misses on already-seen fingerprints trigger abort
    with pytest.raises(BudgetExceeded, match="cache"):
        tracker.note_turn_cache_status(missed=True, fingerprint="block-a")
        tracker.note_turn_cache_status(missed=True, fingerprint="block-b")


def test_cold_corpus_preflight_passes_with_5plus_sources(tmp_path: Path):
    wishlist = tmp_path / "WISHLIST.md"
    wishlist.write_text("sources:\n" + "\n".join(
        f"  - {{id: s{i}, url: https://e{i}.com, lane: niche_vertical, "
        f"rationale: x, last_verified: '2026-05-07', dead_link: false}}" for i in range(5)
    ))
    cold_corpus_preflight(wishlist)  # no raise


def test_cold_corpus_preflight_aborts_below_5(tmp_path: Path):
    wishlist = tmp_path / "WISHLIST.md"
    wishlist.write_text("sources: []\n")
    with pytest.raises(BudgetExceeded, match="WISHLIST"):
        cold_corpus_preflight(wishlist)
