"""Tests for mr.util.config."""
from pathlib import Path

import pytest

from mr.util.config import (
    DEFAULT_CONFIG,
    Config,
    ConfigError,
    load_config,
)


def test_load_missing_file_returns_defaults(tmp_path: Path):
    cfg = load_config(tmp_path / "absent.yaml")
    assert cfg.weights["defensibility"] == 0.35
    assert cfg.budgets["max_tool_turns"]["default"] == 12
    assert cfg.budgets["max_tool_turns"]["discover"] == 25


def test_load_valid_file(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("""
schema_version: 1
weights:
  defensibility: 0.40
  financial: 0.30
  implementation: 0.20
  hardware: 0.10
""")
    cfg = load_config(p)
    assert cfg.weights["defensibility"] == 0.40
    # Unspecified keys retain defaults
    assert cfg.budgets["max_tool_turns"]["discover"] == 25


def test_unknown_top_level_key_rejected(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("""
schema_version: 1
weihgts:
  defensibility: 0.35
""")
    with pytest.raises(ConfigError, match="weihgts"):
        load_config(p)


def test_unsupported_schema_version_fatal(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("schema_version: 2\n")
    with pytest.raises(ConfigError, match="schema_version"):
        load_config(p)


def test_default_config_validates_against_its_own_schema():
    # Sanity: the bundled defaults pass the validator.
    cfg = Config(**DEFAULT_CONFIG)
    assert cfg.weights["defensibility"] + cfg.weights["financial"] \
        + cfg.weights["implementation"] + cfg.weights["hardware"] == pytest.approx(1.0)
