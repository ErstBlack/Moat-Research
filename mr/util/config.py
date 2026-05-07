"""mr.yaml loader with JSON-Schema validation, schema-version-1-only.

Spec: §9 (config schema) and §15.2 (migration deferred).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

_SCHEMA_PATH = Path(__file__).parent / "config_schema.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "models": {
        "default": "claude-opus-4-7",
        "bulk": "claude-sonnet-4-6",
        "per_command": {"wishlist_expand": "claude-sonnet-4-6"},
        "pricing": {
            "claude-opus-4-7": {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_write": 18.75},
            "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
            "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cache_read": 0.10, "cache_write": 1.25},
        },
    },
    "weights": {
        "defensibility": 0.35,
        "financial": 0.30,
        "implementation": 0.20,
        "hardware": 0.15,
    },
    "disqualifiers": {
        "defensibility_min": 5,
        "any_axis_zero": True,
        "unrestricted_archive_min_snapshots": 100,
        "unrestricted_archive_min_years": 3,
    },
    "lanes": [
        "ephemeral_public",
        "soon_to_be_restricted",
        "cross_source_fusion",
        "derived_artifact",
        "niche_vertical",
        "other",
    ],
    "niche_aliases": {},
    "interests": {"affirm": [], "avoid": []},
    "hardware": {
        "cpu": "2× Intel Xeon E5-2698 v4 (40c/80t)",
        "ram_gb": 250,
        "gpu": "NVIDIA P4 (8GB), shared",
        "storage_tb": 17,
        "network": "residential broadband",
    },
    "budgets": {
        "default_per_invocation_usd": {
            "default": 1.00,
            "discover": 5.00,
            "score": 3.00,
            "wishlist_expand": 2.00,
        },
        "max_tool_turns": {
            "default": 12,
            "discover": 25,
            "score": 15,
            "wishlist_expand": 20,
        },
        "max_tokens_per_turn": 1500,
        "max_wallclock_seconds": 240,
        "max_verification_calls": 12,
        "base_input_tokens": 6000,
        "avg_tool_result_tokens": 1500,
    },
    "status": {
        "stale_approved_days": 90,
        "dead_link_window_days": 14,
    },
}


class ConfigError(Exception):
    """Raised on invalid mr.yaml content."""


@dataclass
class Config:
    schema_version: int = 1
    models: dict[str, Any] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    disqualifiers: dict[str, Any] = field(default_factory=dict)
    lanes: list[str] = field(default_factory=list)
    niche_aliases: dict[str, list[str]] = field(default_factory=dict)
    interests: dict[str, list[str]] = field(default_factory=dict)
    hardware: dict[str, Any] = field(default_factory=dict)
    budgets: dict[str, Any] = field(default_factory=dict)
    status: dict[str, Any] = field(default_factory=dict)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursive merge: override wins; missing keys fall back to base."""
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


@lru_cache(maxsize=1)
def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def load_config(path: Path) -> Config:
    """Load mr.yaml from disk, falling back to bundled defaults.

    Raises ConfigError on invalid content or unsupported schema_version.
    """
    if not path.exists():
        return Config(**DEFAULT_CONFIG)

    try:
        parsed = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise ConfigError(f"{path}: invalid YAML — {e}") from e

    if parsed is None:
        return Config(**DEFAULT_CONFIG)
    if not isinstance(parsed, dict):
        raise ConfigError(f"{path}: root must be a YAML mapping, got {type(parsed).__name__}")

    schema_version = parsed.get("schema_version", 1)
    if schema_version != 1:
        raise ConfigError(
            f"{path}: schema_version {schema_version} is not supported in v1. "
            f"Migration framework is deferred (see spec §15.2)."
        )

    validator = Draft202012Validator(_load_schema())
    errors = sorted(validator.iter_errors(parsed), key=lambda e: e.path)
    if errors:
        first = errors[0]
        path_str = "/".join(str(p) for p in first.path)
        location = f" at {path_str}" if path_str else ""
        raise ConfigError(f"{path}: {first.message}{location}")

    merged = _deep_merge(DEFAULT_CONFIG, parsed)
    return Config(**merged)
