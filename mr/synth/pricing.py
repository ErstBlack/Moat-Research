"""Per-model token pricing lookup.

Spec §9: pricing baked-in via DEFAULT_CONFIG; operator overrides in mr.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass

from mr.util.config import Config


@dataclass
class ModelPricing:
    input_per_mtok: float
    output_per_mtok: float
    cache_read_per_mtok: float
    cache_write_per_mtok: float

    def estimate_input_cost_usd(self, tokens: int) -> float:
        return tokens / 1_000_000 * self.input_per_mtok

    def estimate_output_cost_usd(self, tokens: int) -> float:
        return tokens / 1_000_000 * self.output_per_mtok


def get_pricing(cfg: Config, model: str) -> ModelPricing:
    """Look up pricing for a model from mr.yaml: models.pricing.

    Raises KeyError if the model isn't in the pricing table.
    """
    pricing_table = cfg.models.get("pricing", {})
    if model not in pricing_table:
        raise KeyError(f"no pricing for {model!r} in mr.yaml: models.pricing")
    p = pricing_table[model]
    return ModelPricing(
        input_per_mtok=p["input"],
        output_per_mtok=p["output"],
        cache_read_per_mtok=p["cache_read"],
        cache_write_per_mtok=p["cache_write"],
    )
