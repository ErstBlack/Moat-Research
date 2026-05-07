import pytest

from mr.synth.pricing import ModelPricing, get_pricing
from mr.util.config import DEFAULT_CONFIG, Config


def test_default_opus_pricing():
    cfg = Config(**DEFAULT_CONFIG)
    p = get_pricing(cfg, "claude-opus-4-7")
    assert p.input_per_mtok == 15.0
    assert p.output_per_mtok == 75.0
    assert p.cache_read_per_mtok == 1.5
    assert p.cache_write_per_mtok == 18.75


def test_default_sonnet_pricing():
    cfg = Config(**DEFAULT_CONFIG)
    p = get_pricing(cfg, "claude-sonnet-4-6")
    assert p.input_per_mtok == 3.0
    assert p.output_per_mtok == 15.0


def test_unknown_model_raises():
    cfg = Config(**DEFAULT_CONFIG)
    with pytest.raises(KeyError, match="claude-unknown"):
        get_pricing(cfg, "claude-unknown")


def test_estimate_input_cost_usd():
    p = ModelPricing(input_per_mtok=15.0, output_per_mtok=75.0,
                     cache_read_per_mtok=1.5, cache_write_per_mtok=18.75)
    # 1M tokens at $15/M = $15.00
    assert p.estimate_input_cost_usd(1_000_000) == 15.0
    # 100k tokens at $15/M = $1.50
    assert p.estimate_input_cost_usd(100_000) == pytest.approx(1.5)
