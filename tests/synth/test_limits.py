"""Tests for mr.synth.limits."""
from pathlib import Path

import pytest

from mr.synth.limits import (
    LimitExceeded,
    RunLimits,
    cold_corpus_preflight,
    run_limits_from_config,
)


def test_cold_corpus_preflight_missing_file(tmp_path: Path):
    with pytest.raises(LimitExceeded, match="WISHLIST.md not found"):
        cold_corpus_preflight(tmp_path / "WISHLIST.md")


def test_cold_corpus_preflight_short_wishlist(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources:\n  - id: a\n  - id: b\n")
    with pytest.raises(LimitExceeded, match="minimum 5"):
        cold_corpus_preflight(p)


def test_cold_corpus_preflight_passes(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources:\n" + "".join(f"  - id: src_{i}\n" for i in range(5)))
    cold_corpus_preflight(p)


def test_run_limits_from_config():
    cfg = {
        "max_tool_turns": {"default": 12, "discover": 20},
        "max_wallclock_seconds": 600,
        "max_output_tokens": 8192,
    }
    limits = run_limits_from_config(cfg, command="discover")
    assert limits.max_tool_turns == 20
    assert limits.max_wallclock_seconds == 600
    assert limits.max_output_tokens == 8192


def test_run_limits_falls_back_to_default():
    cfg = {
        "max_tool_turns": {"default": 12},
        "max_wallclock_seconds": 600,
        "max_output_tokens": 8192,
    }
    limits = run_limits_from_config(cfg, command="score")
    assert limits.max_tool_turns == 12
