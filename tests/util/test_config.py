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
    assert cfg.limits["max_tool_turns"]["default"] == 12
    assert cfg.limits["max_tool_turns"]["discover"] == 20


def test_load_valid_file(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("""\
schema_version: 2
weights:
  defensibility: 0.40
  financial: 0.30
  implementation: 0.20
  hardware: 0.10
limits:
  max_tool_turns:
    default: 12
    discover: 20
    score: 8
    wishlist_expand: 10
  max_wallclock_seconds: 600
""")
    cfg = load_config(p)
    assert cfg.weights["defensibility"] == 0.40
    # Unspecified keys retain defaults
    assert cfg.limits["max_tool_turns"]["discover"] == 20


def test_unknown_top_level_key_rejected(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("""\
schema_version: 2
limits:
  max_tool_turns:
    default: 12
  max_wallclock_seconds: 600
weihgts:
  defensibility: 0.35
""")
    with pytest.raises(ConfigError, match="weihgts"):
        load_config(p)


def test_v1_config_rejected_with_migrate_message(tmp_path: Path):
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("schema_version: 1\nmodels: {default: x}\n")
    with pytest.raises(ConfigError, match="mr init --migrate"):
        load_config(cfg_path)


def test_unsupported_schema_version_fatal(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("schema_version: 99\n")
    with pytest.raises(ConfigError, match="unsupported schema_version"):
        load_config(p)


def test_default_config_validates_against_its_own_schema():
    # Sanity: the bundled defaults pass the validator.
    cfg = Config(**DEFAULT_CONFIG)
    assert cfg.weights["defensibility"] + cfg.weights["financial"] \
        + cfg.weights["implementation"] + cfg.weights["hardware"] == pytest.approx(1.0)


def test_malformed_yaml_raises_config_error(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("schema_version: 2\nweights: {unclosed\n")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_config(p)


def test_yaml_list_root_raises_config_error(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("- one\n- two\n")
    with pytest.raises(ConfigError, match="must be a YAML mapping"):
        load_config(p)


def test_empty_yaml_file_returns_defaults(tmp_path: Path):
    p = tmp_path / "mr.yaml"
    p.write_text("")
    cfg = load_config(p)
    assert cfg.weights["defensibility"] == 0.35


def test_config_exposes_limits(tmp_path: Path):
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("""\
schema_version: 2
models:
  default: claude-opus-4-7
limits:
  max_tool_turns: {default: 12, discover: 20}
  max_wallclock_seconds: 600
""")
    cfg = load_config(cfg_path)
    assert cfg.limits["max_tool_turns"]["discover"] == 20
    assert cfg.limits["max_wallclock_seconds"] == 600


def test_config_limits_default_when_absent_from_merged_config(tmp_path: Path):
    # limits is required in the schema, so a file without it would fail validation.
    # Test that the _LIMITS_DEFAULT is used when loading defaults (no file).
    cfg = load_config(tmp_path / "absent.yaml")
    assert cfg.limits["max_wallclock_seconds"] == 600
    assert cfg.limits["max_tool_turns"]["default"] == 12


def test_budgets_block_rejected(tmp_path: Path):
    """v2 schema rejects the old budgets key (additionalProperties: false)."""
    p = tmp_path / "mr.yaml"
    p.write_text("""\
schema_version: 2
limits:
  max_tool_turns:
    default: 12
  max_wallclock_seconds: 600
budgets:
  max_tool_turns: {default: 8}
""")
    with pytest.raises(ConfigError):
        load_config(p)
