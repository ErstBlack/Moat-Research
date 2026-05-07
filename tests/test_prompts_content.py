from pathlib import Path

import pytest


def _load(name: str) -> str:
    path = Path("prompts") / f"{name}.md"
    if not path.exists():
        pytest.skip(f"{path} not yet written")
    return path.read_text()


def test_discover_prompt_mandates_seen_lookup():
    text = _load("discover")
    assert "seen_lookup" in text


def test_discover_prompt_lists_all_lanes():
    text = _load("discover")
    for lane in ("ephemeral_public", "soon_to_be_restricted",
                 "cross_source_fusion", "derived_artifact",
                 "niche_vertical", "other"):
        assert lane in text


def test_discover_prompt_mandates_hardware_keys():
    text = _load("discover")
    assert "peak_gpu_gb" in text
    assert "sustained_ram_gb" in text
    assert "storage_tb" in text


def test_discover_prompt_mentions_diversity_bias():
    text = _load("discover")
    assert "diversity" in text.lower() or "underrepresented" in text.lower()


def test_discover_prompt_mentions_interests():
    text = _load("discover")
    assert "interests.affirm" in text or "affirm" in text.lower()
    assert "avoid" in text.lower()


def test_discover_prompt_mentions_yaml_brief_fence():
    text = _load("discover")
    assert "yaml-brief" in text


def test_score_prompt_mentions_rubric():
    text = _load("score")
    assert "0-10" in text
    assert "defensibility" in text.lower()


def test_wishlist_expand_prompt_mentions_seen_lookup():
    text = _load("wishlist_expand")
    assert "seen_lookup" in text
