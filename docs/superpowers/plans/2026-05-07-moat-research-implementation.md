# moat-research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-operator CLI tool (`mr`) and structured corpus that discovers, scores, and graduates data-moat opportunities for a solo operator, per the spec at `docs/superpowers/specs/2026-05-07-moat-research-design.md`.

**Architecture:** Single Python 3.12 package (`mr/`) split into focused subpackages — `cli/`, `lifecycle/`, `scoring/`, `dedup/`, `tools/`, `synth/`, `wishlist/`, `handoff/`, `util/`. Anthropic SDK with native server tools (`web_search_20260209`, `web_fetch_20260209`, `code_execution`) plus custom Python tools (`wayback_check`, `robots_check`, `head_check`, `seen_lookup`, `firecrawl_scrape`). On-demand CLI only — no daemon, no scheduler. Lifecycle is one-directional: `candidates/ → scored/ → {rejected, approved} → graduated/`.

**Tech Stack:** Python 3.12 · uv (package manager) · typer (CLI) · pyyaml · httpx · jsonschema · waybackpy · firecrawl-py (optional) · anthropic · pytest

**Spec reference:** every task references `docs/superpowers/specs/2026-05-07-moat-research-design.md` by section number. Read the cited section before starting the task — the spec is the source of truth.

**Test discipline:** TDD throughout. Write failing test → run to confirm fail → implement → run to confirm pass → commit. Pure-function tasks get full unit tests; LLM/web-touching tasks use heavy mocking. Integration tests at the end.

**Commit cadence:** every task ends with a commit. Use `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` per repo convention.

---

## Phase 1: Migration & Scaffolding

### Task 1: Migration cleanup

**Files:**
- Delete: `briefs/` (entire directory)
- Delete: `FOCUS.md`
- Modify: `.gitignore` (append entries)

- [ ] **Step 1: Verify what's being deleted**

Run: `ls -la briefs/ FOCUS.md`
Expected: 26 brief files in `briefs/` plus `briefs/index.json`; `FOCUS.md` exists.

- [ ] **Step 2: Delete the obsolete corpus and focus doc**

```bash
rm -rf briefs/
rm FOCUS.md
```

- [ ] **Step 3: Augment `.gitignore`**

Append to `.gitignore`:

```
# moat-research runtime state
/.moat-research/

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

- [ ] **Step 4: Verify state**

Run: `git status`
Expected: `briefs/` deletions, `FOCUS.md` deletion, `.gitignore` modification.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
chore: discard prior corpus for greenfield restart per v2 spec

Removes briefs/ (26 prior artifacts + index.json) and FOCUS.md
(stale priorities; status moves into mr status). Augments .gitignore
for /.moat-research/ runtime state and Python artifacts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: pyproject.toml + uv project bootstrap

**Files:**
- Create: `pyproject.toml`
- Create: `uv.lock` (generated)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "moat-research"
version = "0.1.0"
description = "Solo-operator CLI for discovering, scoring, and graduating data-moat opportunities"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.40.0",
    "typer>=0.12.0",
    "pyyaml>=6.0",
    "httpx>=0.27.0",
    "jsonschema>=4.21.0",
    "waybackpy>=3.0.6",
    "rich>=13.7.0",
]

[project.optional-dependencies]
firecrawl = ["firecrawl-py>=4.21.0"]

[project.scripts]
mr = "mr.cli.main:app"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.5.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mr"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --strict-markers"

[tool.ruff]
line-length = 110
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
```

- [ ] **Step 2: Sync the environment**

Run: `uv sync`
Expected: Resolves dependencies, creates `.venv/` and `uv.lock`.

- [ ] **Step 3: Verify the toolchain**

Run: `uv run python --version && uv run pytest --version`
Expected: `Python 3.12.X` and `pytest 8.X.X`.

- [ ] **Step 4: Verify `mr` script entry stub will work**

The `mr` script entry is `mr.cli.main:app`. The package doesn't exist yet — it's created in Task 3. Skip running `mr --help` here; it will fail until Task 3.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "$(cat <<'EOF'
chore: bootstrap moat-research Python package via uv

Adds pyproject.toml with deps (anthropic, typer, pyyaml, httpx,
jsonschema, waybackpy, rich) plus dev tools (pytest, pytest-mock,
pytest-cov, ruff). firecrawl-py is an optional extra. Python 3.12
required. Generates uv.lock.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Empty package scaffolding

**Files:**
- Create: `mr/__init__.py`
- Create: `mr/__main__.py`
- Create: `mr/cli/__init__.py`
- Create: `mr/cli/main.py`
- Create: `mr/lifecycle/__init__.py`
- Create: `mr/scoring/__init__.py`
- Create: `mr/dedup/__init__.py`
- Create: `mr/tools/__init__.py`
- Create: `mr/synth/__init__.py`
- Create: `mr/wishlist/__init__.py`
- Create: `mr/handoff/__init__.py`
- Create: `mr/util/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write the smoke test**

`tests/test_package.py`:

```python
def test_mr_imports():
    import mr
    assert mr is not None

def test_cli_main_app_callable():
    from mr.cli.main import app
    assert callable(app)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'mr'`.

- [ ] **Step 3: Create the package skeleton**

`mr/__init__.py`:

```python
"""moat-research: solo-operator CLI for data-moat opportunities."""
__version__ = "0.1.0"
```

`mr/__main__.py`:

```python
from mr.cli.main import app

if __name__ == "__main__":
    app()
```

Create empty `__init__.py` for each subpackage:
- `mr/cli/__init__.py`
- `mr/lifecycle/__init__.py`
- `mr/scoring/__init__.py`
- `mr/dedup/__init__.py`
- `mr/tools/__init__.py`
- `mr/synth/__init__.py`
- `mr/wishlist/__init__.py`
- `mr/handoff/__init__.py`
- `mr/util/__init__.py`

`mr/cli/main.py` (minimal Typer shell — subcommands wired in later tasks):

```python
"""Entry point for the `mr` CLI."""
import typer

app = typer.Typer(
    name="mr",
    help="Discover, score, and graduate data-moat opportunities.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the installed mr version."""
    from mr import __version__
    typer.echo(f"mr {__version__}")
```

`tests/__init__.py`: empty file.

`tests/conftest.py`:

```python
"""Shared pytest fixtures for moat-research tests."""
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """An empty temp directory standing in for a fresh moat-research repo."""
    return tmp_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_package.py -v`
Expected: PASS for both tests.

- [ ] **Step 5: Verify the CLI entry works**

Run: `uv run mr version`
Expected: `mr 0.1.0`.

- [ ] **Step 6: Commit**

```bash
git add mr/ tests/
git commit -m "$(cat <<'EOF'
feat: scaffold mr package with empty subpackages and version cmd

Creates the mr/ package skeleton (cli, lifecycle, scoring, dedup,
tools, synth, wishlist, handoff, util) and the typer app shell.
Adds a smoke `mr version` subcommand and a tests/conftest.py with
a tmp_repo fixture. Subcommands are wired in subsequent tasks.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 2: Util layer (config, slug, lock, costs)

### Task 4: mr.yaml schema + config loader

**Spec sections:** §9 (mr.yaml schema), §15.2 (schema_version migration deferred)

**Files:**
- Create: `mr/util/config.py`
- Create: `mr/util/config_schema.json`
- Create: `tests/util/__init__.py`
- Create: `tests/util/test_config.py`

- [ ] **Step 1: Write the failing tests**

`tests/util/test_config.py`:

```python
"""Tests for mr.util.config."""
from pathlib import Path

import pytest

from mr.util.config import (
    Config,
    ConfigError,
    DEFAULT_CONFIG,
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
        + cfg.weights["implementation"] + cfg.weights["hardware"] == 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/util/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'mr.util.config'`.

- [ ] **Step 3: Write the JSON schema**

`mr/util/config_schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version"],
  "properties": {
    "schema_version": {"type": "integer", "const": 1},
    "models": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "default": {"type": "string"},
        "bulk": {"type": "string"},
        "per_command": {"type": "object", "additionalProperties": {"type": "string"}},
        "pricing": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "additionalProperties": false,
            "required": ["input", "output", "cache_read", "cache_write"],
            "properties": {
              "input": {"type": "number"},
              "output": {"type": "number"},
              "cache_read": {"type": "number"},
              "cache_write": {"type": "number"}
            }
          }
        }
      }
    },
    "weights": {
      "type": "object",
      "additionalProperties": false,
      "required": ["defensibility", "financial", "implementation", "hardware"],
      "properties": {
        "defensibility": {"type": "number", "minimum": 0, "maximum": 1},
        "financial": {"type": "number", "minimum": 0, "maximum": 1},
        "implementation": {"type": "number", "minimum": 0, "maximum": 1},
        "hardware": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "disqualifiers": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "defensibility_min": {"type": "integer"},
        "any_axis_zero": {"type": "boolean"},
        "unrestricted_archive_min_snapshots": {"type": "integer"},
        "unrestricted_archive_min_years": {"type": "integer"}
      }
    },
    "lanes": {"type": "array", "items": {"type": "string"}},
    "niche_aliases": {
      "type": "object",
      "additionalProperties": {"type": "array", "items": {"type": "string"}}
    },
    "interests": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "affirm": {"type": "array", "items": {"type": "string"}},
        "avoid": {"type": "array", "items": {"type": "string"}}
      }
    },
    "hardware": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "cpu": {"type": "string"},
        "ram_gb": {"type": "integer"},
        "gpu": {"type": "string"},
        "storage_tb": {"type": "integer"},
        "network": {"type": "string"}
      }
    },
    "budgets": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "default_per_invocation_usd": {
          "type": "object",
          "additionalProperties": {"type": "number"}
        },
        "max_tool_turns": {
          "type": "object",
          "additionalProperties": {"type": "integer"}
        },
        "max_tokens_per_turn": {"type": "integer"},
        "max_wallclock_seconds": {"type": "integer"},
        "max_verification_calls": {"type": "integer"},
        "base_input_tokens": {"type": "integer"},
        "avg_tool_result_tokens": {"type": "integer"}
      }
    },
    "status": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "stale_approved_days": {"type": "integer"},
        "dead_link_window_days": {"type": "integer"}
      }
    }
  }
}
```

- [ ] **Step 4: Implement `mr/util/config.py`**

```python
"""mr.yaml loader with JSON-Schema validation, schema-version-1-only.

Spec: §9 (config schema) and §15.2 (migration deferred).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, ValidationError

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


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text())


def load_config(path: Path) -> Config:
    """Load mr.yaml from disk, falling back to bundled defaults.

    Raises ConfigError on invalid content or unsupported schema_version.
    """
    if not path.exists():
        return Config(**DEFAULT_CONFIG)

    raw = yaml.safe_load(path.read_text()) or {}

    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: root must be a YAML mapping")

    schema_version = raw.get("schema_version", 1)
    if schema_version != 1:
        raise ConfigError(
            f"{path}: schema_version {schema_version} is not supported in v1. "
            f"Migration framework is deferred (see spec §15.2)."
        )

    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(raw), key=lambda e: e.path)
    if errors:
        first = errors[0]
        raise ConfigError(f"{path}: {first.message} at {'/'.join(str(p) for p in first.path)}")

    merged = _deep_merge(DEFAULT_CONFIG, raw)
    return Config(**merged)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/util/test_config.py -v`
Expected: PASS for all 5 tests.

- [ ] **Step 6: Commit**

```bash
git add mr/util/config.py mr/util/config_schema.json tests/util/test_config.py tests/util/__init__.py
git commit -m "$(cat <<'EOF'
feat(util): mr.yaml loader with JSON-Schema validation

Implements load_config() per spec §9: bundled defaults, deep-merge
with file overrides, strict-key validation via jsonschema, and
schema_version-1-only fatal error path (migration framework deferred
per §15.2). Includes tests for default fallback, unknown-key rejection,
and version-mismatch error.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Slug normalization

**Spec sections:** §6.1 (slug = lowercase-kebab from title, ≤40 chars, ASCII)

**Files:**
- Create: `mr/util/slug.py`
- Create: `tests/util/test_slug.py`

- [ ] **Step 1: Write the failing tests**

`tests/util/test_slug.py`:

```python
from mr.util.slug import slugify


def test_basic_lowercase_kebab():
    assert slugify("FAA NOTAMs Aviation Alerts") == "faa-notams-aviation-alerts"


def test_strips_punctuation():
    assert slugify("Real-time! Cameras (SoMD)") == "real-time-cameras-somd"


def test_max_40_chars():
    s = slugify("a" * 100)
    assert len(s) <= 40
    assert s == "a" * 40


def test_truncates_at_word_boundary():
    s = slugify("aaaaa-bbbbb-ccccc-ddddd-eeeee-ffffff-this-is-too-long")
    assert len(s) <= 40
    assert not s.endswith("-")


def test_collapses_whitespace_and_dashes():
    assert slugify("foo   bar---baz") == "foo-bar-baz"


def test_strips_non_ascii():
    assert slugify("Münchéñ café") == "munchen-cafe"


def test_empty_input_returns_fallback():
    assert slugify("") == "untitled"
    assert slugify("!!!") == "untitled"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/util/test_slug.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/util/slug.py`**

```python
"""Slug normalization for filenames and identifiers.

Per spec §6.1: lowercase-kebab from title, ≤40 chars, ASCII-only.
"""
from __future__ import annotations

import re
import unicodedata

_MAX_LEN = 40
_FALLBACK = "untitled"


def slugify(text: str) -> str:
    """Normalize text into a kebab-case ASCII slug ≤40 chars."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    kebab = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")

    if not kebab:
        return _FALLBACK

    if len(kebab) <= _MAX_LEN:
        return kebab

    truncated = kebab[:_MAX_LEN]
    last_dash = truncated.rfind("-")
    if last_dash > 0:
        truncated = truncated[:last_dash]

    return truncated or _FALLBACK
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/util/test_slug.py -v`
Expected: PASS for all 7 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/util/slug.py tests/util/test_slug.py
git commit -m "$(cat <<'EOF'
feat(util): slug normalization (lowercase-kebab, ASCII, ≤40 chars)

Implements slugify() per spec §6.1: NFKD-normalize, strip non-ASCII,
collapse non-alphanumeric runs into single dashes, truncate at word
boundary if over 40 chars. Empty/punctuation-only input returns the
fallback "untitled". Used by filename and frontmatter helpers.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: flock(2) wrapper

**Spec sections:** §10 (concurrency contract), §3 (flock on .moat-research/.lock)

**Files:**
- Create: `mr/util/lock.py`
- Create: `tests/util/test_lock.py`

- [ ] **Step 1: Write the failing tests**

`tests/util/test_lock.py`:

```python
import multiprocessing
import time
from pathlib import Path

import pytest

from mr.util.lock import LockTimeout, exclusive_lock


def test_acquires_and_releases(tmp_path: Path):
    lockfile = tmp_path / ".lock"
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        assert lockfile.exists()
    # Re-acquiring after release works
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        pass


def _hold_lock(lockfile: str, hold_seconds: float, ready_q: multiprocessing.Queue):
    from mr.util.lock import exclusive_lock as el
    with el(Path(lockfile), timeout_seconds=2.0):
        ready_q.put("acquired")
        time.sleep(hold_seconds)


def test_blocks_then_times_out(tmp_path: Path):
    lockfile = tmp_path / ".lock"
    ready: multiprocessing.Queue = multiprocessing.Queue()
    holder = multiprocessing.Process(target=_hold_lock, args=(str(lockfile), 3.0, ready))
    holder.start()
    try:
        ready.get(timeout=2.0)  # wait for holder to acquire
        with pytest.raises(LockTimeout):
            with exclusive_lock(lockfile, timeout_seconds=0.5):
                pass
    finally:
        holder.join(timeout=5.0)


def test_creates_parent_dir(tmp_path: Path):
    lockfile = tmp_path / "subdir" / ".lock"
    with exclusive_lock(lockfile, timeout_seconds=2.0):
        assert lockfile.parent.is_dir()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/util/test_lock.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/util/lock.py`**

```python
"""POSIX flock(2)-based exclusive lock for .moat-research/.lock.

Per spec §10: blocks up to 60s by default, then errors. Local POSIX
filesystem only — NFS is unsupported.
"""
from __future__ import annotations

import errno
import fcntl
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class LockTimeout(Exception):
    """Raised when the lock cannot be acquired within timeout_seconds."""


@contextmanager
def exclusive_lock(path: Path, timeout_seconds: float = 60.0) -> Iterator[None]:
    """Hold an exclusive flock on `path` for the duration of the with-block.

    Creates the parent directory and the lockfile if missing. Polls
    every 100ms; raises LockTimeout if the lock isn't available within
    timeout_seconds.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if e.errno not in (errno.EAGAIN, errno.EACCES):
                    raise
                if time.monotonic() >= deadline:
                    raise LockTimeout(
                        f"could not acquire {path} within {timeout_seconds:.1f}s"
                    ) from e
                time.sleep(0.1)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/util/test_lock.py -v`
Expected: PASS for all 3 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/util/lock.py tests/util/test_lock.py
git commit -m "$(cat <<'EOF'
feat(util): flock-based exclusive lock for .moat-research/.lock

Implements exclusive_lock() context manager per spec §10. Polls at
100ms; raises LockTimeout on deadline. Creates parent dir lazily.
POSIX-only — NFS is unsupported per spec §10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: costs.jsonl writer

**Spec sections:** §10 (costs.jsonl schema)

**Files:**
- Create: `mr/util/costs.py`
- Create: `tests/util/test_costs.py`

- [ ] **Step 1: Write the failing tests**

`tests/util/test_costs.py`:

```python
import json
from datetime import datetime, timezone
from pathlib import Path

from mr.util.costs import CostRecord, append_cost, read_cost_history


def test_append_and_read_roundtrip(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    rec = CostRecord(
        ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc),
        command="discover",
        model="claude-opus-4-7",
        input_tokens=1000,
        cached_input_tokens=500,
        output_tokens=200,
        cache_hits=500,
        cache_misses=0,
        code_execution_container_seconds=2.5,
        cost_usd=0.0345,
    )
    append_cost(path, rec)
    records = read_cost_history(path)
    assert len(records) == 1
    assert records[0].command == "discover"
    assert records[0].cost_usd == 0.0345


def test_appends_to_existing_file(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    for i in range(3):
        append_cost(path, CostRecord(
            ts=datetime(2026, 5, 7, 12, i, 0, tzinfo=timezone.utc),
            command="score",
            model="claude-opus-4-7",
            input_tokens=100, cached_input_tokens=0, output_tokens=50,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=0.01,
        ))
    records = read_cost_history(path)
    assert len(records) == 3


def test_running_total_for_command(tmp_path: Path):
    from mr.util.costs import running_total
    path = tmp_path / "costs.jsonl"
    for cmd, cost in [("discover", 0.10), ("score", 0.05), ("discover", 0.20)]:
        append_cost(path, CostRecord(
            ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc),
            command=cmd,
            model="claude-opus-4-7",
            input_tokens=0, cached_input_tokens=0, output_tokens=0,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
    assert running_total(path) == 0.35


def test_jsonl_format_one_object_per_line(tmp_path: Path):
    path = tmp_path / "costs.jsonl"
    append_cost(path, CostRecord(
        ts=datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc),
        command="discover", model="claude-opus-4-7",
        input_tokens=1, cached_input_tokens=0, output_tokens=1,
        cache_hits=0, cache_misses=0,
        code_execution_container_seconds=0.0, cost_usd=0.0001,
    ))
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["command"] == "discover"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/util/test_costs.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/util/costs.py`**

```python
"""costs.jsonl writer and reader for spend tracking.

Spec §10: one JSON object per line with cache_hits/cache_misses
(token counts), code_execution_container_seconds, and cost_usd.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CostRecord:
    ts: datetime
    command: str
    model: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cache_hits: int                       # cache_read_input_tokens from API response
    cache_misses: int                     # cache_creation_input_tokens from API response
    code_execution_container_seconds: float
    cost_usd: float


def append_cost(path: Path, rec: CostRecord) -> None:
    """Append a single cost record as a JSON line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(rec)
    payload["ts"] = rec.ts.isoformat()
    with path.open("a") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def read_cost_history(path: Path) -> list[CostRecord]:
    """Read all cost records from path. Returns empty list if file is missing."""
    if not path.exists():
        return []
    out: list[CostRecord] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        d["ts"] = datetime.fromisoformat(d["ts"])
        out.append(CostRecord(**d))
    return out


def running_total(path: Path, command: str | None = None) -> float:
    """Sum cost_usd across the cost history. Optionally filter by command."""
    records = read_cost_history(path)
    if command is not None:
        records = [r for r in records if r.command == command]
    return sum(r.cost_usd for r in records)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/util/test_costs.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/util/costs.py tests/util/test_costs.py
git commit -m "$(cat <<'EOF'
feat(util): costs.jsonl writer with running-total query

Implements CostRecord dataclass and append_cost/read_cost_history/
running_total per spec §10. Records cache_hits, cache_misses,
code_execution_container_seconds for budget tier-2 enforcement and
mr gain reporting.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 3: Lifecycle (paths, filename, frontmatter, transitions)

### Task 8: Lifecycle directory paths

**Spec sections:** §6 (lifecycle), §7 (mr init creates dirs), §10 (.moat-research/)

**Files:**
- Create: `mr/lifecycle/paths.py`
- Create: `tests/lifecycle/__init__.py`
- Create: `tests/lifecycle/test_paths.py`

- [ ] **Step 1: Write the failing tests**

`tests/lifecycle/test_paths.py`:

```python
from pathlib import Path

from mr.lifecycle.paths import (
    DISPOSITIONS,
    LIFECYCLE_DIRS,
    RepoLayout,
    disposition_for_dir,
)


def test_lifecycle_dir_set():
    assert LIFECYCLE_DIRS == ("candidates", "scored", "rejected", "approved", "graduated")


def test_dispositions_match_dirs():
    assert DISPOSITIONS == ("candidate", "scored", "rejected", "approved", "graduated")


def test_disposition_for_dir():
    assert disposition_for_dir("candidates") == "candidate"
    assert disposition_for_dir("scored") == "scored"
    assert disposition_for_dir("graduated") == "graduated"


def test_repo_layout(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    assert layout.root == tmp_path
    assert layout.candidates == tmp_path / "candidates"
    assert layout.scored == tmp_path / "scored"
    assert layout.rejected == tmp_path / "rejected"
    assert layout.approved == tmp_path / "approved"
    assert layout.graduated == tmp_path / "graduated"
    assert layout.state_dir == tmp_path / ".moat-research"
    assert layout.lock_path == tmp_path / ".moat-research" / "lock"
    assert layout.costs_path == tmp_path / ".moat-research" / "costs.jsonl"
    assert layout.seen_path == tmp_path / ".moat-research" / "seen.jsonl"
    assert layout.config_path == tmp_path / "mr.yaml"
    assert layout.wishlist_path == tmp_path / "WISHLIST.md"
    assert layout.prompts_dir == tmp_path / "prompts"


def test_repo_layout_ensure_dirs(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    for d in LIFECYCLE_DIRS:
        assert (tmp_path / d).is_dir()
    assert layout.state_dir.is_dir()
    assert layout.prompts_dir.is_dir()


def test_lifecycle_dirs_iter(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    paths = list(layout.lifecycle_dirs())
    assert len(paths) == 5
    assert paths[0] == tmp_path / "candidates"
    assert paths[-1] == tmp_path / "graduated"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/lifecycle/test_paths.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/lifecycle/paths.py`**

```python
"""Repo layout — lifecycle directory names and path resolution.

Spec §6 lifecycle: candidates → scored → {rejected, approved} → graduated.
Spec §10 state dir: .moat-research/{lock, costs.jsonl, seen.jsonl, cache/}.
Spec §12.1 disposition: closed set {candidate, scored, rejected, approved, graduated}.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

LIFECYCLE_DIRS: tuple[str, ...] = (
    "candidates",
    "scored",
    "rejected",
    "approved",
    "graduated",
)
"""Lifecycle directory names in canonical order (forward direction)."""

DISPOSITIONS: tuple[str, ...] = (
    "candidate",
    "scored",
    "rejected",
    "approved",
    "graduated",
)
"""seen.jsonl disposition values, parallel to LIFECYCLE_DIRS."""

_DIR_TO_DISPOSITION = dict(zip(LIFECYCLE_DIRS, DISPOSITIONS))


def disposition_for_dir(dirname: str) -> str:
    """Map a lifecycle dirname to its disposition string."""
    return _DIR_TO_DISPOSITION[dirname]


@dataclass
class RepoLayout:
    """Resolved file paths for a moat-research repo rooted at `root`."""

    root: Path

    @property
    def candidates(self) -> Path:
        return self.root / "candidates"

    @property
    def scored(self) -> Path:
        return self.root / "scored"

    @property
    def rejected(self) -> Path:
        return self.root / "rejected"

    @property
    def approved(self) -> Path:
        return self.root / "approved"

    @property
    def graduated(self) -> Path:
        return self.root / "graduated"

    @property
    def state_dir(self) -> Path:
        return self.root / ".moat-research"

    @property
    def lock_path(self) -> Path:
        return self.state_dir / "lock"

    @property
    def costs_path(self) -> Path:
        return self.state_dir / "costs.jsonl"

    @property
    def seen_path(self) -> Path:
        return self.state_dir / "seen.jsonl"

    @property
    def config_path(self) -> Path:
        return self.root / "mr.yaml"

    @property
    def wishlist_path(self) -> Path:
        return self.root / "WISHLIST.md"

    @property
    def prompts_dir(self) -> Path:
        return self.root / "prompts"

    def lifecycle_dirs(self) -> Iterator[Path]:
        """Yield the 5 lifecycle directories in canonical order."""
        for name in LIFECYCLE_DIRS:
            yield self.root / name

    def ensure_dirs(self) -> None:
        """Create all lifecycle dirs, the state dir, and the prompts dir."""
        for d in self.lifecycle_dirs():
            d.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/lifecycle/test_paths.py -v`
Expected: PASS for all 6 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/lifecycle/paths.py tests/lifecycle/__init__.py tests/lifecycle/test_paths.py
git commit -m "$(cat <<'EOF'
feat(lifecycle): RepoLayout + lifecycle dir constants

Implements RepoLayout dataclass + LIFECYCLE_DIRS / DISPOSITIONS
constants per spec §6 (lifecycle) and §10 (state dir). Provides
ensure_dirs() for mr init bootstrap and disposition_for_dir()
for seen.jsonl regeneration in §12.1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Filename convention

**Spec sections:** §6.1 (filename: `<composite_padded>-<yyyymmdd>-<slug>.md`; collision policy `-02, -03, …`)

**Files:**
- Create: `mr/lifecycle/filename.py`
- Create: `tests/lifecycle/test_filename.py`

- [ ] **Step 1: Write the failing tests**

`tests/lifecycle/test_filename.py`:

```python
from datetime import date
from pathlib import Path

import pytest

from mr.lifecycle.filename import (
    candidate_filename,
    composite_padded,
    parse_filename,
    resolve_collision,
    scored_filename,
)


def test_composite_padded_basic():
    assert composite_padded(7.221) == "07221"


def test_composite_padded_zero():
    assert composite_padded(0.0) == "00000"


def test_composite_padded_max():
    assert composite_padded(10.0) == "10000"


def test_composite_padded_rounds_half_to_nearest():
    # 7.2215 × 1000 = 7221.5 → banker's rounding goes either way; just check 5 digits
    assert len(composite_padded(7.2215)) == 5


def test_candidate_filename():
    assert candidate_filename(date(2026, 5, 7), "faa-notams") == "20260507-faa-notams.md"


def test_scored_filename():
    assert scored_filename(7.221, date(2026, 5, 7), "faa-notams") == "07221-20260507-faa-notams.md"


def test_scored_filename_auto_reject():
    assert scored_filename(0.0, date(2026, 5, 7), "bad-idea") == "00000-20260507-bad-idea.md"


def test_resolve_collision_no_collision(tmp_path: Path):
    target_dir = tmp_path
    name = "07221-20260507-foo.md"
    assert resolve_collision(target_dir, name) == name


def test_resolve_collision_appends_zero_padded_suffix(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    assert resolve_collision(target_dir, "07221-20260507-foo.md") == "07221-20260507-foo-02.md"


def test_resolve_collision_chains_to_03(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    (target_dir / "07221-20260507-foo-02.md").write_text("x")
    assert resolve_collision(target_dir, "07221-20260507-foo.md") == "07221-20260507-foo-03.md"


def test_resolve_collision_overflow_raises(tmp_path: Path):
    target_dir = tmp_path
    (target_dir / "07221-20260507-foo.md").write_text("x")
    for i in range(2, 100):
        (target_dir / f"07221-20260507-foo-{i:02d}.md").write_text("x")
    with pytest.raises(ValueError, match="collision"):
        resolve_collision(target_dir, "07221-20260507-foo.md")


def test_parse_scored_filename():
    parsed = parse_filename("07221-20260507-faa-notams.md")
    assert parsed.composite == 7.221
    assert parsed.date == date(2026, 5, 7)
    assert parsed.slug == "faa-notams"


def test_parse_candidate_filename():
    parsed = parse_filename("20260507-faa-notams.md")
    assert parsed.composite is None
    assert parsed.date == date(2026, 5, 7)
    assert parsed.slug == "faa-notams"


def test_parse_with_collision_suffix():
    parsed = parse_filename("07221-20260507-foo-02.md")
    assert parsed.slug == "foo"
    assert parsed.collision_suffix == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/lifecycle/test_filename.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/lifecycle/filename.py`**

```python
"""Filename convention for briefs.

Per spec §6.1:
- scored:    <composite_padded>-<yyyymmdd>-<slug>.md
- candidate: <yyyymmdd>-<slug>.md (no score yet)
- collision: append -02, -03, … (zero-padded to 2 digits, max 99)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_MAX_COLLISION = 99
_SCORED_RE = re.compile(
    r"^(?P<composite>\d{5})-"
    r"(?P<date>\d{8})-"
    r"(?P<slug>[a-z0-9-]+?)"
    r"(?:-(?P<suffix>\d{2}))?"
    r"\.md$"
)
_CANDIDATE_RE = re.compile(
    r"^(?P<date>\d{8})-"
    r"(?P<slug>[a-z0-9-]+?)"
    r"(?:-(?P<suffix>\d{2}))?"
    r"\.md$"
)


def composite_padded(composite: float) -> str:
    """Render a composite score as a 5-digit zero-padded integer (×1000)."""
    return f"{int(round(composite * 1000)):05d}"


def candidate_filename(date_created: date, slug: str) -> str:
    """Filename for a fresh candidate (no score yet)."""
    return f"{date_created:%Y%m%d}-{slug}.md"


def scored_filename(composite: float, date_created: date, slug: str) -> str:
    """Filename for a scored brief (or 00000- for auto-rejected)."""
    return f"{composite_padded(composite)}-{date_created:%Y%m%d}-{slug}.md"


def resolve_collision(target_dir: Path, desired_name: str) -> str:
    """Return a non-colliding filename in target_dir.

    If desired_name is free, returns it as-is. Otherwise appends -02, -03,
    ..., -99 to the base (before .md). Raises ValueError if overflow.
    """
    if not (target_dir / desired_name).exists():
        return desired_name

    base, _, ext = desired_name.rpartition(".md")
    base = base[:-1] if base.endswith("-") else base  # defensive

    # Strip trailing collision suffix if present so we re-suffix cleanly.
    base = re.sub(r"-\d{2}$", "", base)

    for n in range(2, _MAX_COLLISION + 1):
        candidate = f"{base}-{n:02d}.md"
        if not (target_dir / candidate).exists():
            return candidate

    raise ValueError(f"collision overflow: >{_MAX_COLLISION} duplicates of {desired_name}")


@dataclass
class ParsedFilename:
    composite: float | None        # None for candidate-stage filenames
    date: date
    slug: str
    collision_suffix: int | None   # 2-99, or None if no suffix


def parse_filename(name: str) -> ParsedFilename:
    """Parse a brief filename into composite, date, slug, and optional suffix."""
    m = _SCORED_RE.match(name)
    if m:
        return ParsedFilename(
            composite=int(m["composite"]) / 1000.0,
            date=_yyyymmdd(m["date"]),
            slug=m["slug"],
            collision_suffix=int(m["suffix"]) if m["suffix"] else None,
        )
    m = _CANDIDATE_RE.match(name)
    if m:
        return ParsedFilename(
            composite=None,
            date=_yyyymmdd(m["date"]),
            slug=m["slug"],
            collision_suffix=int(m["suffix"]) if m["suffix"] else None,
        )
    raise ValueError(f"unrecognized brief filename: {name!r}")


def _yyyymmdd(s: str) -> date:
    return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/lifecycle/test_filename.py -v`
Expected: PASS for all 13 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/lifecycle/filename.py tests/lifecycle/test_filename.py
git commit -m "$(cat <<'EOF'
feat(lifecycle): brief filename convention + collision resolution

Implements composite_padded, candidate_filename, scored_filename,
resolve_collision, and parse_filename per spec §6.1. Two-digit
zero-padded collision suffixes preserve ls -r ordering through up
to 99 duplicates. Parser handles both scored and candidate forms.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Frontmatter parse/write

**Spec sections:** §6.4 (brief frontmatter schema), §12.5 (niche_key host-computed)

**Files:**
- Create: `mr/lifecycle/frontmatter.py`
- Create: `tests/lifecycle/test_frontmatter.py`

- [ ] **Step 1: Write the failing tests**

`tests/lifecycle/test_frontmatter.py`:

```python
from datetime import date
from pathlib import Path

import pytest

from mr.lifecycle.frontmatter import (
    Brief,
    FrontmatterError,
    read_brief,
    write_brief,
    extract_thesis_first_sentence,
    source_set,
)


def _minimal_brief_yaml() -> str:
    return """---
schema_version: 1
title: FAA NOTAMs
slug: faa-notams
lane: ephemeral_public
niche: aviation alerts
niche_key: alerts_aviation
delivery_form: project
date_created: 2026-05-04
sources:
  - url: https://notams.aim.faa.gov/notamSearch
    role: primary
    archive_status: none
verification_evidence:
  - id: e1
    tool: wayback_check
    args: {url: "https://notams.aim.faa.gov/notamSearch"}
    result: {count: 47, first: "2023-04-12", last: "2026-04-30"}
  - id: e3
    tool: code_execution
    args: {code: "estimate_utilization()"}
    result: {peak_gpu_gb: 0, sustained_ram_gb: 4, storage_tb: 0.1}
disqualifier_verdicts:
  defensibility_threshold: n/a
  any_axis_zero: n/a
  single_source:
    verdict: pass
  unrestricted_archives:
    verdict: pass
    wayback_evidence_id: e1
    publisher_archive_evidence_id: null
  tos_redistribution:
    verdict: n/a
    evidence_id: null
  hardware_over_envelope:
    verdict: pass
    evidence_id: e3
---

# FAA NOTAMs

## Thesis
NOTAMs expire and are not archived by the FAA. Aggregating them creates a unique time-series corpus.

## Why this is a moat
Multi-year accumulation creates archive-history defensibility.

## Sources
| URL | role |
| --- | ---- |
| notams.aim.faa.gov | primary |

## Financial sketch
Aviation lawyers + enthusiast subscribers; ~$20k/yr.

## Implementation sketch
1-2 weeks to MVP.

## Hardware fit
4 GB GPU steady-state, well under envelope.

## Disqualifier check
All hard disqualifiers pass.
"""


def test_read_minimal_brief(tmp_path: Path):
    p = tmp_path / "20260504-faa-notams.md"
    p.write_text(_minimal_brief_yaml())
    b = read_brief(p)
    assert b.slug == "faa-notams"
    assert b.lane == "ephemeral_public"
    assert b.niche == "aviation alerts"
    assert b.niche_key == "alerts_aviation"
    assert b.delivery_form == "project"
    assert b.date_created == date(2026, 5, 4)
    assert len(b.sources) == 1
    assert b.sources[0]["role"] == "primary"
    assert b.scores is None  # not yet scored


def test_extract_thesis_first_sentence(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml())
    sentence = extract_thesis_first_sentence(p)
    assert sentence == "NOTAMs expire and are not archived by the FAA."


def test_source_set_dedups_by_host(tmp_path: Path):
    sources = [
        {"url": "https://example.com/a", "role": "primary"},
        {"url": "https://example.com/b", "role": "corroborating"},
        {"url": "https://other.com/x", "role": "corroborating"},
        {"url": "https://archive.org/wayback/example.com", "role": "counter_evidence"},
    ]
    s = source_set(sources)
    assert s == {"example.com", "other.com", "archive.org"}


def test_write_then_read_roundtrip(tmp_path: Path):
    p = tmp_path / "20260507-test.md"
    p.write_text(_minimal_brief_yaml())
    b = read_brief(p)

    p2 = tmp_path / "out.md"
    write_brief(p2, b, body="# Test\n\n## Thesis\nFoo bar.\n")
    b2 = read_brief(p2)
    assert b2.slug == b.slug
    assert b2.lane == b.lane


def test_invalid_lane_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("lane: ephemeral_public", "lane: bogus_lane"))
    with pytest.raises(FrontmatterError, match="lane"):
        read_brief(p)


def test_other_lane_requires_lane_note(tmp_path: Path):
    p = tmp_path / "x.md"
    yaml_text = _minimal_brief_yaml().replace("lane: ephemeral_public", "lane: other")
    # Missing lane_note for lane: other
    p.write_text(yaml_text)
    with pytest.raises(FrontmatterError, match="lane_note"):
        read_brief(p)


def test_missing_schema_version_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("schema_version: 1\n", ""))
    with pytest.raises(FrontmatterError, match="schema_version"):
        read_brief(p)


def test_unsupported_schema_version_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("schema_version: 1", "schema_version: 2"))
    with pytest.raises(FrontmatterError, match="schema_version"):
        read_brief(p)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/lifecycle/test_frontmatter.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/lifecycle/frontmatter.py`**

```python
"""Brief frontmatter parser, writer, and validator.

Spec §6.4 brief schema. Closed-set lane vocabulary (5 canonical + other).
schema_version 1 only (§15.2).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
_THESIS_RE = re.compile(r"##\s+Thesis\s*\n+(.+?)(?:\n##|\Z)", re.DOTALL)

LANES = frozenset({
    "ephemeral_public",
    "soon_to_be_restricted",
    "cross_source_fusion",
    "derived_artifact",
    "niche_vertical",
    "other",
})

DELIVERY_FORMS = frozenset({"project", "feature"})

SOURCE_ROLES = frozenset({"primary", "corroborating", "counter_evidence"})


class FrontmatterError(Exception):
    """Raised on invalid frontmatter content."""


@dataclass
class Brief:
    schema_version: int
    title: str
    slug: str
    lane: str
    niche: str
    niche_key: str
    delivery_form: str
    date_created: date
    sources: list[dict[str, Any]]
    verification_evidence: list[dict[str, Any]] = field(default_factory=list)
    disqualifier_verdicts: dict[str, Any] = field(default_factory=dict)
    scores: dict[str, Any] | None = None
    lane_note: str | None = None
    parent_project: str | None = None
    body: str = ""


def _parse_split(raw: str) -> tuple[dict[str, Any], str]:
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        raise FrontmatterError("missing or malformed YAML frontmatter")
    fm_text, body = m.group(1), m.group(2)
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return fm, body


def _validate(fm: dict[str, Any]) -> None:
    if fm.get("schema_version") != 1:
        raise FrontmatterError(
            f"unsupported schema_version {fm.get('schema_version')!r} (v1 only)"
        )
    for required in ("title", "slug", "lane", "niche", "niche_key", "delivery_form", "date_created", "sources"):
        if required not in fm:
            raise FrontmatterError(f"missing required key: {required}")

    if fm["lane"] not in LANES:
        raise FrontmatterError(f"lane {fm['lane']!r} not in {sorted(LANES)}")
    if fm["lane"] == "other" and not fm.get("lane_note"):
        raise FrontmatterError("lane: other requires lane_note")

    if fm["delivery_form"] not in DELIVERY_FORMS:
        raise FrontmatterError(f"delivery_form {fm['delivery_form']!r} not in {sorted(DELIVERY_FORMS)}")
    if fm["delivery_form"] == "feature" and not fm.get("parent_project"):
        raise FrontmatterError("delivery_form: feature requires parent_project")

    for s in fm["sources"]:
        if s.get("role") not in SOURCE_ROLES:
            raise FrontmatterError(f"source role {s.get('role')!r} not in {sorted(SOURCE_ROLES)}")


def read_brief(path: Path) -> Brief:
    """Parse a brief markdown file. Raises FrontmatterError on schema violation."""
    raw = path.read_text()
    fm, body = _parse_split(raw)
    _validate(fm)

    return Brief(
        schema_version=fm["schema_version"],
        title=fm["title"],
        slug=fm["slug"],
        lane=fm["lane"],
        niche=fm["niche"],
        niche_key=fm["niche_key"],
        delivery_form=fm["delivery_form"],
        date_created=fm["date_created"] if isinstance(fm["date_created"], date) else date.fromisoformat(str(fm["date_created"])),
        sources=fm["sources"],
        verification_evidence=fm.get("verification_evidence", []),
        disqualifier_verdicts=fm.get("disqualifier_verdicts", {}),
        scores=fm.get("scores"),
        lane_note=fm.get("lane_note"),
        parent_project=fm.get("parent_project"),
        body=body,
    )


def write_brief(path: Path, brief: Brief, body: str | None = None) -> None:
    """Write a brief to disk with frontmatter + body."""
    fm: dict[str, Any] = {
        "schema_version": brief.schema_version,
        "title": brief.title,
        "slug": brief.slug,
        "lane": brief.lane,
        "niche": brief.niche,
        "niche_key": brief.niche_key,
        "delivery_form": brief.delivery_form,
        "date_created": brief.date_created.isoformat(),
        "sources": brief.sources,
        "verification_evidence": brief.verification_evidence,
        "disqualifier_verdicts": brief.disqualifier_verdicts,
    }
    if brief.lane_note:
        fm["lane_note"] = brief.lane_note
    if brief.parent_project:
        fm["parent_project"] = brief.parent_project
    if brief.scores:
        fm["scores"] = brief.scores

    fm_text = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False)
    body_text = body if body is not None else brief.body
    path.write_text(f"---\n{fm_text}---\n{body_text}")


def extract_thesis_first_sentence(path: Path) -> str:
    """Pull the first sentence from the brief's `## Thesis` body section."""
    raw = path.read_text()
    _, body = _parse_split(raw)
    m = _THESIS_RE.search(body)
    if not m:
        return ""
    para = m.group(1).strip().split("\n")[0].strip()
    # Split on '. ' for sentence boundary; keep terminal punctuation.
    if "." in para:
        first = para.split(".")[0].strip() + "."
        return first
    return para


def source_set(sources: list[dict[str, Any]]) -> set[str]:
    """Distinct hostnames across all sources (any role)."""
    out: set[str] = set()
    for s in sources:
        url = s.get("url", "")
        if not url:
            continue
        host = urlparse(url).hostname
        if host:
            out.add(host)
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/lifecycle/test_frontmatter.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/lifecycle/frontmatter.py tests/lifecycle/test_frontmatter.py
git commit -m "$(cat <<'EOF'
feat(lifecycle): brief frontmatter parser, writer, validator

Implements Brief dataclass, read_brief, write_brief, source_set,
extract_thesis_first_sentence per spec §6.4 schema. Validates closed
sets (lane, delivery_form, source role), lane: other requires
lane_note, delivery_form: feature requires parent_project, schema_version
must be 1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: Atomic transitions (os.replace moves)

**Spec sections:** §6.2 (transitions table), §12.1 (atomic moves via os.replace)

**Files:**
- Create: `mr/lifecycle/transitions.py`
- Create: `tests/lifecycle/test_transitions.py`

- [ ] **Step 1: Write the failing tests**

`tests/lifecycle/test_transitions.py`:

```python
from pathlib import Path

import pytest

from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def _make_brief(path: Path, content: str = "---\nschema_version: 1\n---\n# x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_move_candidate_to_scored(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout.candidates / "20260507-foo.md")

    dst = layout.scored / "07221-20260507-foo.md"
    move_brief(src, dst)
    assert not src.exists()
    assert dst.exists()


def test_move_to_existing_dest_raises(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout.candidates / "20260507-foo.md")
    existing = _make_brief(layout.scored / "07221-20260507-foo.md", content="existing")

    with pytest.raises(TransitionError, match="already exists"):
        move_brief(src, existing)
    assert src.exists()  # source untouched on failure
    assert existing.read_text() == "existing"  # dest untouched


def test_move_creates_dest_parent_if_missing(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    src = tmp_path / "candidates" / "20260507-foo.md"
    _make_brief(src)
    dst = tmp_path / "scored" / "07221-20260507-foo.md"
    # scored/ doesn't exist yet
    move_brief(src, dst)
    assert dst.exists()


def test_move_missing_source_raises(tmp_path: Path):
    src = tmp_path / "absent.md"
    dst = tmp_path / "out.md"
    with pytest.raises(TransitionError, match="not found"):
        move_brief(src, dst)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/lifecycle/test_transitions.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/lifecycle/transitions.py`**

```python
"""Atomic lifecycle transitions via os.replace.

Spec §6.2 (transitions table) + §12.1 (atomicity contract).
"""
from __future__ import annotations

import os
from pathlib import Path


class TransitionError(Exception):
    """Raised when a brief move cannot proceed safely."""


def move_brief(src: Path, dst: Path) -> None:
    """Atomically move src to dst. Refuses to overwrite an existing dest.

    Creates dst's parent directory if missing. Source must exist.
    Uses os.replace (atomic on POSIX same-filesystem renames).
    """
    if not src.exists():
        raise TransitionError(f"source not found: {src}")
    if dst.exists():
        raise TransitionError(f"destination already exists: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dst)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/lifecycle/test_transitions.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/lifecycle/transitions.py tests/lifecycle/test_transitions.py
git commit -m "$(cat <<'EOF'
feat(lifecycle): atomic move_brief helper using os.replace

Implements move_brief() per spec §6.2 transitions and §12.1
atomicity contract. Refuses to overwrite existing dest (collision
must be resolved before calling). Creates parent dir lazily.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 4: Scoring (rubric, auto-reject)

### Task 12: 4-axis weighted geometric mean composite

**Spec sections:** §5 (rubric formula), §5.6 (sensitivity)

**Files:**
- Create: `mr/scoring/rubric.py`
- Create: `tests/scoring/__init__.py`
- Create: `tests/scoring/test_rubric.py`

- [ ] **Step 1: Write the failing tests**

`tests/scoring/test_rubric.py`:

```python
import math

import pytest

from mr.scoring.rubric import Scores, composite, default_weights


def test_default_weights_sum_to_one():
    w = default_weights()
    assert math.isclose(sum(w.values()), 1.0)


def test_all_tens_gives_ten():
    s = Scores(defensibility=10, financial=10, implementation=10, hardware=10)
    assert math.isclose(composite(s), 10.0, rel_tol=1e-6)


def test_all_zeros_gives_zero():
    s = Scores(defensibility=0, financial=0, implementation=0, hardware=0)
    assert composite(s) == 0.0


def test_any_axis_zero_zeros_composite():
    s = Scores(defensibility=10, financial=0, implementation=10, hardware=10)
    assert composite(s) == 0.0


def test_d5_others10_around_785():
    s = Scores(defensibility=5, financial=10, implementation=10, hardware=10)
    assert math.isclose(composite(s), 7.847, abs_tol=0.01)


def test_d10_others5_around_637():
    s = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    assert math.isclose(composite(s), 6.372, abs_tol=0.01)


def test_d5_others10_ranks_above_d10_others5():
    a = Scores(defensibility=5, financial=10, implementation=10, hardware=10)
    b = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    assert composite(a) > composite(b)


def test_custom_weights_override_default():
    s = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    custom = {"defensibility": 0.50, "financial": 0.20, "implementation": 0.15, "hardware": 0.15}
    # With heavy defensibility weight, the d=10 case should jump
    val = composite(s, weights=custom)
    assert val > 6.5  # should now be ~6.69


def test_invalid_score_outside_range_raises():
    with pytest.raises(ValueError):
        composite(Scores(defensibility=11, financial=5, implementation=5, hardware=5))
    with pytest.raises(ValueError):
        composite(Scores(defensibility=-1, financial=5, implementation=5, hardware=5))


def test_weights_must_sum_to_one():
    s = Scores(defensibility=5, financial=5, implementation=5, hardware=5)
    with pytest.raises(ValueError, match="weights"):
        composite(s, weights={"defensibility": 0.5, "financial": 0.5, "implementation": 0.5, "hardware": 0.5})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/scoring/test_rubric.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/scoring/rubric.py`**

```python
"""4-axis weighted geometric mean composite.

Spec §5: composite = d^0.35 × f^0.30 × i^0.20 × h^0.15.
Per-axis elasticity equals weight (§5.6).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Scores:
    defensibility: float
    financial: float
    implementation: float
    hardware: float


def default_weights() -> dict[str, float]:
    """Spec §5 default weights."""
    return {
        "defensibility": 0.35,
        "financial": 0.30,
        "implementation": 0.20,
        "hardware": 0.15,
    }


def composite(scores: Scores, weights: dict[str, float] | None = None) -> float:
    """Compute the weighted geometric mean composite score.

    Returns 0.0 if any axis is 0 (consistent with §5.5 auto-reject force-to-0).
    Raises ValueError if scores are outside [0, 10] or weights don't sum to 1.
    """
    w = weights or default_weights()

    if not math.isclose(sum(w.values()), 1.0, abs_tol=1e-6):
        raise ValueError(f"weights must sum to 1.0; got {sum(w.values())}")

    axes = {
        "defensibility": scores.defensibility,
        "financial": scores.financial,
        "implementation": scores.implementation,
        "hardware": scores.hardware,
    }

    for name, val in axes.items():
        if val < 0 or val > 10:
            raise ValueError(f"{name} score {val} outside [0, 10]")

    if any(v == 0 for v in axes.values()):
        return 0.0

    out = 1.0
    for name, val in axes.items():
        out *= val ** w[name]
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/scoring/test_rubric.py -v`
Expected: PASS for all 10 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/scoring/rubric.py tests/scoring/__init__.py tests/scoring/test_rubric.py
git commit -m "$(cat <<'EOF'
feat(scoring): 4-axis weighted geometric mean composite

Implements Scores dataclass and composite() per spec §5. Validates
weights sum to 1.0 and scores ∈ [0, 10]. Verifies the documented
sensitivity examples in §5.6: d=5+others=10 (7.85) > d=10+others=5
(6.37). Custom weights via mr.yaml override defaults.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 13: Auto-reject decisions + reason strings

**Spec sections:** §5.5 (auto-reject normative table), §6.4 (predicates)

**Files:**
- Create: `mr/scoring/auto_reject.py`
- Create: `tests/scoring/test_auto_reject.py`

- [ ] **Step 1: Write the failing tests**

`tests/scoring/test_auto_reject.py`:

```python
import pytest

from mr.scoring.auto_reject import (
    AutoRejectReason,
    REASON_STRINGS,
    SEVERITY_TIERS,
    decide_floor_rejection,
    severity_tier,
)
from mr.scoring.rubric import Scores


def test_reason_strings_are_normative():
    # Match spec §5.5 normative table verbatim
    assert REASON_STRINGS[AutoRejectReason.DEFENSIBILITY_LOW] == "defensibility ≤ 4"
    assert REASON_STRINGS[AutoRejectReason.AXIS_ZERO] == "any axis = 0"
    assert REASON_STRINGS[AutoRejectReason.SINGLE_SOURCE] == "single source"
    assert REASON_STRINGS[AutoRejectReason.UNRESTRICTED_ARCHIVES] == "unrestricted archives"
    assert REASON_STRINGS[AutoRejectReason.TOS_PROHIBITS] == "TOS prohibits redistribution"
    assert REASON_STRINGS[AutoRejectReason.HARDWARE_OVER] == "hardware over envelope"
    assert REASON_STRINGS[AutoRejectReason.MISSING_HW_KEYS] == "code_execution result missing required hardware keys"
    assert REASON_STRINGS[AutoRejectReason.FABRICATION] == "claimed verdict inconsistent with cited evidence"


def test_decide_floor_rejection_low_defensibility():
    s = Scores(defensibility=4, financial=10, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.DEFENSIBILITY_LOW


def test_decide_floor_rejection_axis_zero():
    s = Scores(defensibility=10, financial=0, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.AXIS_ZERO


def test_decide_floor_rejection_defensibility_priority():
    # When both d≤4 AND axis=0, defensibility takes priority (spec §5.5 order)
    s = Scores(defensibility=3, financial=0, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.DEFENSIBILITY_LOW


def test_decide_floor_rejection_passes():
    s = Scores(defensibility=5, financial=5, implementation=5, hardware=5)
    assert decide_floor_rejection(s) is None


def test_severity_tier_classification():
    assert severity_tier("single source") == 1
    assert severity_tier("unrestricted archives") == 1
    assert severity_tier("TOS prohibits redistribution") == 1
    assert severity_tier("hardware over envelope") == 1
    assert severity_tier("code_execution result missing required hardware keys") == 1
    assert severity_tier("claimed verdict inconsistent with cited evidence") == 1
    assert severity_tier("defensibility ≤ 4") == 2
    assert severity_tier("any axis = 0") == 2
    assert severity_tier("manual: not the right time") == 3
    assert severity_tier("manual: bad fit") == 3


def test_severity_tier_unknown_string_returns_none():
    assert severity_tier("some other reason") is None


def test_severity_tiers_are_complete():
    # Every named reason has a tier assignment
    for reason in AutoRejectReason:
        assert reason in SEVERITY_TIERS
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/scoring/test_auto_reject.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/scoring/auto_reject.py`**

```python
"""Auto-reject decisions and the §5.5 normative reason-string table.

Spec §5.5 (auto-reject conditions + normative strings + severity tiers)
and §13.3 (severity tiers consumed by adjacent-rejection appendix).
"""
from __future__ import annotations

from enum import Enum

from mr.scoring.rubric import Scores


class AutoRejectReason(Enum):
    DEFENSIBILITY_LOW = "defensibility_low"
    AXIS_ZERO = "axis_zero"
    SINGLE_SOURCE = "single_source"
    UNRESTRICTED_ARCHIVES = "unrestricted_archives"
    TOS_PROHIBITS = "tos_prohibits"
    HARDWARE_OVER = "hardware_over"
    MISSING_HW_KEYS = "missing_hw_keys"
    FABRICATION = "fabrication"


# Spec §5.5 normative table — these strings are stored in scores.auto_reject_reason
# and referenced by §13.3 severity classification. DO NOT change the strings without
# also updating the spec.
REASON_STRINGS: dict[AutoRejectReason, str] = {
    AutoRejectReason.DEFENSIBILITY_LOW: "defensibility ≤ 4",
    AutoRejectReason.AXIS_ZERO: "any axis = 0",
    AutoRejectReason.SINGLE_SOURCE: "single source",
    AutoRejectReason.UNRESTRICTED_ARCHIVES: "unrestricted archives",
    AutoRejectReason.TOS_PROHIBITS: "TOS prohibits redistribution",
    AutoRejectReason.HARDWARE_OVER: "hardware over envelope",
    AutoRejectReason.MISSING_HW_KEYS: "code_execution result missing required hardware keys",
    AutoRejectReason.FABRICATION: "claimed verdict inconsistent with cited evidence",
}


# Spec §13.3 severity tiers (after pass-6 merge of tier 4 into tier 1)
# Tier 1: hard-disqualifier rejections + missing-hw-keys + fabrication
# Tier 2: floor rejections (defensibility, axis-zero)
# Tier 3: manual rejections (string starting with "manual: ")
SEVERITY_TIERS: dict[AutoRejectReason, int] = {
    AutoRejectReason.SINGLE_SOURCE: 1,
    AutoRejectReason.UNRESTRICTED_ARCHIVES: 1,
    AutoRejectReason.TOS_PROHIBITS: 1,
    AutoRejectReason.HARDWARE_OVER: 1,
    AutoRejectReason.MISSING_HW_KEYS: 1,
    AutoRejectReason.FABRICATION: 1,
    AutoRejectReason.DEFENSIBILITY_LOW: 2,
    AutoRejectReason.AXIS_ZERO: 2,
}


def decide_floor_rejection(scores: Scores) -> AutoRejectReason | None:
    """Return the auto-reject reason if scores trigger §5.5 floor; else None.

    Defensibility ≤ 4 takes priority over any-axis-zero per spec §5.5
    enumeration order.
    """
    if scores.defensibility <= 4:
        return AutoRejectReason.DEFENSIBILITY_LOW
    if any(s == 0 for s in (
        scores.defensibility, scores.financial, scores.implementation, scores.hardware
    )):
        return AutoRejectReason.AXIS_ZERO
    return None


# Reverse map for severity_tier(): reason string → tier
_STRING_TO_TIER: dict[str, int] = {
    REASON_STRINGS[r]: SEVERITY_TIERS[r] for r in AutoRejectReason
}


def severity_tier(reason: str | None) -> int | None:
    """Map an auto_reject_reason string to its severity tier (1-3) per §13.3.

    Returns None if the string is unrecognized. Manual rejections with the
    "manual: " prefix return tier 3.
    """
    if reason is None:
        return None
    if reason.startswith("manual: "):
        return 3
    return _STRING_TO_TIER.get(reason)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/scoring/test_auto_reject.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/scoring/auto_reject.py tests/scoring/test_auto_reject.py
git commit -m "$(cat <<'EOF'
feat(scoring): auto-reject decisions + §5.5 normative reason strings

Implements AutoRejectReason enum with the spec §5.5 normative
auto_reject_reason strings, decide_floor_rejection() for the
defensibility-≤4 / any-axis-zero check, and severity_tier() mapping
strings to §13.3 tiers (1-3) after the pass-6 merge of tier 4 into
tier 1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 5: Dedup (niche_key, seen.jsonl, summary)

### Task 14: niche_key normalization

**Spec sections:** §6.4 (niche_key host-computed), §12.5 (alias resolution at regen time), §9 (niche_aliases schema)

**Files:**
- Create: `mr/dedup/niche_key.py`
- Create: `tests/dedup/__init__.py`
- Create: `tests/dedup/test_niche_key.py`

- [ ] **Step 1: Write the failing tests**

`tests/dedup/test_niche_key.py`:

```python
from mr.dedup.niche_key import normalize_niche, resolve_niche_key


def test_lowercase():
    assert normalize_niche("Aviation Alerts") == "alerts_aviation"


def test_strips_punctuation_and_collapses_whitespace():
    assert normalize_niche("Aviation, alerts!") == "alerts_aviation"


def test_sorts_tokens_alphabetically():
    assert normalize_niche("Real-Time Cameras") == "cameras_real_time"


def test_unicode_to_ascii():
    assert normalize_niche("Café Münchéñ") == "cafe_munchen"


def test_empty_input_returns_fallback():
    assert normalize_niche("") == "untagged"
    assert normalize_niche("!!!") == "untagged"


def test_alias_resolution_maps_to_canonical():
    aliases = {"alerts_aviation": ["aviation alerts", "FAA aviation", "aviation"]}
    assert resolve_niche_key("aviation alerts", aliases) == "alerts_aviation"
    assert resolve_niche_key("FAA aviation", aliases) == "alerts_aviation"
    assert resolve_niche_key("aviation", aliases) == "alerts_aviation"


def test_alias_resolution_falls_through_when_no_match():
    aliases = {"alerts_aviation": ["aviation alerts"]}
    assert resolve_niche_key("court records", aliases) == "court_records"


def test_alias_resolution_normalizes_alias_input():
    # Aliases are matched against the normalized niche, not the raw string
    aliases = {"alerts_aviation": ["aviation alerts"]}
    assert resolve_niche_key("AVIATION ALERTS!!!", aliases) == "alerts_aviation"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/dedup/test_niche_key.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/dedup/niche_key.py`**

```python
"""niche_key normalization with alias resolution.

Spec §6.4: niche_key = lowercase, alphanumerics+underscore, tokens sorted alphabetically.
Spec §12.5: aliases resolve at seen.jsonl regen time using current mr.yaml.
"""
from __future__ import annotations

import re
import unicodedata

_FALLBACK = "untagged"


def normalize_niche(text: str) -> str:
    """Canonicalize a free-text niche tag into a stable key.

    Rules:
    - NFKD normalize + strip non-ASCII
    - lowercase
    - non-alphanumeric → underscore
    - collapse repeated underscores
    - split on underscore, sort tokens alphabetically, rejoin with `_`
    - empty → "untagged"
    """
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")

    if not normalized:
        return _FALLBACK

    tokens = [t for t in normalized.split("_") if t]
    tokens.sort()
    return "_".join(tokens) or _FALLBACK


def resolve_niche_key(niche: str, aliases: dict[str, list[str]]) -> str:
    """Compute the canonical niche_key, applying aliases from mr.yaml.

    `aliases` maps canonical key → list of synonym strings (the synonyms
    are matched after normalization). If the input's normalized form
    matches a synonym, the canonical key is returned; otherwise the
    normalized form itself is returned.
    """
    normalized = normalize_niche(niche)
    for canonical, synonyms in aliases.items():
        for syn in synonyms:
            if normalize_niche(syn) == normalized:
                return canonical
    return normalized
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/dedup/test_niche_key.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/dedup/niche_key.py tests/dedup/__init__.py tests/dedup/test_niche_key.py
git commit -m "$(cat <<'EOF'
feat(dedup): niche_key normalization with alias resolution

Implements normalize_niche() (NFKD → ASCII → lowercase →
alphanumerics+underscore → token-sort) and resolve_niche_key()
(applies mr.yaml: niche_aliases). Per spec §6.4 and §12.5 — aliases
resolve at regen time so editing the alias map retroactively
re-buckets old briefs.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 15: seen.jsonl regeneration with atomic write + lifecycle-violation detection

**Spec sections:** §12.1 (canonical artifact, atomicity, recovery rules)

**Files:**
- Create: `mr/dedup/seen.py`
- Create: `tests/dedup/test_seen.py`

- [ ] **Step 1: Write the failing tests**

`tests/dedup/test_seen.py`:

```python
import json
import os
import time
from datetime import date
from pathlib import Path

import pytest

from mr.dedup.seen import (
    LifecycleViolation,
    SeenEntry,
    is_stale,
    read_seen,
    regenerate_seen,
)
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout


def _make_brief(layout: RepoLayout, dirname: str, slug: str, niche: str = "aviation alerts") -> Path:
    target = layout.root / dirname
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"20260507-{slug}.md"
    brief = Brief(
        schema_version=1,
        title=slug,
        slug=slug,
        lane="ephemeral_public",
        niche=niche,
        niche_key="alerts_aviation",
        delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": f"https://{slug}.example.com/", "role": "primary", "archive_status": "none"}],
    )
    body = f"# {slug}\n\n## Thesis\n{slug} thesis sentence.\n"
    write_brief(path, brief, body=body)
    return path


def test_regenerate_empty_repo(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    regenerate_seen(layout, niche_aliases={})
    entries = read_seen(layout.seen_path)
    assert entries == []


def test_regenerate_with_one_brief(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    entries = read_seen(layout.seen_path)
    assert len(entries) == 1
    assert entries[0].slug == "foo"
    assert entries[0].disposition == "candidate"
    assert entries[0].source_set == ["foo.example.com"]
    assert entries[0].auto_reject_reason is None


def test_regenerate_recomputes_niche_key_from_aliases(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    p = _make_brief(layout, "candidates", "foo", niche="aviation alerts")
    aliases = {"new_canonical_key": ["aviation alerts"]}
    regenerate_seen(layout, niche_aliases=aliases)
    entries = read_seen(layout.seen_path)
    assert entries[0].niche_key == "new_canonical_key"


def test_partial_move_recovery(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout, "candidates", "foo")
    # Simulate partial move: copy to scored/ with newer mtime
    dst = layout.scored / "07221-20260507-foo.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text())
    # Make dst newer than src
    now = time.time()
    os.utime(src, (now - 30, now - 30))
    os.utime(dst, (now, now))

    regenerate_seen(layout, niche_aliases={})
    # Recovery: dst (forward) kept, src (earlier) deleted
    assert dst.exists()
    assert not src.exists()


def test_operator_error_fallback_cp_in_candidates(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    src = _make_brief(layout, "candidates", "foo")
    # Simulate cp from scored/: candidates/ copy is newer
    dst = layout.scored / "07221-20260507-foo.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text())
    now = time.time()
    os.utime(dst, (now - 30, now - 30))
    os.utime(src, (now, now))

    regenerate_seen(layout, niche_aliases={})
    # Both copies left alone for operator's mr score to consume.
    assert src.exists()
    assert dst.exists()
    # seen.jsonl records candidates/ as canonical disposition
    entries = read_seen(layout.seen_path)
    assert len(entries) == 1
    assert entries[0].disposition == "candidate"


def test_unrelated_branches_fatal(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    a = _make_brief(layout, "rejected", "foo")
    b = layout.approved / "08412-20260507-foo.md"
    b.parent.mkdir(parents=True, exist_ok=True)
    b.write_text(a.read_text())

    with pytest.raises(LifecycleViolation, match="rejected.*approved|approved.*rejected"):
        regenerate_seen(layout, niche_aliases={})


def test_atomic_write_via_tmp(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    # No leftover .tmp files
    assert not any(p.name.endswith(".tmp") for p in layout.state_dir.iterdir())


def test_is_stale_when_seen_missing(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    assert is_stale(layout) is True


def test_is_stale_when_dir_mtime_newer(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    layout.seen_path.write_text("")
    old = time.time() - 100
    os.utime(layout.seen_path, (old, old))
    # Touch a lifecycle dir to update mtime
    _make_brief(layout, "candidates", "foo")
    assert is_stale(layout) is True


def test_is_stale_false_when_seen_newer(tmp_path: Path):
    layout = RepoLayout(tmp_path)
    layout.ensure_dirs()
    _make_brief(layout, "candidates", "foo")
    regenerate_seen(layout, niche_aliases={})
    assert is_stale(layout) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/dedup/test_seen.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/dedup/seen.py`**

```python
"""seen.jsonl canonical dedup artifact.

Spec §12.1: regenerated when stale (dir mtime > artifact mtime).
Lifecycle-violation recovery: partial-move artifacts auto-heal,
operator-error (cp instead of mv) leaves duplicates alone, unrelated
branches abort fatally.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mr.dedup.niche_key import resolve_niche_key
from mr.lifecycle.filename import parse_filename
from mr.lifecycle.frontmatter import extract_thesis_first_sentence, read_brief, source_set
from mr.lifecycle.paths import LIFECYCLE_DIRS, RepoLayout, disposition_for_dir

# §12.1: forward-direction order of lifecycle dirs (canonical chain)
_FORWARD_ORDER = list(LIFECYCLE_DIRS)
_DIR_INDEX = {name: i for i, name in enumerate(_FORWARD_ORDER)}

# Adjacent pairs along the canonical chain (for partial-move recovery)
_ADJACENT_PAIRS = {
    frozenset({"candidates", "scored"}),
    frozenset({"candidates", "rejected"}),
    frozenset({"scored", "rejected"}),
    frozenset({"scored", "approved"}),
    frozenset({"approved", "graduated"}),
}

_PARTIAL_MOVE_MTIME_DELTA_SECONDS = 60.0


class LifecycleViolation(Exception):
    """Raised when same slug appears in unrelated lifecycle branches."""


@dataclass
class SeenEntry:
    slug: str
    lane: str
    niche: str
    niche_key: str
    thesis: str
    source_set: list[str]              # sorted list for stable JSON
    disposition: str
    auto_reject_reason: str | None
    date_created: str                  # ISO yyyy-mm-dd

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "lane": self.lane,
            "niche": self.niche,
            "niche_key": self.niche_key,
            "thesis": self.thesis,
            "source_set": self.source_set,
            "disposition": self.disposition,
            "auto_reject_reason": self.auto_reject_reason,
            "date_created": self.date_created,
        }


def is_stale(layout: RepoLayout) -> bool:
    """True iff seen.jsonl is missing or older than any lifecycle dir mtime."""
    if not layout.seen_path.exists():
        return True
    seen_mtime = layout.seen_path.stat().st_mtime
    for d in layout.lifecycle_dirs():
        if not d.exists():
            continue
        if d.stat().st_mtime > seen_mtime:
            return True
    return False


def regenerate_seen(layout: RepoLayout, niche_aliases: dict[str, list[str]]) -> None:
    """Walk all lifecycle dirs, rebuild seen.jsonl atomically.

    Applies §12.1 recovery rules to handle duplicate slugs:
    - Adjacent dirs + forward-newer → keep forward, delete earlier.
    - Adjacent dirs + earlier-newer (candidates/ newer) → leave alone.
    - Non-adjacent dirs → raise LifecycleViolation.
    """
    by_slug: dict[str, list[tuple[Path, str]]] = {}
    for d in layout.lifecycle_dirs():
        if not d.exists():
            continue
        for f in d.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            try:
                parsed = parse_filename(f.name)
            except ValueError:
                continue
            by_slug.setdefault(parsed.slug, []).append((f, d.name))

    entries: list[SeenEntry] = []

    for slug, copies in by_slug.items():
        if len(copies) == 1:
            path, dirname = copies[0]
            entries.append(_brief_to_entry(path, dirname, niche_aliases))
            continue

        # Duplicate slug — apply §12.1 recovery rules
        chosen = _resolve_duplicate(slug, copies)
        path, dirname = chosen
        entries.append(_brief_to_entry(path, dirname, niche_aliases))

    _atomic_write(layout.seen_path, entries)


def _resolve_duplicate(slug: str, copies: list[tuple[Path, str]]) -> tuple[Path, str]:
    """§12.1 recovery decision. Returns the (path, dirname) to use as canonical.

    Side effect: deletes the earlier copy on partial-move recovery.
    Raises LifecycleViolation for unrelated-branch duplicates.
    """
    if len(copies) > 2:
        dirs = sorted({d for _, d in copies})
        raise LifecycleViolation(
            f"slug {slug!r} appears in {len(copies)} dirs: {dirs}"
        )

    (path_a, dir_a), (path_b, dir_b) = copies
    pair_set = frozenset({dir_a, dir_b})

    if pair_set not in _ADJACENT_PAIRS:
        raise LifecycleViolation(
            f"slug {slug!r} in unrelated branches {dir_a!r} and {dir_b!r} — "
            f"requires manual resolution via mr doctor (deferred to §15.2)"
        )

    # Identify the forward-direction dir
    forward, earlier = (dir_b, dir_a) if _DIR_INDEX[dir_b] > _DIR_INDEX[dir_a] else (dir_a, dir_b)
    forward_path = path_b if forward == dir_b else path_a
    earlier_path = path_a if forward == dir_b else path_b

    fwd_mtime = forward_path.stat().st_mtime
    ear_mtime = earlier_path.stat().st_mtime

    if forward == "candidates":
        # Should be impossible given _ADJACENT_PAIRS construction
        return forward_path, forward

    if fwd_mtime >= ear_mtime and (fwd_mtime - ear_mtime) <= _PARTIAL_MOVE_MTIME_DELTA_SECONDS:
        # Partial-move artifact: keep forward, delete earlier
        earlier_path.unlink()
        return forward_path, forward

    # Operator-error fallback: candidates/ newer → leave alone, record candidates/ as canonical
    if earlier == "candidates" and ear_mtime > fwd_mtime:
        return earlier_path, earlier

    # Anything else with mtime delta > 60s: fatal
    raise LifecycleViolation(
        f"slug {slug!r} duplicate in {dir_a!r} and {dir_b!r} with mtime "
        f"delta {abs(fwd_mtime - ear_mtime):.0f}s — requires manual resolution"
    )


def _brief_to_entry(path: Path, dirname: str, niche_aliases: dict[str, list[str]]) -> SeenEntry:
    brief = read_brief(path)
    return SeenEntry(
        slug=brief.slug,
        lane=brief.lane,
        niche=brief.niche,
        niche_key=resolve_niche_key(brief.niche, niche_aliases),
        thesis=extract_thesis_first_sentence(path),
        source_set=sorted(source_set(brief.sources)),
        disposition=disposition_for_dir(dirname),
        auto_reject_reason=(brief.scores or {}).get("auto_reject_reason") if dirname == "rejected" else None,
        date_created=brief.date_created.isoformat(),
    )


def _atomic_write(path: Path, entries: list[SeenEntry]) -> None:
    """Write seen.jsonl via tmpfile + os.replace for atomicity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".seen.", suffix=".jsonl.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            for e in entries:
                f.write(json.dumps(e.to_json_obj(), separators=(",", ":")) + "\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def read_seen(path: Path) -> list[SeenEntry]:
    """Read seen.jsonl. Returns empty list if absent."""
    if not path.exists():
        return []
    entries: list[SeenEntry] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        entries.append(SeenEntry(**d))
    return entries
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/dedup/test_seen.py -v`
Expected: PASS for all 9 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/dedup/seen.py tests/dedup/test_seen.py
git commit -m "$(cat <<'EOF'
feat(dedup): seen.jsonl regen with atomic write and §12.1 recovery

Implements is_stale (dir-mtime check, since os.replace preserves
file mtime), regenerate_seen with partial-move auto-recovery,
operator-error (cp) fallback, and unrelated-branch fatal abort.
Atomic writes via tmpfile + os.replace.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 16: Pre-pended summary block (bounded ~3k tokens)

**Spec sections:** §12.2 (bounded summary), §8.4.1 (other-lane treatment)

**Files:**
- Create: `mr/dedup/summary.py`
- Create: `tests/dedup/test_summary.py`

- [ ] **Step 1: Write the failing tests**

`tests/dedup/test_summary.py`:

```python
from mr.dedup.seen import SeenEntry
from mr.dedup.summary import build_summary_block


def _entry(slug: str, lane: str = "ephemeral_public", niche_key: str = "alerts_aviation",
           hosts: tuple[str, ...] = ("a.com",), disposition: str = "candidate",
           date_created: str = "2026-05-07") -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche=niche_key.replace("_", " "),
        niche_key=niche_key, thesis=f"{slug} thesis.",
        source_set=list(hosts), disposition=disposition,
        auto_reject_reason=None, date_created=date_created,
    )


def test_empty_corpus_yields_minimal_block():
    block = build_summary_block([])
    assert "Lane × niche frequency" in block
    assert "no briefs yet" in block.lower() or "none" in block.lower()


def test_small_corpus_uses_full_index():
    entries = [_entry(f"brief-{i:02d}") for i in range(5)]
    block = build_summary_block(entries)
    for i in range(5):
        assert f"brief-{i:02d}" in block


def test_large_corpus_uses_bounded_summary():
    entries = [_entry(f"brief-{i:03d}") for i in range(60)]
    block = build_summary_block(entries)
    # Bounded summary path: only 30 most-recent appear in the recent-briefs section
    assert "30 most-recent" in block.lower() or "most recent" in block.lower()


def test_lane_niche_freq_excludes_other_lane():
    entries = [
        _entry("a", lane="ephemeral_public", niche_key="alerts_aviation"),
        _entry("b", lane="other", niche_key="weird_thing"),
        _entry("c", lane="ephemeral_public", niche_key="alerts_aviation"),
    ]
    block = build_summary_block(entries)
    # Frequency table should count alerts_aviation = 2, NOT include weird_thing
    assert "alerts_aviation" in block
    assert "weird_thing" not in block.split("Lane × niche frequency")[1].split("\n##")[0]


def test_other_lane_rows_tagged_in_recent_list():
    entries = [_entry("a", lane="other", niche_key="weird")]
    block = build_summary_block(entries)
    assert "(exploration)" in block


def test_most_mined_hosts_split_solo_vs_fusion():
    entries = [
        _entry("a", hosts=("a.com",)),
        _entry("b", hosts=("a.com",)),
        _entry("c", hosts=("a.com", "b.com")),  # fusion
    ]
    block = build_summary_block(entries)
    # a.com: 2 solo + 1 fusion appearance (3 total)
    assert "a.com" in block
    # solo/fusion split should be visible
    assert "solo" in block.lower()
    assert "fusion" in block.lower()


def test_other_lane_only_hosts_tagged_exploration():
    entries = [
        _entry("a", lane="other", hosts=("explore.com",)),
        _entry("b", lane="other", hosts=("explore.com",)),
    ]
    block = build_summary_block(entries)
    assert "(exploration host)" in block
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/dedup/test_summary.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/dedup/summary.py`**

```python
"""Bounded pre-pended summary block for mr discover and mr wishlist expand.

Spec §12.2: lane×niche freq + 30 most-recent + top-20 mined hosts (solo/fusion split).
§8.4.1 other-lane treatment: exempt from frequency table; tagged in recent + hosts blocks.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from mr.dedup.seen import SeenEntry

_COLD_CORPUS_THRESHOLD = 50
_RECENT_LIMIT = 30
_TOP_HOSTS = 20


def build_summary_block(entries: Sequence[SeenEntry]) -> str:
    """Render the §12.2 bounded summary block as markdown."""
    if not entries:
        return _empty_block()

    if len(entries) <= _COLD_CORPUS_THRESHOLD:
        return _full_index_block(entries)

    return _bounded_summary_block(entries)


def _empty_block() -> str:
    return (
        "## Lane × niche frequency\n"
        "(no briefs yet — corpus is empty)\n\n"
        "## 30 most-recent briefs\n"
        "(none)\n\n"
        "## Most-mined hosts\n"
        "(none)\n"
    )


def _full_index_block(entries: Sequence[SeenEntry]) -> str:
    return _bounded_summary_block(entries)


def _bounded_summary_block(entries: Sequence[SeenEntry]) -> str:
    parts: list[str] = []
    parts.append(_freq_table(entries))
    parts.append(_recent_briefs(entries))
    parts.append(_mined_hosts(entries))
    return "\n\n".join(parts)


def _freq_table(entries: Sequence[SeenEntry]) -> str:
    """Lane × niche frequency excluding lane=other (§8.4.1 exemption)."""
    pairs = Counter(
        (e.lane, e.niche_key) for e in entries if e.lane != "other"
    )
    lines = ["## Lane × niche frequency (excl. lane: other — exploration channel)"]
    if not pairs:
        lines.append("(no canonical-lane briefs yet)")
    else:
        lines.append("| lane | niche_key | count |")
        lines.append("|---|---|---|")
        for (lane, niche_key), count in pairs.most_common():
            lines.append(f"| {lane} | {niche_key} | {count} |")
    return "\n".join(lines)


def _recent_briefs(entries: Sequence[SeenEntry]) -> str:
    """30 most-recent briefs, with `(exploration)` tag for lane=other."""
    sorted_recent = sorted(entries, key=lambda e: e.date_created, reverse=True)[:_RECENT_LIMIT]
    lines = ["## 30 most-recent briefs"]
    if not sorted_recent:
        lines.append("(none)")
        return "\n".join(lines)

    lines.append("| slug | lane | niche_key | thesis | source_set |")
    lines.append("|---|---|---|---|---|")
    for e in sorted_recent:
        lane_display = f"{e.lane} (exploration)" if e.lane == "other" else e.lane
        hosts = ", ".join(e.source_set) if e.source_set else "—"
        thesis = (e.thesis or "—").replace("|", "\\|").strip()
        lines.append(f"| {e.slug} | {lane_display} | {e.niche_key} | {thesis} | {hosts} |")
    return "\n".join(lines)


def _mined_hosts(entries: Sequence[SeenEntry]) -> str:
    """Top-20 hosts by appearance count, split solo vs. fusion."""
    solo: Counter[str] = Counter()
    fusion: Counter[str] = Counter()
    other_only: set[str] = set()
    canonical_seen: set[str] = set()

    for e in entries:
        is_fusion = len(e.source_set) > 1
        for host in e.source_set:
            if is_fusion:
                fusion[host] += 1
            else:
                solo[host] += 1
            if e.lane == "other":
                other_only.add(host)
            else:
                canonical_seen.add(host)

    totals: Counter[str] = Counter()
    for host, c in solo.items():
        totals[host] += c
    for host, c in fusion.items():
        totals[host] += c

    lines = ["## Most-mined hosts (top 20, solo vs. fusion split)"]
    top = totals.most_common(_TOP_HOSTS)
    if not top:
        lines.append("(none)")
        return "\n".join(lines)

    lines.append("| host | total | solo | fusion |")
    lines.append("|---|---|---|---|")
    for host, total in top:
        tag = " (exploration host)" if host in other_only and host not in canonical_seen else ""
        lines.append(f"| {host}{tag} | {total} | {solo.get(host, 0)} | {fusion.get(host, 0)} |")
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/dedup/test_summary.py -v`
Expected: PASS for all 7 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/dedup/summary.py tests/dedup/test_summary.py
git commit -m "$(cat <<'EOF'
feat(dedup): bounded pre-pended summary block (~3k token cap)

Implements build_summary_block() per spec §12.2: lane×niche frequency
(excl. lane=other), 30 most-recent briefs (exploration-tagged), top-20
mined hosts with solo/fusion split. Cold-corpus exception (n≤50) uses
full index. §8.4.1 other-lane treatment fully wired.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 6: Custom Python tools

### Task 17: wayback_check

**Spec sections:** §8.3 (waybackpy → CDX → {first, last, count})

**Files:**
- Create: `mr/tools/wayback.py`
- Create: `tests/tools/__init__.py`
- Create: `tests/tools/test_wayback.py`

- [ ] **Step 1: Write the failing tests**

`tests/tools/test_wayback.py`:

```python
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from mr.tools.wayback import WaybackResult, wayback_check


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_returns_count_first_last(mock_cdx_class):
    snapshot1 = MagicMock(timestamp="20230412120000", original="https://example.com/")
    snapshot2 = MagicMock(timestamp="20260430120000", original="https://example.com/")
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = [snapshot1, snapshot2]
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://example.com/")
    assert isinstance(result, WaybackResult)
    assert result.count == 2
    assert result.first == date(2023, 4, 12)
    assert result.last == date(2026, 4, 30)


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_no_snapshots(mock_cdx_class):
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = []
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://no-archive.example.com/")
    assert result.count == 0
    assert result.first is None
    assert result.last is None


@patch("mr.tools.wayback.WaybackMachineCDXServerAPI")
def test_years_helper(mock_cdx_class):
    snapshot1 = MagicMock(timestamp="20230101000000", original="https://example.com/")
    snapshot2 = MagicMock(timestamp="20260101000000", original="https://example.com/")
    mock_instance = MagicMock()
    mock_instance.snapshots.return_value = [snapshot1, snapshot2]
    mock_cdx_class.return_value = mock_instance

    result = wayback_check("https://example.com/")
    assert result.years == pytest.approx(3.0, abs=0.01)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tools/test_wayback.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/tools/wayback.py`**

```python
"""Wayback Machine CDX API wrapper.

Spec §8.3: waybackpy → CDX → {first, last, count}.
Used by mr discover, mr score (host-driven verification), mr wishlist refresh.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from waybackpy import WaybackMachineCDXServerAPI


@dataclass
class WaybackResult:
    count: int
    first: date | None
    last: date | None

    @property
    def years(self) -> float:
        if self.first is None or self.last is None:
            return 0.0
        return (self.last - self.first).days / 365.25


def wayback_check(url: str, user_agent: str = "moat-research/0.1") -> WaybackResult:
    """Query Wayback CDX for snapshot count and date range.

    Returns count=0 / first=None / last=None when no snapshots exist.
    """
    cdx = WaybackMachineCDXServerAPI(url=url, user_agent=user_agent)
    snapshots = list(cdx.snapshots())

    if not snapshots:
        return WaybackResult(count=0, first=None, last=None)

    timestamps = [_parse_ts(s.timestamp) for s in snapshots]
    return WaybackResult(
        count=len(snapshots),
        first=min(timestamps),
        last=max(timestamps),
    )


def _parse_ts(ts: str) -> date:
    """CDX timestamps are 'yyyymmddHHMMSS'; we keep only the date."""
    return date(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/tools/test_wayback.py -v`
Expected: PASS for all 3 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/tools/wayback.py tests/tools/__init__.py tests/tools/test_wayback.py
git commit -m "$(cat <<'EOF'
feat(tools): wayback_check using waybackpy CDX API

Implements WaybackResult dataclass and wayback_check() per spec §8.3.
Returns {count, first, last, years}. Used by host-driven verification
of unrestricted_archives (§6.4) and wishlist refresh (§11).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 18: robots_check

**Spec sections:** §8.3 (urllib.robotparser stdlib wrapper)

**Files:**
- Create: `mr/tools/robots.py`
- Create: `tests/tools/test_robots.py`

- [ ] **Step 1: Write the failing tests**

`tests/tools/test_robots.py`:

```python
from unittest.mock import patch

from mr.tools.robots import RobotsResult, robots_check


def test_allowed_when_no_robots(monkeypatch):
    """Missing robots.txt → assumed allowed per RFC."""
    class FakeParser:
        def set_url(self, url): pass
        def read(self): pass
        def can_fetch(self, ua, url): return True
    with patch("mr.tools.robots.RobotFileParser", return_value=FakeParser()):
        r = robots_check("https://example.com/some/path", user_agent="moat-research/0.1")
        assert r.allowed is True


def test_disallowed_path(monkeypatch):
    class FakeParser:
        def set_url(self, url): pass
        def read(self): pass
        def can_fetch(self, ua, url): return False
    with patch("mr.tools.robots.RobotFileParser", return_value=FakeParser()):
        r = robots_check("https://example.com/private", user_agent="moat-research/0.1")
        assert r.allowed is False


def test_robots_url_constructed_from_origin():
    r = RobotsResult(allowed=True, robots_url="https://example.com/robots.txt", error=None)
    assert r.robots_url == "https://example.com/robots.txt"


def test_returns_error_on_unreachable(monkeypatch):
    class BrokenParser:
        def set_url(self, url): pass
        def read(self): raise OSError("network down")
        def can_fetch(self, ua, url): return False
    with patch("mr.tools.robots.RobotFileParser", return_value=BrokenParser()):
        r = robots_check("https://offline.example/", user_agent="moat-research/0.1")
        assert r.allowed is True  # fail open per RFC convention
        assert r.error is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tools/test_robots.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/tools/robots.py`**

```python
"""robots.txt check using urllib.robotparser.

Spec §8.3: stdlib only. Fail-open on network errors per RFC convention.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


@dataclass
class RobotsResult:
    allowed: bool
    robots_url: str
    error: str | None


def robots_check(url: str, user_agent: str) -> RobotsResult:
    """Check robots.txt for the URL's origin. Fails open on network error."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        parser.read()
    except OSError as e:
        return RobotsResult(allowed=True, robots_url=robots_url, error=str(e))

    allowed = parser.can_fetch(user_agent, url)
    return RobotsResult(allowed=allowed, robots_url=robots_url, error=None)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/tools/test_robots.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/tools/robots.py tests/tools/test_robots.py
git commit -m "$(cat <<'EOF'
feat(tools): robots_check using urllib.robotparser

Implements robots_check() per spec §8.3 — pure stdlib. Fails open on
network errors (RFC convention). Used by mr score TOS verification
and wishlist refresh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 19: head_check

**Spec sections:** §8.3 (httpx HEAD)

**Files:**
- Create: `mr/tools/head.py`
- Create: `tests/tools/test_head.py`

- [ ] **Step 1: Write the failing tests**

`tests/tools/test_head.py`:

```python
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from mr.tools.head import HeadResult, head_check


@patch("mr.tools.head.httpx.Client")
def test_returns_status_and_headers(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MagicMock(status_code=200, headers={
        "content-type": "text/html; charset=utf-8",
        "last-modified": "Wed, 07 May 2026 12:00:00 GMT",
    })
    mock_client.head.return_value = mock_response
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://example.com/")
    assert r.status == 200
    assert r.content_type == "text/html; charset=utf-8"
    assert r.last_modified is not None


@patch("mr.tools.head.httpx.Client")
def test_4xx_status(mock_client_cls):
    mock_client = MagicMock()
    mock_response = MagicMock(status_code=404, headers={})
    mock_client.head.return_value = mock_response
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://example.com/missing")
    assert r.status == 404
    assert r.content_type is None


@patch("mr.tools.head.httpx.Client")
def test_network_error(mock_client_cls):
    import httpx
    mock_client = MagicMock()
    mock_client.head.side_effect = httpx.ConnectError("connection refused")
    mock_client_cls.return_value.__enter__.return_value = mock_client

    r = head_check("https://offline.example/")
    assert r.status is None
    assert r.error is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tools/test_head.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/tools/head.py`**

```python
"""HTTP HEAD wrapper for liveness checks.

Spec §8.3: httpx HEAD → {status, content_type, last_modified}.
Used by mr wishlist refresh (§11).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx

_DEFAULT_TIMEOUT_S = 10.0


@dataclass
class HeadResult:
    status: int | None
    content_type: str | None
    last_modified: datetime | None
    error: str | None


def head_check(url: str, timeout_s: float = _DEFAULT_TIMEOUT_S) -> HeadResult:
    """HTTP HEAD a URL. Returns status, content-type, last-modified.

    Network errors are reported via `error`; status is None in that case.
    """
    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            resp = client.head(url)
    except httpx.HTTPError as e:
        return HeadResult(status=None, content_type=None, last_modified=None, error=str(e))

    content_type = resp.headers.get("content-type")
    last_mod_raw = resp.headers.get("last-modified")
    last_modified = None
    if last_mod_raw:
        try:
            last_modified = parsedate_to_datetime(last_mod_raw)
        except (TypeError, ValueError):
            last_modified = None

    return HeadResult(
        status=resp.status_code,
        content_type=content_type,
        last_modified=last_modified,
        error=None,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/tools/test_head.py -v`
Expected: PASS for all 3 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/tools/head.py tests/tools/test_head.py
git commit -m "$(cat <<'EOF'
feat(tools): head_check via httpx HEAD with timeout + redirect follow

Implements HeadResult and head_check() per spec §8.3. Returns status,
content_type, last_modified. Network errors reported in .error. Used
by wishlist refresh and (host-driven) wishlist verification.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 20: seen_lookup

**Spec sections:** §12.3 (seen_lookup tool: matches + near_matches)

**Files:**
- Create: `mr/tools/seen_lookup.py`
- Create: `tests/tools/test_seen_lookup.py`

- [ ] **Step 1: Write the failing tests**

`tests/tools/test_seen_lookup.py`:

```python
from pathlib import Path

from mr.dedup.seen import SeenEntry
from mr.tools.seen_lookup import SeenLookupResult, seen_lookup


def _write_seen(path: Path, entries: list[SeenEntry]) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for e in entries:
            f.write(json.dumps(e.to_json_obj()) + "\n")


def _entry(slug: str, hosts: list[str], lane: str = "ephemeral_public",
           niche_key: str = "alerts_aviation") -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche="x", niche_key=niche_key,
        thesis=f"{slug} thesis.", source_set=hosts,
        disposition="candidate", auto_reject_reason=None,
        date_created="2026-05-07",
    )


def test_exact_slug_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen, slug="foo")
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_slug"


def test_exact_source_set_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "b.com"])])
    r = seen_lookup(seen, source_set=["b.com", "a.com"])  # order-independent
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_source_set"


def test_exact_lane_niche_match(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"], lane="cross_source_fusion", niche_key="abc")])
    r = seen_lookup(seen, lane_niche=("cross_source_fusion", "abc"))
    assert len(r.matches) == 1
    assert r.matches[0]["match_reason"] == "exact_lane_niche"


def test_near_match_source_set_subset(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "b.com"])])
    r = seen_lookup(seen, source_set=["a.com"])
    assert len(r.matches) == 0
    assert any(nm["match_reason"] == "source_set_subset" for nm in r.near_matches)


def test_near_match_source_set_superset(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen, source_set=["a.com", "b.com"])
    assert any(nm["match_reason"] == "source_set_superset" for nm in r.near_matches)


def test_near_match_single_host_overlap(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com", "x.com"])])
    r = seen_lookup(seen, source_set=["a.com", "y.com"])
    assert any(nm["match_reason"] == "single_host_overlap" for nm in r.near_matches)


def test_no_args_returns_empty(tmp_path: Path):
    seen = tmp_path / "seen.jsonl"
    _write_seen(seen, [_entry("foo", ["a.com"])])
    r = seen_lookup(seen)
    assert r.matches == []
    assert r.near_matches == []


def test_missing_seen_file_returns_empty(tmp_path: Path):
    r = seen_lookup(tmp_path / "absent.jsonl", slug="foo")
    assert r.matches == []
    assert r.near_matches == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tools/test_seen_lookup.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/tools/seen_lookup.py`**

```python
"""seen_lookup custom tool: query seen.jsonl for matches and near-matches.

Spec §12.3: returns {matches, near_matches}. Set semantics on source_set.
~100 LOC, no LLM, host-side Python.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mr.dedup.seen import read_seen


@dataclass
class SeenLookupResult:
    matches: list[dict[str, Any]] = field(default_factory=list)
    near_matches: list[dict[str, Any]] = field(default_factory=list)


def seen_lookup(
    seen_path: Path,
    slug: str | None = None,
    source_set: list[str] | None = None,
    lane_niche: tuple[str, str] | None = None,
) -> SeenLookupResult:
    """Look up matches in seen.jsonl. Returns matches + near-matches.

    See spec §12.4 for match-type definitions:
    - matches: exact_slug, exact_source_set, exact_lane_niche
    - near_matches: source_set_subset/superset, single_host_overlap, partial_niche
    """
    out = SeenLookupResult()
    if all(arg is None for arg in (slug, source_set, lane_niche)):
        return out

    entries = read_seen(seen_path)
    query_set = frozenset(source_set) if source_set else None

    for e in entries:
        info = {"file": e.slug, "slug": e.slug, "thesis": e.thesis}

        if slug is not None and e.slug == slug:
            out.matches.append({**info, "match_reason": "exact_slug"})
            continue

        if query_set is not None and query_set == frozenset(e.source_set):
            out.matches.append({**info, "match_reason": "exact_source_set"})
            continue

        if lane_niche is not None and (e.lane, e.niche_key) == lane_niche:
            out.matches.append({**info, "match_reason": "exact_lane_niche"})
            continue

        # Near-match analysis on source_set
        if query_set is not None:
            entry_set = frozenset(e.source_set)
            if query_set < entry_set:
                out.near_matches.append({**info, "match_reason": "source_set_subset"})
                continue
            if query_set > entry_set:
                out.near_matches.append({**info, "match_reason": "source_set_superset"})
                continue
            if query_set & entry_set:
                out.near_matches.append({**info, "match_reason": "single_host_overlap"})
                continue

        # Partial niche match
        if lane_niche is not None and lane_niche[0] == e.lane:
            out.near_matches.append({**info, "match_reason": "partial_niche"})

    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/tools/test_seen_lookup.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/tools/seen_lookup.py tests/tools/test_seen_lookup.py
git commit -m "$(cat <<'EOF'
feat(tools): seen_lookup custom tool for §12.3 dedup queries

Implements seen_lookup(slug?, source_set?, lane_niche?) → matches +
near_matches. Set semantics on source_set (order-independent). All
match types from spec §12.4 covered: exact_slug, exact_source_set,
exact_lane_niche, source_set_subset/superset, single_host_overlap,
partial_niche.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 21: firecrawl_scrape (optional)

**Spec sections:** §8.3 (firecrawl-py optional, only when MR_FIRECRAWL_API_KEY is set)

**Files:**
- Create: `mr/tools/firecrawl.py`
- Create: `tests/tools/test_firecrawl.py`

- [ ] **Step 1: Write the failing tests**

`tests/tools/test_firecrawl.py`:

```python
import os
from unittest.mock import MagicMock, patch

import pytest

from mr.tools.firecrawl import FirecrawlNotConfigured, firecrawl_scrape, is_firecrawl_available


def test_unavailable_when_env_unset(monkeypatch):
    monkeypatch.delenv("MR_FIRECRAWL_API_KEY", raising=False)
    assert is_firecrawl_available() is False


def test_available_when_env_set(monkeypatch):
    monkeypatch.setenv("MR_FIRECRAWL_API_KEY", "fc-test-key")
    assert is_firecrawl_available() is True


def test_scrape_raises_without_env(monkeypatch):
    monkeypatch.delenv("MR_FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(FirecrawlNotConfigured):
        firecrawl_scrape("https://example.com")


@patch("mr.tools.firecrawl.FirecrawlApp")
def test_scrape_returns_markdown(mock_app_cls, monkeypatch):
    monkeypatch.setenv("MR_FIRECRAWL_API_KEY", "fc-test-key")
    mock_app = MagicMock()
    mock_app.scrape.return_value = MagicMock(markdown="# Hello\n\nworld")
    mock_app_cls.return_value = mock_app

    result = firecrawl_scrape("https://example.com")
    assert result.markdown == "# Hello\n\nworld"
    mock_app_cls.assert_called_once_with(api_key="fc-test-key")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/tools/test_firecrawl.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/tools/firecrawl.py`**

```python
"""Firecrawl wrapper for JS-rendered or structured-extraction targets.

Spec §8.3: optional dependency, only loaded when MR_FIRECRAWL_API_KEY is set.
Used as fallback by mr discover and mr wishlist expand.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


class FirecrawlNotConfigured(Exception):
    """Raised when firecrawl_scrape is called without MR_FIRECRAWL_API_KEY."""


@dataclass
class FirecrawlResult:
    markdown: str
    url: str


def is_firecrawl_available() -> bool:
    """True iff MR_FIRECRAWL_API_KEY is set in the environment."""
    return bool(os.environ.get("MR_FIRECRAWL_API_KEY"))


def firecrawl_scrape(url: str) -> FirecrawlResult:
    """Scrape a URL via Firecrawl and return its markdown.

    Raises FirecrawlNotConfigured if the API key is missing.
    The firecrawl-py dependency is only imported here, so the package
    works without it as long as this function is never called.
    """
    api_key = os.environ.get("MR_FIRECRAWL_API_KEY")
    if not api_key:
        raise FirecrawlNotConfigured(
            "MR_FIRECRAWL_API_KEY not set; install moat-research[firecrawl] "
            "and export the key to enable JS-rendered scraping."
        )

    from firecrawl import FirecrawlApp

    app = FirecrawlApp(api_key=api_key)
    response = app.scrape(url)
    return FirecrawlResult(markdown=response.markdown, url=url)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/tools/test_firecrawl.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/tools/firecrawl.py tests/tools/test_firecrawl.py
git commit -m "$(cat <<'EOF'
feat(tools): optional firecrawl_scrape for JS-rendered fallback

Implements firecrawl_scrape() with deferred import — package usable
without firecrawl-py as long as the function isn't called. Gated on
MR_FIRECRAWL_API_KEY env var per spec §8.3.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 7: Synth (pricing, budget, prompts, client, tools, verify)

### Task 22: Model pricing lookup

**Spec sections:** §9 (mr.yaml models.pricing block)

**Files:**
- Create: `mr/synth/__init__.py` (already exists empty; ensure it stays empty)
- Create: `mr/synth/pricing.py`
- Create: `tests/synth/__init__.py`
- Create: `tests/synth/test_pricing.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_pricing.py`:

```python
import pytest

from mr.synth.pricing import ModelPricing, get_pricing
from mr.util.config import Config, DEFAULT_CONFIG


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_pricing.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/pricing.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_pricing.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/pricing.py tests/synth/__init__.py tests/synth/test_pricing.py
git commit -m "$(cat <<'EOF'
feat(synth): per-model pricing lookup from mr.yaml

Implements ModelPricing dataclass and get_pricing() per spec §9.
Used by §7 tier-1 budget ceiling computation and post-call cost
recording into costs.jsonl.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 23: Budget enforcement (4-tier + cold-corpus preflight)

**Spec sections:** §7 (four-tier enforcement + cold-corpus preflight)

**Files:**
- Create: `mr/synth/budget.py`
- Create: `tests/synth/test_budget.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_budget.py`:

```python
from datetime import datetime, timezone
from pathlib import Path

import pytest

from mr.synth.budget import (
    BudgetExceeded,
    BudgetTracker,
    cold_corpus_preflight,
    worst_case_ceiling,
)
from mr.synth.pricing import ModelPricing
from mr.util.config import Config, DEFAULT_CONFIG
from mr.util.costs import CostRecord, append_cost


def _opus() -> ModelPricing:
    return ModelPricing(input_per_mtok=15.0, output_per_mtok=75.0,
                        cache_read_per_mtok=1.5, cache_write_per_mtok=18.75)


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
    costs = tmp_path / "costs.jsonl"
    tracker = BudgetTracker(cfg=cfg, command="discover", model="claude-opus-4-7",
                            budget_usd=1.00, costs_path=costs)
    # Spend $0.85 already
    append_cost(costs, CostRecord(
        ts=datetime.now(timezone.utc), command="discover", model="claude-opus-4-7",
        input_tokens=0, cached_input_tokens=0, output_tokens=0,
        cache_hits=0, cache_misses=0,
        code_execution_container_seconds=0, cost_usd=0.85,
    ))
    # Estimate $0.10 more → tally + estimate = $0.95 > 0.9 × $1.00 → abort
    with pytest.raises(BudgetExceeded, match="per-turn"):
        tracker.check_pre_call(input_tokens_estimate=2000, max_output_tokens=1500)


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_budget.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/budget.py`**

```python
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
from mr.util.costs import running_total

_MIN_WISHLIST_SOURCES = 5


class BudgetExceeded(Exception):
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


class BudgetTracker:
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
        if self.costs_path is None or not self.costs_path.exists():
            running = 0.0
        else:
            running = running_total(self.costs_path, command=self.command)

        estimate = (
            self.pricing.estimate_input_cost_usd(input_tokens_estimate)
            + self.pricing.estimate_output_cost_usd(max_output_tokens)
        )
        if running + estimate > self.budget_usd * 0.9:
            raise BudgetExceeded(
                f"per-turn estimate would exceed budget × 0.9: "
                f"running ${running:.2f} + estimate ${estimate:.2f} > "
                f"${self.budget_usd * 0.9:.2f}"
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
        if self._turn_idx <= 2:
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

        if self._consecutive_misses >= 2:
            raise BudgetExceeded(
                f"consecutive cache misses (re-writes) at turn {self._turn_idx}: "
                f"working set exceeds 5-min TTL"
            )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_budget.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/budget.py tests/synth/test_budget.py
git commit -m "$(cat <<'EOF'
feat(synth): four-tier budget enforcement + cold-corpus preflight

Implements worst_case_ceiling (tier 1, cache-amortized formula),
BudgetTracker (tiers 2-4), and cold_corpus_preflight per spec §7.
Tier 4b distinguishes first-time cache creation (turns 1-2 exempt)
from re-write misses on previously-cached fingerprints.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 24: Prompt loader

**Spec sections:** §8.4 (prompts/ user-editable, read on each invocation)

**Files:**
- Create: `mr/synth/prompts.py`
- Create: `tests/synth/test_prompts.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_prompts.py`:

```python
from pathlib import Path

import pytest

from mr.synth.prompts import PromptNotFound, load_prompt


def test_load_existing(tmp_path: Path):
    p = tmp_path / "discover.md"
    p.write_text("# Discover prompt\n\nRules...")
    text = load_prompt(tmp_path, "discover")
    assert "Discover prompt" in text


def test_load_missing_raises(tmp_path: Path):
    with pytest.raises(PromptNotFound, match="discover"):
        load_prompt(tmp_path, "discover")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_prompts.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/prompts.py`**

```python
"""Prompt loader. Reads from prompts/ on each invocation, no compilation."""
from __future__ import annotations

from pathlib import Path


class PromptNotFound(Exception):
    pass


def load_prompt(prompts_dir: Path, name: str) -> str:
    """Load a prompt file by name (without .md extension)."""
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        raise PromptNotFound(f"prompt {name!r} not found at {path}")
    return path.read_text()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_prompts.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/prompts.py tests/synth/test_prompts.py
git commit -m "$(cat <<'EOF'
feat(synth): prompt loader from prompts/ directory

Reads prompts on each invocation per spec §8.4 — no compilation.
Used by discover, score, wishlist_expand subcommands.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 25: Anthropic SDK client wrapper with caching

**Spec sections:** §8.1 (model defaults, mandatory prompt caching), §10 (cost recording)

**Files:**
- Create: `mr/synth/client.py`
- Create: `tests/synth/test_client.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_client.py`:

```python
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mr.synth.client import SynthClient, build_cached_blocks
from mr.util.config import Config, DEFAULT_CONFIG


def test_build_cached_blocks_separates_system_wishlist_seen():
    blocks = build_cached_blocks(
        system_text="System prompt here.",
        wishlist_text="WISHLIST yaml here.",
        seen_summary="seen summary here.",
    )
    assert len(blocks) == 3
    for block in blocks:
        assert block["type"] == "text"
        assert block["cache_control"] == {"type": "ephemeral"}
    assert "System prompt here" in blocks[0]["text"]
    assert "WISHLIST yaml here" in blocks[1]["text"]
    assert "seen summary here" in blocks[2]["text"]


@patch("mr.synth.client.Anthropic")
def test_synth_client_uses_correct_model(mock_anthropic_cls):
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    assert client.model == "claude-opus-4-7"


@patch("mr.synth.client.Anthropic")
def test_synth_client_per_command_override(mock_anthropic_cls):
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="wishlist_expand")
    assert client.model == "claude-sonnet-4-6"


@patch("mr.synth.client.Anthropic")
def test_create_message_passes_through(mock_anthropic_cls):
    mock_anthropic = MagicMock()
    mock_response = MagicMock(
        usage=MagicMock(
            input_tokens=100, output_tokens=50,
            cache_read_input_tokens=200, cache_creation_input_tokens=0,
        ),
        content=[MagicMock(type="text", text="hello")],
        stop_reason="end_turn",
    )
    mock_anthropic.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_anthropic

    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    response = client.create_message(
        system_blocks=[{"type": "text", "text": "sys", "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "hi"}],
        tools=[],
        max_tokens=1500,
    )
    assert response is mock_response
    assert mock_anthropic.messages.create.called


@patch("mr.synth.client.Anthropic")
def test_extract_usage_returns_cost_record_fields(mock_anthropic_cls):
    cfg = Config(**DEFAULT_CONFIG)
    client = SynthClient(cfg=cfg, command="discover")
    response = MagicMock(
        usage=MagicMock(
            input_tokens=100, output_tokens=50,
            cache_read_input_tokens=300, cache_creation_input_tokens=0,
        ),
    )
    fields = client.extract_usage(response)
    assert fields["input_tokens"] == 100
    assert fields["output_tokens"] == 50
    assert fields["cache_hits"] == 300
    assert fields["cache_misses"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_client.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/client.py`**

```python
"""Anthropic SDK client wrapper with mandatory prompt caching.

Spec §8.1: cached blocks for system prompt, WISHLIST, seen-summary.
Spec §10: post-call usage recorded in costs.jsonl.
"""
from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

from mr.synth.pricing import get_pricing
from mr.util.config import Config


def build_cached_blocks(
    system_text: str,
    wishlist_text: str | None = None,
    seen_summary: str | None = None,
) -> list[dict[str, Any]]:
    """Build a list of cache-controlled system blocks.

    Each unique chunk of repeated content gets its own cache slot so
    additions to one don't invalidate others (e.g., adding to WISHLIST
    doesn't bust the system prompt cache). Empty pieces are skipped.
    """
    blocks: list[dict[str, Any]] = []
    blocks.append({
        "type": "text",
        "text": system_text,
        "cache_control": {"type": "ephemeral"},
    })
    if wishlist_text:
        blocks.append({
            "type": "text",
            "text": wishlist_text,
            "cache_control": {"type": "ephemeral"},
        })
    if seen_summary:
        blocks.append({
            "type": "text",
            "text": seen_summary,
            "cache_control": {"type": "ephemeral"},
        })
    return blocks


class SynthClient:
    """Wrapper around Anthropic API enforcing cache-controlled blocks."""

    def __init__(self, cfg: Config, command: str):
        self.cfg = cfg
        self.command = command
        self.model = self._resolve_model()
        self.pricing = get_pricing(cfg, self.model)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = Anthropic(api_key=api_key)

    def _resolve_model(self) -> str:
        models = self.cfg.models
        per_command = models.get("per_command", {})
        if self.command in per_command:
            return per_command[self.command]
        return models.get("default", "claude-opus-4-7")

    def create_message(
        self,
        *,
        system_blocks: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int,
        tool_choice: dict[str, Any] | None = None,
    ) -> Any:
        """Make a single API call. Returns the raw response object."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_blocks,
            "messages": messages,
            "tools": tools,
        }
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
        return self._client.messages.create(**kwargs)

    def extract_usage(self, response: Any) -> dict[str, int]:
        """Pull token counts from the response's usage block."""
        usage = response.usage
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "cache_hits": getattr(usage, "cache_read_input_tokens", 0) or 0,
            "cache_misses": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        }

    def compute_cost_usd(self, usage: dict[str, int]) -> float:
        """Compute USD cost from extracted usage fields per spec §10."""
        return (
            self.pricing.estimate_input_cost_usd(usage["input_tokens"])
            + self.pricing.estimate_output_cost_usd(usage["output_tokens"])
            + (usage["cache_hits"] / 1_000_000) * self.pricing.cache_read_per_mtok
            + (usage["cache_misses"] / 1_000_000) * self.pricing.cache_write_per_mtok
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_client.py -v`
Expected: PASS for all 5 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/client.py tests/synth/test_client.py
git commit -m "$(cat <<'EOF'
feat(synth): SynthClient wrapping Anthropic SDK with cached blocks

Implements build_cached_blocks (separate cache slots for system,
WISHLIST, seen-summary per spec §8.1), SynthClient (model resolution
per command, cost extraction). compute_cost_usd uses §9 pricing
table for spec §10 costs.jsonl reconstruction.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 26: Native + custom tool definitions for the API

**Spec sections:** §8.2 (tools per subcommand), §12.3 (seen_lookup tool spec)

**Files:**
- Create: `mr/synth/tools.py`
- Create: `tests/synth/test_tools.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_tools.py`:

```python
from mr.synth.tools import (
    CUSTOM_TOOL_DEFS,
    NATIVE_TOOL_DEFS,
    tools_for_command,
)


def test_native_tools_have_anthropic_types():
    assert NATIVE_TOOL_DEFS["web_search"]["type"] == "web_search_20260209"
    assert NATIVE_TOOL_DEFS["web_fetch"]["type"] == "web_fetch_20260209"
    assert NATIVE_TOOL_DEFS["code_execution"]["type"] == "code_execution_20260209"


def test_custom_seen_lookup_schema():
    seen_lookup = CUSTOM_TOOL_DEFS["seen_lookup"]
    assert seen_lookup["name"] == "seen_lookup"
    schema = seen_lookup["input_schema"]
    assert schema["type"] == "object"
    assert "slug" in schema["properties"]
    assert "source_set" in schema["properties"]
    assert "lane_niche" in schema["properties"]


def test_tools_for_discover_has_seen_lookup_search_fetch_code_wayback():
    tools = tools_for_command("discover", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "web_search_20260209" in names
    assert "web_fetch_20260209" in names
    assert "code_execution_20260209" in names
    assert "seen_lookup" in names
    assert "wayback_check" in names
    assert "firecrawl_scrape" not in names


def test_tools_for_score_excludes_web_search():
    tools = tools_for_command("score", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "web_search_20260209" not in names
    assert "web_fetch_20260209" in names
    assert "wayback_check" in names
    assert "robots_check" in names
    assert "head_check" in names


def test_tools_for_wishlist_expand_includes_seen_lookup():
    tools = tools_for_command("wishlist_expand", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "seen_lookup" in names
    assert "web_search_20260209" in names


def test_firecrawl_only_when_available():
    tools_with = tools_for_command("discover", firecrawl_available=True)
    names_with = {t.get("name", t.get("type")) for t in tools_with}
    assert "firecrawl_scrape" in names_with
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_tools.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/tools.py`**

```python
"""Tool definitions for Anthropic API requests.

Spec §8.2: tool set per subcommand.
Spec §12.3: seen_lookup custom tool schema.
"""
from __future__ import annotations

from typing import Any

NATIVE_TOOL_DEFS: dict[str, dict[str, Any]] = {
    "web_search": {"type": "web_search_20260209", "name": "web_search"},
    "web_fetch": {"type": "web_fetch_20260209", "name": "web_fetch"},
    "code_execution": {"type": "code_execution_20260209", "name": "code_execution"},
}

CUSTOM_TOOL_DEFS: dict[str, dict[str, Any]] = {
    "seen_lookup": {
        "name": "seen_lookup",
        "description": (
            "Look up matches in seen.jsonl for a candidate brief before commit. "
            "Returns matches (exact_slug, exact_source_set, exact_lane_niche) and "
            "near_matches (subset/superset/single_host_overlap/partial_niche). "
            "Use when about to commit a candidate to verify novelty."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "source_set": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Set of distinct hosts (order-independent).",
                },
                "lane_niche": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Tuple [lane, niche_key].",
                },
            },
        },
    },
    "wayback_check": {
        "name": "wayback_check",
        "description": "Query Wayback Machine CDX for snapshot count and date range. Returns {count, first, last, years}.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
            },
        },
    },
    "robots_check": {
        "name": "robots_check",
        "description": "Check robots.txt for the URL's origin. Returns {allowed, robots_url, error}.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
                "user_agent": {"type": "string"},
            },
        },
    },
    "head_check": {
        "name": "head_check",
        "description": "HTTP HEAD a URL. Returns {status, content_type, last_modified, error}.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
            },
        },
    },
    "firecrawl_scrape": {
        "name": "firecrawl_scrape",
        "description": "Fallback for JS-rendered pages. Returns {markdown, url}. Only available when MR_FIRECRAWL_API_KEY is set.",
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string"},
            },
        },
    },
}

# Per-command tool inclusion (§8.2)
_COMMAND_TOOLS: dict[str, list[str]] = {
    "discover": ["web_search", "web_fetch", "code_execution",
                 "seen_lookup", "wayback_check", "firecrawl_scrape"],
    "score": ["web_fetch", "code_execution",
              "wayback_check", "robots_check", "head_check"],
    "wishlist_expand": ["web_search", "web_fetch", "code_execution",
                        "seen_lookup", "firecrawl_scrape"],
}


def tools_for_command(command: str, firecrawl_available: bool) -> list[dict[str, Any]]:
    """Return the tool definitions list for `command`, in API request shape."""
    out: list[dict[str, Any]] = []
    for name in _COMMAND_TOOLS.get(command, []):
        if name == "firecrawl_scrape" and not firecrawl_available:
            continue
        if name in NATIVE_TOOL_DEFS:
            out.append(NATIVE_TOOL_DEFS[name])
        elif name in CUSTOM_TOOL_DEFS:
            out.append(CUSTOM_TOOL_DEFS[name])
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_tools.py -v`
Expected: PASS for all 6 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/tools.py tests/synth/test_tools.py
git commit -m "$(cat <<'EOF'
feat(synth): native + custom tool definitions per subcommand

Implements NATIVE_TOOL_DEFS (web_search/web_fetch/code_execution) and
CUSTOM_TOOL_DEFS (seen_lookup, wayback_check, robots_check, head_check,
firecrawl_scrape) per spec §8.2/§12.3. tools_for_command() composes
the API request tool list, omitting web_search for mr score and
firecrawl when MR_FIRECRAWL_API_KEY is unset.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 27: Custom tool dispatcher

**Spec sections:** §8.2 (tool dispatch), §12.3 (seen_lookup), §8.3 (custom tool implementations)

**Files:**
- Create: `mr/synth/dispatch.py`
- Create: `tests/synth/test_dispatch.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_dispatch.py`:

```python
import json
from pathlib import Path
from unittest.mock import patch

from mr.synth.dispatch import dispatch_tool_call


def test_seen_lookup_dispatched(tmp_path: Path):
    seen_path = tmp_path / "seen.jsonl"
    seen_path.write_text("")  # empty
    result = dispatch_tool_call(
        name="seen_lookup",
        args={"slug": "foo"},
        seen_path=seen_path,
    )
    assert "matches" in result
    assert "near_matches" in result


@patch("mr.synth.dispatch.wayback_check")
def test_wayback_dispatched(mock_wayback, tmp_path: Path):
    from datetime import date

    from mr.tools.wayback import WaybackResult
    mock_wayback.return_value = WaybackResult(count=42, first=date(2023, 1, 1), last=date(2026, 4, 30))
    result = dispatch_tool_call(
        name="wayback_check",
        args={"url": "https://example.com/"},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert result["count"] == 42
    assert result["first"] == "2023-01-01"


@patch("mr.synth.dispatch.robots_check")
def test_robots_dispatched(mock_robots, tmp_path: Path):
    from mr.tools.robots import RobotsResult
    mock_robots.return_value = RobotsResult(allowed=True, robots_url="https://example.com/robots.txt", error=None)
    result = dispatch_tool_call(
        name="robots_check",
        args={"url": "https://example.com/", "user_agent": "test"},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert result["allowed"] is True


def test_unknown_tool_returns_error(tmp_path: Path):
    result = dispatch_tool_call(
        name="bogus_tool",
        args={},
        seen_path=tmp_path / "seen.jsonl",
    )
    assert "error" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_dispatch.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/dispatch.py`**

```python
"""Dispatch custom tool calls received from the LLM.

Each model-emitted tool_use block with a custom-tool name is routed
to the matching mr.tools implementation; results are JSON-serialized
back to the model as a tool_result block.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from mr.tools.firecrawl import (
    FirecrawlNotConfigured,
    firecrawl_scrape,
    is_firecrawl_available,
)
from mr.tools.head import head_check
from mr.tools.robots import robots_check
from mr.tools.seen_lookup import seen_lookup
from mr.tools.wayback import wayback_check


def dispatch_tool_call(
    *,
    name: str,
    args: dict[str, Any],
    seen_path: Path,
) -> dict[str, Any]:
    """Run a custom tool by name. Returns a JSON-safe dict.

    Native tools (web_search, web_fetch, code_execution) are handled
    by Anthropic — never dispatched here.
    """
    try:
        if name == "seen_lookup":
            r = seen_lookup(
                seen_path=seen_path,
                slug=args.get("slug"),
                source_set=args.get("source_set"),
                lane_niche=tuple(args["lane_niche"]) if args.get("lane_niche") else None,
            )
            return asdict(r)

        if name == "wayback_check":
            r = wayback_check(args["url"])
            return {
                "count": r.count,
                "first": r.first.isoformat() if r.first else None,
                "last": r.last.isoformat() if r.last else None,
                "years": r.years,
            }

        if name == "robots_check":
            r = robots_check(args["url"], user_agent=args.get("user_agent", "moat-research/0.1"))
            return asdict(r)

        if name == "head_check":
            r = head_check(args["url"])
            return {
                "status": r.status,
                "content_type": r.content_type,
                "last_modified": r.last_modified.isoformat() if r.last_modified else None,
                "error": r.error,
            }

        if name == "firecrawl_scrape":
            if not is_firecrawl_available():
                return {"error": "firecrawl unavailable: MR_FIRECRAWL_API_KEY not set"}
            try:
                r = firecrawl_scrape(args["url"])
                return {"markdown": r.markdown, "url": r.url}
            except FirecrawlNotConfigured as e:
                return {"error": str(e)}

        return {"error": f"unknown tool: {name}"}
    except Exception as e:
        return {"error": f"{name} failed: {e}"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_dispatch.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/dispatch.py tests/synth/test_dispatch.py
git commit -m "$(cat <<'EOF'
feat(synth): custom tool dispatcher

Implements dispatch_tool_call() routing model-emitted tool_use blocks
to mr.tools implementations. Native tools (web_search/web_fetch/
code_execution) are handled by Anthropic and never dispatched here.
Errors are returned as {"error": ...} so the model can recover.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 28: Host-driven disqualifier verification

**Spec sections:** §6.4 (predicate-based verification, host-driven, off tool-turn budget)

**Files:**
- Create: `mr/synth/verify.py`
- Create: `tests/synth/test_verify.py`

- [ ] **Step 1: Write the failing tests**

`tests/synth/test_verify.py`:

```python
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from mr.lifecycle.frontmatter import Brief
from mr.synth.verify import (
    VerificationOutcome,
    verify_disqualifier_check,
)


def _brief_with_verdicts(
    sources: list[dict],
    verification_evidence: list[dict],
    disqualifier_verdicts: dict,
) -> Brief:
    return Brief(
        schema_version=1, title="x", slug="x", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=sources,
        verification_evidence=verification_evidence,
        disqualifier_verdicts=disqualifier_verdicts,
    )


def test_single_source_predicate_le_1():
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.flipped_to_fail("single_source")


def test_single_source_passes_with_two_distinct_hosts():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert not outcome.any_failure


def test_single_source_counter_evidence_excluded():
    """Per spec §6.4: counter_evidence does NOT count toward distinct hosts."""
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://archive.org/", "role": "counter_evidence", "archive_status": "none"},
        ],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    # Only "a.com" counts → fail
    assert outcome.flipped_to_fail("single_source")


@patch("mr.synth.verify.wayback_check")
def test_unrestricted_archives_predicate_meets_threshold(mock_wayback):
    from datetime import date as ddate
    from mr.tools.wayback import WaybackResult
    mock_wayback.return_value = WaybackResult(count=150, first=ddate(2020, 1, 1), last=ddate(2026, 1, 1))

    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {"id": "e1", "tool": "wayback_check", "args": {"url": "https://a.com/"}, "result": {"count": 47, "first": "2023-04-12", "last": "2026-04-30"}},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "unrestricted_archives": {
                "verdict": "pass",  # claimed pass, but re-execution shows count=150 ≥ 100 over 6 years
                "wayback_evidence_id": "e1",
                "publisher_archive_evidence_id": None,
            },
        },
    )
    cfg_dummy = type("Cfg", (), {"disqualifiers": {"unrestricted_archive_min_snapshots": 100, "unrestricted_archive_min_years": 3}})()
    outcome = verify_disqualifier_check(brief, cfg=cfg_dummy)
    # Re-execution reveals the brief should fail
    assert outcome.flipped_to_fail("unrestricted_archives")


def test_hardware_over_envelope_missing_keys_fails():
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"},
                 {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"}],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": {"peak_gpu_gb": 4.0}},  # missing keys
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.missing_hw_keys


def test_hardware_over_envelope_predicate_pass():
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"},
                 {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"}],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": {"peak_gpu_gb": 4.0, "sustained_ram_gb": 32, "storage_tb": 0.5}},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert not outcome.any_failure
    assert not outcome.missing_hw_keys


def test_hardware_over_envelope_predicate_fail():
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"},
                 {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"}],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": {"peak_gpu_gb": 16, "sustained_ram_gb": 32, "storage_tb": 0.5}},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    # peak_gpu_gb=16 > 8 → predicate says fail; brief claimed pass → flipped
    assert outcome.flipped_to_fail("hardware_over_envelope")


def test_fabrication_when_claim_inconsistent_with_evidence():
    """Brief claims pass but its OWN cited result fails the predicate."""
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"},
                 {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"}],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": {"peak_gpu_gb": 16, "sustained_ram_gb": 32, "storage_tb": 0.5}},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    # The brief's own cited result already fails → fabrication
    assert outcome.fabrication_detected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/synth/test_verify.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/synth/verify.py`**

```python
"""Host-driven disqualifier verification.

Spec §6.4: re-execute cited tools, evaluate predicates against new
results, detect fabrications (claim doesn't match own cited evidence).
Exempt from max_tool_turns; counts toward max_verification_calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from mr.lifecycle.frontmatter import Brief
from mr.tools.wayback import wayback_check


_HARDWARE_KEYS = ("peak_gpu_gb", "sustained_ram_gb", "storage_tb")
_HARDWARE_LIMITS = {"peak_gpu_gb": 8, "sustained_ram_gb": 250, "storage_tb": 17}


@dataclass
class VerificationOutcome:
    new_verdicts: dict[str, str] = field(default_factory=dict)
    flipped: dict[str, tuple[str, str]] = field(default_factory=dict)  # key → (old, new)
    missing_hw_keys: bool = False
    fabrication_detected: bool = False

    @property
    def any_failure(self) -> bool:
        return any(v == "fail" for v in self.new_verdicts.values())

    def flipped_to_fail(self, key: str) -> bool:
        return key in self.flipped and self.flipped[key][1] == "fail"


def _evidence_by_id(brief: Brief) -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in brief.verification_evidence}


def _distinct_primary_corroborating_hosts(brief: Brief) -> set[str]:
    out: set[str] = set()
    for s in brief.sources:
        if s.get("role") in ("primary", "corroborating"):
            host = urlparse(s.get("url", "")).hostname
            if host:
                out.add(host)
    return out


def verify_disqualifier_check(brief: Brief, cfg: Any) -> VerificationOutcome:
    """Re-evaluate predicates against re-executed evidence; detect fabrication."""
    outcome = VerificationOutcome()
    evidence = _evidence_by_id(brief)

    # single_source predicate
    hosts = _distinct_primary_corroborating_hosts(brief)
    new_single = "fail" if len(hosts) <= 1 else "pass"
    claimed = brief.disqualifier_verdicts.get("single_source", {}).get("verdict")
    outcome.new_verdicts["single_source"] = new_single
    if claimed and claimed != new_single:
        outcome.flipped["single_source"] = (claimed, new_single)

    # unrestricted_archives predicate (Wayback arm)
    ua = brief.disqualifier_verdicts.get("unrestricted_archives", {})
    if ua:
        wayback_evid_id = ua.get("wayback_evidence_id")
        publisher_evid_id = ua.get("publisher_archive_evidence_id")
        new_ua = "pass"
        if wayback_evid_id and wayback_evid_id in evidence:
            ev = evidence[wayback_evid_id]
            url = ev.get("args", {}).get("url")
            if url:
                wb = wayback_check(url)
                min_snapshots = getattr(cfg, "disqualifiers", {}).get("unrestricted_archive_min_snapshots", 100) if cfg else 100
                min_years = getattr(cfg, "disqualifiers", {}).get("unrestricted_archive_min_years", 3) if cfg else 3
                if wb.count >= min_snapshots and wb.years >= min_years:
                    new_ua = "fail"
        if publisher_evid_id and new_ua == "pass":
            # publisher arm: presence indicates failure (verification of content
            # happens in mr/score/verify_score.py via re-fetch + regex; here
            # we trust the claim if it's not Wayback-falsified)
            new_ua = "fail"
        outcome.new_verdicts["unrestricted_archives"] = new_ua
        claimed_ua = ua.get("verdict")
        if claimed_ua and claimed_ua != new_ua:
            outcome.flipped["unrestricted_archives"] = (claimed_ua, new_ua)

    # hardware_over_envelope predicate
    hw = brief.disqualifier_verdicts.get("hardware_over_envelope", {})
    if hw:
        evid_id = hw.get("evidence_id")
        if evid_id and evid_id in evidence:
            ev = evidence[evid_id]
            result = ev.get("result", {})
            if not all(k in result for k in _HARDWARE_KEYS):
                outcome.missing_hw_keys = True
            else:
                fail = any(result[k] > _HARDWARE_LIMITS[k] for k in _HARDWARE_KEYS)
                new_hw = "fail" if fail else "pass"
                outcome.new_verdicts["hardware_over_envelope"] = new_hw
                claimed_hw = hw.get("verdict")
                if claimed_hw and claimed_hw != new_hw:
                    outcome.flipped["hardware_over_envelope"] = (claimed_hw, new_hw)
                    # Fabrication: claim doesn't match brief's OWN cited evidence
                    outcome.fabrication_detected = True

    return outcome
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/synth/test_verify.py -v`
Expected: PASS for all 8 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/synth/verify.py tests/synth/test_verify.py
git commit -m "$(cat <<'EOF'
feat(synth): host-driven disqualifier verification (predicate-based)

Implements verify_disqualifier_check() per spec §6.4: re-evaluates
predicates against cited evidence, detects fabrication when the
brief's claimed verdict doesn't match its own evidence. Single_source
≤ 1 (zero-source guard); unrestricted_archives uses both Wayback +
publisher arms; hardware_over_envelope requires all three keys.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 8: Wishlist (schema, add, refresh, expand)

### Task 29: WISHLIST.md schema validation

**Spec sections:** §11 (WISHLIST schema), §15.1 (schema_version: 1 only)

**Files:**
- Create: `mr/wishlist/schema.py`
- Create: `mr/wishlist/wishlist_schema.json`
- Create: `tests/wishlist/__init__.py`
- Create: `tests/wishlist/test_schema.py`

- [ ] **Step 1: Write the failing tests**

`tests/wishlist/test_schema.py`:

```python
from pathlib import Path

import pytest

from mr.wishlist.schema import (
    Wishlist,
    WishlistError,
    WishlistSource,
    load_wishlist,
)


def test_load_empty(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    w = load_wishlist(p)
    assert w.sources == []


def test_load_with_sources(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: faa-notams
    url: https://notams.aim.faa.gov/
    lane: ephemeral_public
    rationale: NOTAMs expire.
    last_verified: 2026-05-07
    dead_link: false
""")
    w = load_wishlist(p)
    assert len(w.sources) == 1
    assert w.sources[0].id == "faa-notams"
    assert w.sources[0].lane == "ephemeral_public"
    assert w.sources[0].dead_link is False


def test_invalid_id_kebab(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: "not_kebab_case_with_underscores"
    url: https://example.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="id"):
        load_wishlist(p)


def test_duplicate_id_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: dup
    url: https://a.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
  - id: dup
    url: https://b.com/
    lane: niche_vertical
    rationale: y
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="duplicate"):
        load_wishlist(p)


def test_invalid_lane(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: foo
    url: https://example.com/
    lane: bogus
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="lane"):
        load_wishlist(p)


def test_missing_file_returns_empty(tmp_path: Path):
    w = load_wishlist(tmp_path / "absent.md")
    assert w.sources == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/wishlist/test_schema.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/wishlist/schema.py`**

```python
"""WISHLIST.md schema and loader.

Spec §11: top-level YAML with sources: list of {id, url, lane, rationale,
last_verified, last_attempted?, dead_link}.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VALID_LANES = frozenset({
    "ephemeral_public", "soon_to_be_restricted", "cross_source_fusion",
    "derived_artifact", "niche_vertical", "other",
})


class WishlistError(Exception):
    pass


@dataclass
class WishlistSource:
    id: str
    url: str
    lane: str
    rationale: str
    last_verified: date
    dead_link: bool = False
    last_attempted: date | None = None


@dataclass
class Wishlist:
    sources: list[WishlistSource] = field(default_factory=list)


def load_wishlist(path: Path) -> Wishlist:
    if not path.exists():
        return Wishlist()
    raw = yaml.safe_load(path.read_text()) or {}
    sources_raw = raw.get("sources") or []
    if not isinstance(sources_raw, list):
        raise WishlistError("sources: must be a list")

    seen_ids: set[str] = set()
    sources: list[WishlistSource] = []
    for s in sources_raw:
        if not isinstance(s, dict):
            raise WishlistError(f"source must be a mapping: {s!r}")
        for required in ("id", "url", "lane", "rationale", "last_verified"):
            if required not in s:
                raise WishlistError(f"source missing required key {required!r}: {s.get('id')}")
        sid = s["id"]
        if not _KEBAB_RE.match(sid):
            raise WishlistError(f"source id {sid!r} is not lowercase-kebab")
        if sid in seen_ids:
            raise WishlistError(f"duplicate source id: {sid!r}")
        seen_ids.add(sid)
        if s["lane"] not in _VALID_LANES:
            raise WishlistError(f"source {sid!r}: lane {s['lane']!r} not in {sorted(_VALID_LANES)}")

        last_verified = s["last_verified"]
        if isinstance(last_verified, str):
            last_verified = date.fromisoformat(last_verified)

        last_attempted = s.get("last_attempted")
        if isinstance(last_attempted, str):
            last_attempted = date.fromisoformat(last_attempted)

        sources.append(WishlistSource(
            id=sid, url=s["url"], lane=s["lane"], rationale=s["rationale"],
            last_verified=last_verified, dead_link=bool(s.get("dead_link", False)),
            last_attempted=last_attempted,
        ))

    return Wishlist(sources=sources)


def save_wishlist(path: Path, wishlist: Wishlist) -> None:
    """Write wishlist back to disk in canonical format."""
    payload: dict = {"sources": []}
    for s in wishlist.sources:
        entry = {
            "id": s.id,
            "url": s.url,
            "lane": s.lane,
            "rationale": s.rationale,
            "last_verified": s.last_verified.isoformat(),
            "dead_link": s.dead_link,
        }
        if s.last_attempted:
            entry["last_attempted"] = s.last_attempted.isoformat()
        payload["sources"].append(entry)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, default_flow_style=False))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/wishlist/test_schema.py -v`
Expected: PASS for all 6 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/wishlist/schema.py tests/wishlist/__init__.py tests/wishlist/test_schema.py
git commit -m "$(cat <<'EOF'
feat(wishlist): schema validator + load/save helpers

Implements WishlistSource dataclass, load_wishlist (validates
kebab id, closed-set lane, ISO date, no duplicates), and save_wishlist
per spec §11. last_attempted field carries refresh telemetry per spec.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 30: mr wishlist add — append validated source

**Spec sections:** §7 (mr wishlist add), §11 (append + validate + reject id collision)

**Files:**
- Create: `mr/wishlist/add.py`
- Create: `tests/wishlist/test_add.py`

- [ ] **Step 1: Write the failing tests**

`tests/wishlist/test_add.py`:

```python
from datetime import date
from pathlib import Path

import pytest

from mr.wishlist.add import add_source
from mr.wishlist.schema import WishlistError, load_wishlist


def test_add_to_empty(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    yaml_fragment = """id: faa-notams
url: https://notams.aim.faa.gov/
lane: ephemeral_public
rationale: NOTAMs expire.
last_verified: 2026-05-07
dead_link: false
"""
    add_source(p, yaml_fragment)
    w = load_wishlist(p)
    assert len(w.sources) == 1
    assert w.sources[0].id == "faa-notams"


def test_add_duplicate_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("""sources:
  - id: foo
    url: https://a.com/
    lane: niche_vertical
    rationale: x
    last_verified: 2026-05-07
    dead_link: false
""")
    with pytest.raises(WishlistError, match="duplicate"):
        add_source(p, """id: foo
url: https://b.com/
lane: niche_vertical
rationale: y
last_verified: 2026-05-07
dead_link: false
""")


def test_add_invalid_kebab_rejected(tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    p.write_text("sources: []\n")
    with pytest.raises(WishlistError, match="kebab"):
        add_source(p, """id: BadID
url: https://a.com/
lane: niche_vertical
rationale: x
last_verified: 2026-05-07
dead_link: false
""")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/wishlist/test_add.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/wishlist/add.py`**

```python
"""Append a source to WISHLIST.md after validation."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from mr.wishlist.schema import (
    Wishlist,
    WishlistError,
    WishlistSource,
    load_wishlist,
    save_wishlist,
)


def add_source(wishlist_path: Path, yaml_fragment: str) -> None:
    """Parse yaml_fragment, validate, and append to WISHLIST.md."""
    parsed = yaml.safe_load(yaml_fragment)
    if not isinstance(parsed, dict):
        raise WishlistError("yaml fragment must be a mapping")

    # Build a synthetic single-source Wishlist to leverage validator
    proposed_yaml = {"sources": [parsed]}
    tmp_text = yaml.safe_dump(proposed_yaml)

    # Validate by writing to a temp Wishlist
    tmp_path = wishlist_path.parent / ".wishlist-add.tmp.yaml"
    tmp_path.write_text(tmp_text)
    try:
        new_wishlist = load_wishlist(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    new_source = new_wishlist.sources[0]

    existing = load_wishlist(wishlist_path)
    if any(s.id == new_source.id for s in existing.sources):
        raise WishlistError(f"duplicate source id: {new_source.id!r}")

    existing.sources.append(new_source)
    save_wishlist(wishlist_path, existing)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/wishlist/test_add.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/wishlist/add.py tests/wishlist/test_add.py
git commit -m "$(cat <<'EOF'
feat(wishlist): mr wishlist add — append validated source

Implements add_source() per spec §11. Re-uses load_wishlist's
validator on a temp file (kebab id, closed-set lane, ISO date),
then appends if id is not duplicate.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 31: mr wishlist refresh — deterministic re-verify

**Spec sections:** §11 (refresh: HEAD + robots + Wayback; last_verified on 2xx; last_attempted always; dead_link on consecutive failures within window)

**Files:**
- Create: `mr/wishlist/refresh.py`
- Create: `tests/wishlist/test_refresh.py`

- [ ] **Step 1: Write the failing tests**

`tests/wishlist/test_refresh.py`:

```python
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from mr.tools.head import HeadResult
from mr.wishlist.refresh import refresh_wishlist
from mr.wishlist.schema import WishlistSource, save_wishlist, load_wishlist, Wishlist


def _fake_head_ok(_url: str, **_kwargs):
    return HeadResult(status=200, content_type="text/html", last_modified=None, error=None)


def _fake_head_404(_url: str, **_kwargs):
    return HeadResult(status=404, content_type=None, last_modified=None, error=None)


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_ok)
def test_2xx_updates_last_verified(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1), dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].last_verified == date(2026, 5, 7)
    assert w.sources[0].dead_link is False


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_4xx_does_not_update_last_verified(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1), dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].last_verified == date(2025, 1, 1)  # unchanged
    assert w.sources[0].last_attempted == date(2026, 5, 7)
    assert w.sources[0].dead_link is False  # only one failure so far


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_two_consecutive_failures_within_window_marks_dead(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1),
        last_attempted=date(2026, 5, 1),  # within 14 days of "today"
        dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].dead_link is True


@patch("mr.wishlist.refresh.head_check", side_effect=_fake_head_404)
def test_failures_outside_window_reset_counter(_mock_head, tmp_path: Path):
    p = tmp_path / "WISHLIST.md"
    save_wishlist(p, Wishlist(sources=[WishlistSource(
        id="a", url="https://a.com/", lane="niche_vertical", rationale="x",
        last_verified=date(2025, 1, 1),
        last_attempted=date(2025, 12, 1),  # > 14 days ago
        dead_link=False,
    )]))
    refresh_wishlist(p, today=date(2026, 5, 7), dead_link_window_days=14)
    w = load_wishlist(p)
    assert w.sources[0].dead_link is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/wishlist/test_refresh.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/wishlist/refresh.py`**

```python
"""mr wishlist refresh — deterministic re-verification of WISHLIST sources.

Spec §11: HEAD + robots + Wayback; last_verified only on 2xx;
last_attempted always; dead_link on consecutive failures within window.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from mr.tools.head import head_check
from mr.wishlist.schema import load_wishlist, save_wishlist


def refresh_wishlist(
    wishlist_path: Path,
    today: date,
    dead_link_window_days: int,
) -> None:
    """Re-verify every source. Update last_verified/last_attempted/dead_link."""
    w = load_wishlist(wishlist_path)

    for src in w.sources:
        result = head_check(src.url)
        is_ok = result.status is not None and 200 <= result.status < 300

        prev_attempted = src.last_attempted
        src.last_attempted = today

        if is_ok:
            src.last_verified = today
            src.dead_link = False
            continue

        # Failure path: check whether the *previous* attempt also failed within window
        if prev_attempted and prev_attempted >= today - timedelta(days=dead_link_window_days):
            # Consecutive failures within the window
            src.dead_link = True
        # Outside window or first failure: leave dead_link as-is (defaults False)

    save_wishlist(wishlist_path, w)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/wishlist/test_refresh.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Commit**

```bash
git add mr/wishlist/refresh.py tests/wishlist/test_refresh.py
git commit -m "$(cat <<'EOF'
feat(wishlist): refresh — deterministic re-verify with window-based dead_link

Implements refresh_wishlist() per spec §11. Updates last_verified
only on 2xx; last_attempted always; dead_link only on consecutive
failures within mr.yaml: status.dead_link_window_days (default 14).
Pure stdlib + httpx — no LLM call.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 32: mr wishlist expand — LLM-driven source proposal

**Spec sections:** §7, §11 (expand emits candidate entries to stdout for operator review), §8.4.1 (prompt requirements)

**Files:**
- Create: `mr/wishlist/expand.py`
- Create: `tests/wishlist/test_expand.py`

- [ ] **Step 1: Write the failing tests**

`tests/wishlist/test_expand.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch

from mr.wishlist.expand import format_proposal


def test_format_proposal_renders_yaml_blocks():
    proposals = [
        {"id": "foo-bar", "url": "https://example.com/",
         "lane": "niche_vertical", "rationale": "Foo bar baz."},
        {"id": "another-thing", "url": "https://other.com/",
         "lane": "ephemeral_public", "rationale": "Disappears nightly."},
    ]
    out = format_proposal(proposals)
    assert "id: foo-bar" in out
    assert "id: another-thing" in out
    # YAML-block boundaries between proposals
    assert "---" in out


def test_format_proposal_empty():
    out = format_proposal([])
    assert "no proposals" in out.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/wishlist/test_expand.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/wishlist/expand.py`**

```python
"""mr wishlist expand — LLM-driven source proposal.

Spec §11: emits candidate entries to stdout for operator review;
operator runs `mr wishlist add` on the ones they like. With --seed,
bootstraps from an empty list.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from mr.dedup.seen import is_stale, regenerate_seen
from mr.dedup.summary import build_summary_block
from mr.lifecycle.paths import RepoLayout
from mr.synth.budget import BudgetTracker
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.tools.firecrawl import is_firecrawl_available
from mr.util.config import Config
from mr.dedup.seen import read_seen


def format_proposal(proposals: list[dict[str, Any]]) -> str:
    """Render LLM-proposed sources as user-reviewable YAML blocks."""
    if not proposals:
        return "(no proposals — try a different lane or run again later)\n"
    out: list[str] = []
    for p in proposals:
        out.append("---")
        out.append(yaml.safe_dump(p, sort_keys=False, default_flow_style=False).rstrip())
    out.append("---")
    return "\n".join(out) + "\n"


def expand_wishlist(
    layout: RepoLayout,
    cfg: Config,
    *,
    seed: bool,
    budget_usd: float,
) -> str:
    """Run the LLM to propose new WISHLIST sources. Returns stdout text."""
    # Refresh seen.jsonl if stale (cold-corpus exception applies inside summary)
    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    summary = build_summary_block(read_seen(layout.seen_path))

    wishlist_text = layout.wishlist_path.read_text() if layout.wishlist_path.exists() else "sources: []\n"
    if seed:
        wishlist_text = "sources: []\n"

    system_text = load_prompt(layout.prompts_dir, "wishlist_expand")
    system_blocks = build_cached_blocks(
        system_text=system_text,
        wishlist_text=f"## Current WISHLIST\n```yaml\n{wishlist_text}\n```",
        seen_summary=summary,
    )

    client = SynthClient(cfg=cfg, command="wishlist_expand")
    tracker = BudgetTracker(
        cfg=cfg, command="wishlist_expand", model=client.model,
        budget_usd=budget_usd, costs_path=layout.costs_path,
    )

    tools = tools_for_command("wishlist_expand", firecrawl_available=is_firecrawl_available())

    user_msg = (
        "Propose 3-7 new WISHLIST sources following the diversity bias. "
        "For each, output a YAML block with id/url/lane/rationale. "
        "Use seen_lookup to verify novelty before final commit."
    )

    proposals = _run_loop(client, tracker, layout, system_blocks, user_msg, tools, cfg)
    return format_proposal(proposals)


def _run_loop(
    client: SynthClient,
    tracker: BudgetTracker,
    layout: RepoLayout,
    system_blocks: list[dict[str, Any]],
    user_text: str,
    tools: list[dict[str, Any]],
    cfg: Config,
) -> list[dict[str, Any]]:
    """Multi-turn tool-use loop. Extracts proposals from final assistant text."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    max_tokens = cfg.budgets["max_tokens_per_turn"]

    while True:
        tracker.note_tool_turn()
        tracker.check_wallclock()
        tracker.check_pre_call(input_tokens_estimate=10000, max_output_tokens=max_tokens)

        response = client.create_message(
            system_blocks=system_blocks,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)

        from datetime import datetime, timezone
        from mr.util.costs import CostRecord, append_cost
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(timezone.utc), command="wishlist_expand",
            model=client.model, input_tokens=usage["input_tokens"],
            cached_input_tokens=0, output_tokens=usage["output_tokens"],
            cache_hits=usage["cache_hits"], cache_misses=usage["cache_misses"],
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))

        tracker.note_turn_cache_status(missed=usage["cache_misses"] > 0, fingerprint="wishlist_expand_system")

        # Append assistant turn
        assistant_content = list(response.content)
        messages.append({"role": "assistant", "content": [_block_to_dict(b) for b in assistant_content]})

        if response.stop_reason != "tool_use":
            return _extract_proposals(assistant_content)

        tool_uses = [b for b in assistant_content if getattr(b, "type", None) == "tool_use"]
        tool_results = []
        for tu in tool_uses:
            result = dispatch_tool_call(name=tu.name, args=tu.input, seen_path=layout.seen_path)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": json.dumps(result),
            })
        messages.append({"role": "user", "content": tool_results})


def _block_to_dict(block: Any) -> dict[str, Any]:
    """Convert SDK content block back to JSON-safe dict."""
    btype = getattr(block, "type", None)
    if btype == "text":
        return {"type": "text", "text": block.text}
    if btype == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return {"type": btype}


def _extract_proposals(content: list[Any]) -> list[dict[str, Any]]:
    """Parse YAML blocks from the assistant's final text."""
    text_parts = [b.text for b in content if getattr(b, "type", None) == "text"]
    if not text_parts:
        return []
    full = "\n".join(text_parts)
    proposals: list[dict[str, Any]] = []
    for block in full.split("---"):
        block = block.strip()
        if not block:
            continue
        try:
            parsed = yaml.safe_load(block)
        except yaml.YAMLError:
            continue
        if isinstance(parsed, dict) and "id" in parsed:
            proposals.append(parsed)
    return proposals
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/wishlist/test_expand.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/wishlist/expand.py tests/wishlist/test_expand.py
git commit -m "$(cat <<'EOF'
feat(wishlist): expand — LLM proposes new sources for operator review

Implements expand_wishlist() per spec §11: runs the synth loop with
the wishlist_expand prompt, dispatches custom tools, extracts YAML
proposals from final assistant text, returns them as stdout-ready
text. Operator pipes through `mr wishlist add`. Cold-start with --seed
bootstraps from empty.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 9: Handoff (project, feature, adjacent_rejections)

### Task 33: Adjacent-rejection appendix

**Spec sections:** §13.3 (severity-ranked, capped at 3)

**Files:**
- Create: `mr/handoff/adjacent_rejections.py`
- Create: `tests/handoff/__init__.py`
- Create: `tests/handoff/test_adjacent_rejections.py`

- [ ] **Step 1: Write the failing tests**

`tests/handoff/test_adjacent_rejections.py`:

```python
from mr.dedup.seen import SeenEntry
from mr.handoff.adjacent_rejections import build_appendix


def _entry(slug: str, lane: str, niche_key: str, reason: str) -> SeenEntry:
    return SeenEntry(
        slug=slug, lane=lane, niche=niche_key, niche_key=niche_key,
        thesis=f"{slug} thesis.", source_set=["a.com"],
        disposition="rejected", auto_reject_reason=reason,
        date_created="2026-05-07",
    )


def test_appendix_severity_ranks_hard_disqualifier_first():
    entries = [
        _entry("a", "ephemeral_public", "alerts_aviation", "manual: bad fit"),
        _entry("b", "ephemeral_public", "alerts_aviation", "single source"),
        _entry("c", "ephemeral_public", "alerts_aviation", "defensibility ≤ 4"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    # tier 1 (single source) appears before tier 2 (defensibility) before tier 3 (manual)
    assert out.index("single source") < out.index("defensibility ≤ 4")
    assert out.index("defensibility ≤ 4") < out.index("manual: bad fit")


def test_appendix_capped_at_3():
    entries = [
        _entry(f"a{i}", "ephemeral_public", "alerts_aviation", "single source")
        for i in range(5)
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    # Only 3 slugs surface
    surfaces = [f"a{i}" for i in range(5) if f"a{i}" in out]
    assert len(surfaces) == 3


def test_appendix_filters_to_matching_lane_niche():
    entries = [
        _entry("a", "ephemeral_public", "alerts_aviation", "single source"),
        _entry("b", "ephemeral_public", "different_niche", "single source"),
        _entry("c", "niche_vertical", "alerts_aviation", "single source"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    assert "a" in out
    assert "b" not in out
    assert "c" not in out


def test_appendix_empty_when_no_matches():
    entries = [
        _entry("a", "ephemeral_public", "different", "single source"),
    ]
    out = build_appendix(entries, target_lane="ephemeral_public",
                        target_niche_key="alerts_aviation")
    assert "(none)" in out.lower() or "no adjacent" in out.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/handoff/test_adjacent_rejections.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/handoff/adjacent_rejections.py`**

```python
"""Adjacent-rejection appendix for hand-off prompts.

Spec §13.3: matching (lane, niche_key) tuple, capped at 3, severity-ranked
(tier 1 hard disqualifier > tier 2 floor > tier 3 manual).
"""
from __future__ import annotations

from typing import Sequence

from mr.dedup.seen import SeenEntry
from mr.scoring.auto_reject import severity_tier

_CAP = 3


def build_appendix(
    entries: Sequence[SeenEntry],
    *,
    target_lane: str,
    target_niche_key: str,
) -> str:
    """Render the adjacent-rejection appendix for a graduating brief."""
    matching = [
        e for e in entries
        if e.disposition == "rejected"
        and e.lane == target_lane
        and e.niche_key == target_niche_key
        and e.auto_reject_reason is not None
    ]

    def _rank(e: SeenEntry) -> int:
        tier = severity_tier(e.auto_reject_reason)
        return tier if tier is not None else 99

    matching.sort(key=lambda e: (_rank(e), e.date_created), reverse=False)
    top = matching[:_CAP]

    if not top:
        return "## Adjacent rejections (same lane, same niche)\n\n(none)\n"

    lines = ["## Adjacent rejections (same lane, same niche — known dead-ends)", ""]
    for e in top:
        lines.append(f"- **{e.slug}** — `{e.auto_reject_reason}` — {e.thesis}")
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/handoff/test_adjacent_rejections.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/handoff/adjacent_rejections.py tests/handoff/__init__.py tests/handoff/test_adjacent_rejections.py
git commit -m "$(cat <<'EOF'
feat(handoff): adjacent-rejection appendix (severity-ranked, cap 3)

Implements build_appendix() per spec §13.3. Filters seen entries to
matching (lane, niche_key); ranks by severity_tier; caps at 3.
Tier 1 (hard disqualifiers) before tier 2 (floor) before tier 3 (manual).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 34: Project hand-off prompt builder

**Spec sections:** §13.1 (delivery_form: project init prompt + hardware envelope)

**Files:**
- Create: `mr/handoff/project.py`
- Create: `tests/handoff/test_project.py`

- [ ] **Step 1: Write the failing tests**

`tests/handoff/test_project.py`:

```python
from datetime import date
from pathlib import Path

from mr.handoff.project import build_project_handoff
from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config, DEFAULT_CONFIG


def _brief() -> Brief:
    return Brief(
        schema_version=1, title="FAA NOTAMs", slug="faa-notams",
        lane="ephemeral_public", niche="aviation alerts",
        niche_key="alerts_aviation", delivery_form="project",
        date_created=date(2026, 5, 4),
        sources=[{"url": "https://notams.aim.faa.gov/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.13},
        body="## Thesis\nNOTAMs expire and are not archived by the FAA.\n",
    )


def test_project_handoff_includes_hardware_envelope():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="(no adjacent rejections)")
    assert "Xeon E5-2698 v4" in out
    assert "250 GB" in out
    assert "P4" in out


def test_project_handoff_includes_brief_body():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "FAA NOTAMs" in out
    assert "NOTAMs expire" in out


def test_project_handoff_first_action_prompt():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "First action" in out
    assert "CLAUDE.md" in out


def test_project_handoff_includes_appendix():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="## Adjacent rejections\n(none)")
    assert "Adjacent rejections" in out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/handoff/test_project.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `mr/handoff/project.py`**

```python
"""Hand-off prompt builder for delivery_form: project (fresh project init).

Spec §13.1.
"""
from __future__ import annotations

from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config


def build_project_handoff(brief: Brief, *, cfg: Config, adjacent_appendix: str) -> str:
    """Render the project init-prompt to stdout for `mr graduate`."""
    hw = cfg.hardware
    return f"""You are starting {brief.slug}. Brief follows verbatim.

Hardware envelope:
  CPU: {hw['cpu']}
  RAM: {hw['ram_gb']} GB
  GPU: {hw['gpu']} — plan for ≤4 GB sustained
  Storage: {hw['storage_tb']} TB NAS
  Network: {hw['network']}

Brief:
{_brief_markdown(brief)}

{adjacent_appendix}

First action: read CLAUDE.md if present, then ask 1–3 clarifying questions before scaffolding.
"""


def _brief_markdown(brief: Brief) -> str:
    """Render the brief body with frontmatter context."""
    scores = brief.scores or {}
    score_line = (
        f"Scores: defensibility={scores.get('defensibility', '?')} | "
        f"financial={scores.get('financial', '?')} | "
        f"implementation={scores.get('implementation', '?')} | "
        f"hardware={scores.get('hardware', '?')} | "
        f"composite={scores.get('composite', '?')}"
    )
    src_lines = "\n".join(f"  - {s.get('url', '?')} ({s.get('role', '?')})" for s in brief.sources)
    return f"""# {brief.title}

Lane: {brief.lane}  ·  Niche: {brief.niche}  ·  Date: {brief.date_created}
{score_line}
Sources:
{src_lines}

{brief.body}"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/handoff/test_project.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/handoff/project.py tests/handoff/test_project.py
git commit -m "$(cat <<'EOF'
feat(handoff): project init-prompt builder

Implements build_project_handoff() per spec §13.1. Includes hardware
envelope (cpu/ram/gpu/storage/network from mr.yaml), brief body,
adjacent-rejection appendix, and the standard first-action prompt
(read CLAUDE.md, ask 1-3 clarifying questions).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 35: Feature hand-off prompt builder

**Spec sections:** §13.2 (delivery_form: feature, patch proposal for parent_project)

**Files:**
- Create: `mr/handoff/feature.py`
- Create: `tests/handoff/test_feature.py`

- [ ] **Step 1: Write the failing tests**

`tests/handoff/test_feature.py`:

```python
from datetime import date

from mr.handoff.feature import build_feature_handoff
from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config, DEFAULT_CONFIG


def _brief() -> Brief:
    return Brief(
        schema_version=1, title="Aviation alerts in SoMD",
        slug="aviation-alerts-somd",
        lane="ephemeral_public", niche="aviation alerts",
        niche_key="alerts_aviation", delivery_form="feature",
        parent_project="somd-cameras",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://notams.aim.faa.gov/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.13},
        body="## Thesis\nAdd aviation NOTAMs to somd-cameras feed.\n",
    )


def test_feature_handoff_mentions_parent_project():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_feature_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "somd-cameras" in out
    assert "extending" in out.lower() or "feature" in out.lower()


def test_feature_handoff_first_action_reads_existing_repo():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_feature_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "CLAUDE.md" in out
    # Per spec §13.2: read existing arch + don't create files yet
    assert "do not create new files" in out.lower()
    assert "feature branch" in out.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/handoff/test_feature.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/handoff/feature.py`**

```python
"""Hand-off prompt builder for delivery_form: feature (patch proposal).

Spec §13.2.
"""
from __future__ import annotations

from mr.handoff.project import _brief_markdown
from mr.lifecycle.frontmatter import Brief
from mr.util.config import Config


def build_feature_handoff(brief: Brief, *, cfg: Config, adjacent_appendix: str) -> str:
    """Render the feature patch-proposal prompt for `mr graduate`."""
    if not brief.parent_project:
        raise ValueError(f"feature brief {brief.slug!r} missing parent_project")
    hw = cfg.hardware
    return f"""You are extending the `{brief.parent_project}` repo with a new feature. Brief follows verbatim.

Hardware envelope:
  CPU: {hw['cpu']}
  RAM: {hw['ram_gb']} GB
  GPU: {hw['gpu']} — plan for ≤4 GB sustained
  Storage: {hw['storage_tb']} TB NAS
  Network: {hw['network']}

Brief:
{_brief_markdown(brief)}

{adjacent_appendix}

First action: read this repo's CLAUDE.md, the existing architecture, and any modules relevant to the brief. Do not create new files until you have understood the current shape. Propose a feature branch name and a draft PR description before any code edits.
"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/handoff/test_feature.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/handoff/feature.py tests/handoff/test_feature.py
git commit -m "$(cat <<'EOF'
feat(handoff): feature patch-proposal prompt builder

Implements build_feature_handoff() per spec §13.2. Targets the
brief's parent_project, instructs Claude to read existing CLAUDE.md
and architecture before any edits, and to propose feature branch +
draft PR description.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 10: CLI commands

### Task 36: mr init — bootstrap dirs, mr.yaml, prompts/

**Spec sections:** §7 (mr init), §13.1.2.4 (mr init creates state)

**Files:**
- Create: `mr/cli/init.py`
- Modify: `mr/cli/main.py:add init subcommand`
- Create: `tests/cli/__init__.py`
- Create: `tests/cli/test_init.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_init.py`:

```python
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app

runner = CliRunner()


def test_init_creates_dirs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    for d in ("candidates", "scored", "rejected", "approved", "graduated"):
        assert (tmp_path / d).is_dir()
    assert (tmp_path / ".moat-research").is_dir()
    assert (tmp_path / "prompts").is_dir()


def test_init_creates_default_mr_yaml(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "mr.yaml").exists()
    text = (tmp_path / "mr.yaml").read_text()
    assert "schema_version: 1" in text


def test_init_creates_default_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "WISHLIST.md").exists()
    assert "sources: []" in (tmp_path / "WISHLIST.md").read_text()


def test_init_idempotent(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    # Modify mr.yaml; second init should not clobber
    (tmp_path / "mr.yaml").write_text("schema_version: 1\nweights:\n  defensibility: 0.50\n")
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "0.50" in (tmp_path / "mr.yaml").read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_init.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/init.py` and wire in `mr/cli/main.py`**

`mr/cli/init.py`:

```python
"""mr init — bootstrap repo layout, mr.yaml, prompts/, WISHLIST.md."""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

from mr.lifecycle.paths import RepoLayout
from mr.util.config import DEFAULT_CONFIG


def init(root: Path) -> None:
    """Create lifecycle dirs, .moat-research/, prompts/, and seed defaults."""
    layout = RepoLayout(root)
    layout.ensure_dirs()

    if not layout.config_path.exists():
        layout.config_path.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))
        typer.echo(f"created {layout.config_path}")

    if not layout.wishlist_path.exists():
        layout.wishlist_path.write_text("sources: []\n")
        typer.echo(f"created {layout.wishlist_path}")

    # Prompt placeholders — actual prompts are written in Phase 11
    for name in ("discover", "score", "wishlist_expand"):
        target = layout.prompts_dir / f"{name}.md"
        if not target.exists():
            target.write_text(f"# {name} prompt\n\n(replace with the shipped {name}.md)\n")
            typer.echo(f"created {target}")

    typer.echo("mr init: done")
```

Modify `mr/cli/main.py` to add the init command:

```python
"""Entry point for the `mr` CLI."""
from pathlib import Path

import typer

from mr.cli import init as init_module

app = typer.Typer(
    name="mr",
    help="Discover, score, and graduate data-moat opportunities.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the installed mr version."""
    from mr import __version__
    typer.echo(f"mr {__version__}")


@app.command(name="init")
def init_cmd(
    root: Path = typer.Argument(Path.cwd(), help="Repo root (default: cwd)"),
) -> None:
    """Bootstrap dirs, mr.yaml, prompts/, WISHLIST.md (idempotent)."""
    init_module.init(root)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_init.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/init.py mr/cli/main.py tests/cli/__init__.py tests/cli/test_init.py
git commit -m "$(cat <<'EOF'
feat(cli): mr init — bootstrap repo layout

Implements mr init per spec §7. Creates lifecycle dirs (candidates/
scored/rejected/approved/graduated), .moat-research/ state dir,
prompts/ with placeholders, mr.yaml with DEFAULT_CONFIG (if absent),
WISHLIST.md with empty sources list. Idempotent: never overwrites.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 37: mr status

**Spec sections:** §7 (status: counts + top-3 + stale-approved warning + most-mined hosts), §8.5 (mr status flags other-lane briefs)

**Files:**
- Create: `mr/cli/status.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_status.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_status.py`:

```python
from datetime import date, timedelta
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _scaffold(tmp_path: Path) -> RepoLayout:
    runner.invoke(app, ["init", str(tmp_path)])
    return RepoLayout(tmp_path)


def _write_brief(layout: RepoLayout, dirname: str, slug: str, *, lane="ephemeral_public",
                 days_old: int = 0) -> Path:
    target = layout.root / dirname / f"20260507-{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title=slug, slug=slug, lane=lane,
        niche="x", niche_key="x", delivery_form="project",
        date_created=date.today() - timedelta(days=days_old),
        sources=[{"url": f"https://{slug}.com/", "role": "primary", "archive_status": "none"}],
    )
    write_brief(target, brief, body=f"## Thesis\n{slug}.\n")
    return target


def test_status_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "candidates: 0" in result.stdout
    assert "scored: 0" in result.stdout


def test_status_counts(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    _write_brief(layout, "candidates", "a")
    _write_brief(layout, "candidates", "b")
    _write_brief(layout, "scored", "c")
    result = runner.invoke(app, ["status"])
    assert "candidates: 2" in result.stdout
    assert "scored: 1" in result.stdout


def test_status_stale_approved_warning(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    _write_brief(layout, "approved", "old", days_old=120)  # > 90 days
    result = runner.invoke(app, ["status"])
    assert "stale" in result.stdout.lower()
    assert "old" in result.stdout


def test_status_other_lane_flagged(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    # Brief in `other` lane requires lane_note — we skip writing one for the test;
    # so write directly via write_brief with lane_note set.
    target = layout.candidates / "20260507-explore.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="explore", slug="explore", lane="other",
        lane_note="novel moat shape",
        niche="weird", niche_key="weird", delivery_form="project",
        date_created=date.today(),
        sources=[{"url": "https://x.com/", "role": "primary", "archive_status": "none"}],
    )
    write_brief(target, brief, body="## Thesis\nx.\n")
    result = runner.invoke(app, ["status"])
    assert "other" in result.stdout.lower() or "exploration" in result.stdout.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_status.py -v`
Expected: FAIL (status command not yet wired).

- [ ] **Step 3: Implement `mr/cli/status.py`**

```python
"""mr status — counts per dir, stale-approved warning, top-mined hosts."""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import typer

from mr.dedup.seen import is_stale, regenerate_seen, read_seen
from mr.lifecycle.paths import RepoLayout
from mr.util.config import load_config


def status(root: Path) -> None:
    """Print lifecycle counts, stale-approved warnings, exploration flags."""
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    entries = read_seen(layout.seen_path)

    # Counts per disposition
    counts = Counter(e.disposition for e in entries)
    typer.echo("## Lifecycle counts")
    for disposition in ("candidate", "scored", "approved", "rejected", "graduated"):
        typer.echo(f"  {disposition}s: {counts.get(disposition, 0)}")

    # Stale-approved warning
    stale_days = cfg.status.get("stale_approved_days", 90)
    today = date.today()
    stale_threshold = today - timedelta(days=stale_days)
    stale_briefs = [
        e for e in entries
        if e.disposition == "approved"
        and date.fromisoformat(e.date_created) < stale_threshold
    ]
    if stale_briefs:
        typer.echo(f"\n## Stale approved (older than {stale_days} days)")
        for e in stale_briefs:
            typer.echo(f"  {e.slug} (created {e.date_created})")

    # Other-lane (exploration) flag
    other_briefs = [e for e in entries if e.lane == "other"]
    if other_briefs:
        typer.echo(f"\n## Exploration (lane: other) — {len(other_briefs)} briefs")
        for e in other_briefs[:3]:
            typer.echo(f"  {e.slug} ({e.disposition})")

    # Top-3 most-mined hosts
    host_counts: Counter[str] = Counter()
    for e in entries:
        for h in e.source_set:
            host_counts[h] += 1
    if host_counts:
        typer.echo("\n## Top-3 most-mined hosts")
        for host, c in host_counts.most_common(3):
            typer.echo(f"  {host}: {c}")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import status as status_module


@app.command(name="status")
def status_cmd(
    root: Path = typer.Argument(Path.cwd(), help="Repo root"),
) -> None:
    """Show lifecycle counts and operator-relevant warnings."""
    status_module.status(root)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_status.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/status.py mr/cli/main.py tests/cli/test_status.py
git commit -m "$(cat <<'EOF'
feat(cli): mr status — counts, stale-approved, exploration flags

Implements mr status per spec §7 + §8.5. Counts per disposition,
stale-approved warning (configurable days; default 90), exploration
(lane: other) flag, top-3 most-mined hosts. Auto-regenerates
seen.jsonl if stale before reporting.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 38: mr promote — scored → approved

**Files:**
- Create: `mr/cli/promote.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_promote.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_promote.py`:

```python
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup(tmp_path: Path) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.scored / "07221-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 7, "hardware": 8, "composite": 7.221},
    )
    write_brief(src, brief, body="## Thesis\nFoo.\n")
    return layout, src


def test_promote_moves_to_approved(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["promote", str(src)])
    assert result.exit_code == 0
    assert not src.exists()
    assert (layout.approved / "07221-20260507-foo.md").exists()


def test_promote_nonexistent_fails(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["promote", str(tmp_path / "scored" / "absent.md")])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_promote.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/promote.py`**

```python
"""mr promote — move a scored brief to approved/."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def promote(src_path: Path, root: Path) -> None:
    layout = RepoLayout(root)
    if not src_path.exists():
        typer.echo(f"error: {src_path} not found", err=True)
        raise typer.Exit(code=2)
    if src_path.parent.resolve() != layout.scored.resolve():
        typer.echo(f"error: {src_path} is not in scored/", err=True)
        raise typer.Exit(code=2)
    dst = layout.approved / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2)
    typer.echo(f"promoted: {dst}")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import promote as promote_module


@app.command(name="promote")
def promote_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Move a scored brief to approved/."""
    promote_module.promote(path, root)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_promote.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/promote.py mr/cli/main.py tests/cli/test_promote.py
git commit -m "$(cat <<'EOF'
feat(cli): mr promote — scored → approved

Implements mr promote per spec §6.2 transition table. Refuses to
promote files outside scored/. Uses os.replace for atomicity.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 39: mr reject — scored → rejected with operator reason

**Spec sections:** §6.2 (mr reject writes auto_reject_reason: "manual: <text>"), §13.3 tier 3

**Files:**
- Create: `mr/cli/reject.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_reject.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_reject.py`:

```python
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, read_brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup(tmp_path: Path) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.scored / "06000-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 6, "financial": 6, "implementation": 6, "hardware": 6, "composite": 6.0},
    )
    write_brief(src, brief, body="## Thesis\nFoo.\n")
    return layout, src


def test_reject_writes_manual_reason(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["reject", str(src), "--reason", "not the right time"])
    assert result.exit_code == 0
    moved = layout.rejected / "06000-20260507-foo.md"
    assert moved.exists()
    b = read_brief(moved)
    assert b.scores["auto_reject_reason"] == "manual: not the right time"


def test_reject_without_reason_uses_blank(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["reject", str(src)])
    assert result.exit_code == 0
    moved = layout.rejected / "06000-20260507-foo.md"
    b = read_brief(moved)
    assert b.scores["auto_reject_reason"].startswith("manual:")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_reject.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/reject.py`**

```python
"""mr reject — move scored brief to rejected/ with operator reason."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.lifecycle.frontmatter import read_brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def reject(src_path: Path, root: Path, reason: str | None) -> None:
    layout = RepoLayout(root)
    if src_path.parent.resolve() != layout.scored.resolve():
        typer.echo(f"error: {src_path} is not in scored/", err=True)
        raise typer.Exit(code=2)

    brief = read_brief(src_path)
    reason_text = reason.strip() if reason else "(no reason provided)"
    if brief.scores is None:
        brief.scores = {}
    brief.scores["auto_reject_reason"] = f"manual: {reason_text}"
    write_brief(src_path, brief)

    dst = layout.rejected / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2)
    typer.echo(f"rejected: {dst}")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import reject as reject_module


@app.command(name="reject")
def reject_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    reason: str = typer.Option(None, "--reason", help="Operator's rejection reason"),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Move a scored brief to rejected/ with optional reason."""
    reject_module.reject(path, root, reason)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_reject.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/reject.py mr/cli/main.py tests/cli/test_reject.py
git commit -m "$(cat <<'EOF'
feat(cli): mr reject — manual rejection with operator reason

Implements mr reject per spec §6.2 + §5.5. Writes
scores.auto_reject_reason: "manual: <text>" before the move so
§13.3 severity classifier (tier 3) and seen.jsonl regen pick it up.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 40: mr graduate — emit hand-off, move to graduated/, idempotent

**Spec sections:** §13.4 (idempotent + durable .handoff.txt sidecar), §13.1/13.2 (delivery_form branching)

**Files:**
- Create: `mr/cli/graduate.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_graduate.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_graduate.py`:

```python
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup_approved(tmp_path: Path, *, delivery_form: str = "project",
                    parent: str | None = None) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.approved / "07500-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="aviation alerts", niche_key="alerts_aviation",
        delivery_form=delivery_form, parent_project=parent,
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.5},
    )
    write_brief(src, brief, body="## Thesis\nFoo bar baz.\n")
    return layout, src


def test_graduate_project_emits_init_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path)
    result = runner.invoke(app, ["graduate", str(src)])
    assert result.exit_code == 0
    assert "You are starting foo" in result.stdout
    assert "Xeon E5-2698 v4" in result.stdout
    moved = layout.graduated / src.name
    assert moved.exists()
    assert (layout.graduated / "foo.handoff.txt").exists()


def test_graduate_feature_emits_patch_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path, delivery_form="feature", parent="somd-cameras")
    result = runner.invoke(app, ["graduate", str(src)])
    assert result.exit_code == 0
    assert "extending the `somd-cameras` repo" in result.stdout


def test_graduate_idempotent_on_already_graduated(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path)
    runner.invoke(app, ["graduate", str(src)])
    moved = layout.graduated / src.name
    # Second graduate on the moved file: should re-emit, not move
    result = runner.invoke(app, ["graduate", str(moved)])
    assert result.exit_code == 0
    assert "You are starting foo" in result.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_graduate.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/graduate.py`**

```python
"""mr graduate — emit hand-off prompt and move approved → graduated."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.handoff.adjacent_rejections import build_appendix
from mr.handoff.feature import build_feature_handoff
from mr.handoff.project import build_project_handoff
from mr.lifecycle.frontmatter import read_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief
from mr.util.config import load_config


def graduate(src_path: Path, root: Path) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    in_approved = src_path.parent.resolve() == layout.approved.resolve()
    in_graduated = src_path.parent.resolve() == layout.graduated.resolve()

    if not in_approved and not in_graduated:
        typer.echo(f"error: {src_path} is not in approved/ or graduated/", err=True)
        raise typer.Exit(code=2)

    brief = read_brief(src_path)
    appendix = build_appendix(
        read_seen(layout.seen_path),
        target_lane=brief.lane,
        target_niche_key=brief.niche_key,
    )

    if brief.delivery_form == "feature":
        prompt = build_feature_handoff(brief, cfg=cfg, adjacent_appendix=appendix)
    else:
        prompt = build_project_handoff(brief, cfg=cfg, adjacent_appendix=appendix)

    # Idempotency: if already in graduated/, just emit and exit
    if in_graduated:
        typer.echo(prompt)
        return

    # Otherwise: move + write durable sidecar + emit
    dst = layout.graduated / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2)

    sidecar = layout.graduated / f"{brief.slug}.handoff.txt"
    sidecar.write_text(prompt)
    typer.echo(prompt)
```

Add to `mr/cli/main.py`:

```python
from mr.cli import graduate as graduate_module


@app.command(name="graduate")
def graduate_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Emit hand-off prompt and move approved → graduated. Idempotent."""
    graduate_module.graduate(path, root)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_graduate.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/graduate.py mr/cli/main.py tests/cli/test_graduate.py
git commit -m "$(cat <<'EOF'
feat(cli): mr graduate — hand-off + idempotent move

Implements mr graduate per spec §13. Branches on delivery_form
(project vs. feature), builds adjacent-rejection appendix from
seen.jsonl, writes graduated/<slug>.handoff.txt sidecar for durable
recovery, idempotent on already-graduated briefs.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 41: mr discover — generate candidates

**Spec sections:** §7 (mr discover, four-tier budget, cold-corpus preflight), §8 (synth)

**Files:**
- Create: `mr/cli/discover.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_discover.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_discover.py`:

```python
from datetime import date
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def test_discover_aborts_on_empty_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1", "--budget", "1.0"])
    assert result.exit_code != 0
    assert "WISHLIST" in result.stdout or "WISHLIST" in result.stderr


def test_discover_aborts_when_anthropic_api_key_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    # Seed WISHLIST with 5+ sources to pass cold-corpus preflight
    layout = RepoLayout(tmp_path)
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1", "--budget", "1.0"])
    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.stdout or "ANTHROPIC_API_KEY" in result.stderr


@patch("mr.cli.discover.run_discover_loop")
def test_discover_dispatches_to_loop(mock_loop, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "3", "--budget", "5.0"])
    assert result.exit_code == 0
    mock_loop.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_discover.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/discover.py`**

```python
"""mr discover — generate candidate briefs from WISHLIST + live web tools."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import typer
import yaml

from mr.dedup.niche_key import resolve_niche_key
from mr.dedup.seen import is_stale, regenerate_seen, read_seen
from mr.dedup.summary import build_summary_block
from mr.lifecycle.filename import candidate_filename, resolve_collision
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.synth.budget import BudgetExceeded, BudgetTracker, cold_corpus_preflight, worst_case_ceiling
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.tools.firecrawl import is_firecrawl_available
from mr.util.config import Config, load_config
from mr.util.costs import CostRecord, append_cost
from mr.util.lock import exclusive_lock
from mr.util.slug import slugify


def discover(root: Path, lane: str | None, n: int, budget: float) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    cold_corpus_preflight(layout.wishlist_path)

    # Tier 1 worst-case ceiling
    cli = SynthClient(cfg=cfg, command="discover")  # may raise if no API key
    ceiling = worst_case_ceiling(cfg, "discover", cli.model)
    if ceiling > budget:
        typer.echo(f"error: tier-1 ceiling ${ceiling:.2f} exceeds budget ${budget:.2f}", err=True)
        raise typer.Exit(code=2)

    with exclusive_lock(layout.lock_path):
        if is_stale(layout):
            regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

        run_discover_loop(layout=layout, cfg=cfg, lane=lane, n=n, budget=budget, client=cli)


def run_discover_loop(
    *,
    layout: RepoLayout,
    cfg: Config,
    lane: str | None,
    n: int,
    budget: float,
    client: SynthClient,
) -> None:
    """Drive the synth loop and write candidates to candidates/."""
    summary = build_summary_block(read_seen(layout.seen_path))
    wishlist_text = layout.wishlist_path.read_text()
    system_text = load_prompt(layout.prompts_dir, "discover")

    system_blocks = build_cached_blocks(
        system_text=system_text,
        wishlist_text=f"## Current WISHLIST\n```yaml\n{wishlist_text}\n```",
        seen_summary=summary,
    )

    tracker = BudgetTracker(
        cfg=cfg, command="discover", model=client.model,
        budget_usd=budget, costs_path=layout.costs_path,
    )
    tools = tools_for_command("discover", firecrawl_available=is_firecrawl_available())

    lane_clause = f"Generate exactly {n} candidates in lane `{lane}`." if lane else \
                  f"Generate exactly {n} candidates, distributing across underrepresented (lane, niche_key) cells."
    user_msg = (
        f"{lane_clause} For each, output the full YAML frontmatter + body per spec §6.4. "
        f"Wrap each candidate in fenced ```yaml-brief blocks so the runner can extract them. "
        f"Use seen_lookup before commit; populate verification_evidence; honor the affirm/avoid "
        f"interest filter; obey the diversity bias."
    )

    candidates = _run_loop(
        client=client, tracker=tracker, layout=layout,
        system_blocks=system_blocks, user_text=user_msg,
        tools=tools, cfg=cfg,
    )

    _write_candidates(candidates, layout=layout, cfg=cfg)


def _run_loop(
    *, client: SynthClient, tracker: BudgetTracker, layout: RepoLayout,
    system_blocks: list[dict[str, Any]], user_text: str,
    tools: list[dict[str, Any]], cfg: Config,
) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    max_tokens = cfg.budgets["max_tokens_per_turn"]

    while True:
        tracker.note_tool_turn()
        tracker.check_wallclock()
        tracker.check_pre_call(input_tokens_estimate=12000, max_output_tokens=max_tokens)

        response = client.create_message(
            system_blocks=system_blocks, messages=messages, tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(timezone.utc), command="discover", model=client.model,
            input_tokens=usage["input_tokens"], cached_input_tokens=0,
            output_tokens=usage["output_tokens"],
            cache_hits=usage["cache_hits"], cache_misses=usage["cache_misses"],
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
        tracker.note_turn_cache_status(missed=usage["cache_misses"] > 0, fingerprint="discover_system")

        assistant = list(response.content)
        messages.append({"role": "assistant", "content": [_block_to_dict(b) for b in assistant]})

        if response.stop_reason != "tool_use":
            return _extract_candidates(assistant)

        tool_uses = [b for b in assistant if getattr(b, "type", None) == "tool_use"]
        tool_results = []
        for tu in tool_uses:
            result = dispatch_tool_call(name=tu.name, args=tu.input, seen_path=layout.seen_path)
            tool_results.append({
                "type": "tool_result", "tool_use_id": tu.id,
                "content": json.dumps(result),
            })
        messages.append({"role": "user", "content": tool_results})


def _block_to_dict(block: Any) -> dict[str, Any]:
    btype = getattr(block, "type", None)
    if btype == "text":
        return {"type": "text", "text": block.text}
    if btype == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return {"type": btype}


def _extract_candidates(content: list[Any]) -> list[dict[str, Any]]:
    """Parse ```yaml-brief fenced blocks from the assistant's final text."""
    text_parts = [b.text for b in content if getattr(b, "type", None) == "text"]
    if not text_parts:
        return []
    full = "\n".join(text_parts)
    candidates: list[dict[str, Any]] = []

    fence = "```yaml-brief"
    end_fence = "```"
    pos = 0
    while True:
        start = full.find(fence, pos)
        if start < 0:
            break
        body_start = full.find("\n", start) + 1
        body_end = full.find(end_fence, body_start)
        if body_end < 0:
            break
        block_text = full[body_start:body_end].strip()
        try:
            parsed = yaml.safe_load(block_text)
        except yaml.YAMLError:
            pos = body_end + len(end_fence)
            continue
        if isinstance(parsed, dict) and "frontmatter" in parsed and "body" in parsed:
            candidates.append(parsed)
        pos = body_end + len(end_fence)

    return candidates


def _write_candidates(
    candidates: list[dict[str, Any]], *, layout: RepoLayout, cfg: Config,
) -> None:
    """Convert each LLM-emitted candidate into a Brief and write to candidates/."""
    for c in candidates:
        fm = c["frontmatter"]
        body = c["body"]
        slug = slugify(fm.get("slug") or fm.get("title", "untitled"))
        # Host-compute niche_key — overwrite any model-supplied value
        niche_key = resolve_niche_key(fm.get("niche", "untagged"), cfg.niche_aliases)
        date_created = fm.get("date_created", date.today().isoformat())
        if isinstance(date_created, str):
            date_created = date.fromisoformat(date_created)
        brief = Brief(
            schema_version=1,
            title=fm["title"],
            slug=slug,
            lane=fm["lane"],
            niche=fm["niche"],
            niche_key=niche_key,
            delivery_form=fm.get("delivery_form", "project"),
            parent_project=fm.get("parent_project"),
            lane_note=fm.get("lane_note"),
            date_created=date_created,
            sources=fm["sources"],
            verification_evidence=fm.get("verification_evidence", []),
            disqualifier_verdicts=fm.get("disqualifier_verdicts", {}),
        )
        desired = candidate_filename(brief.date_created, slug)
        actual = resolve_collision(layout.candidates, desired)
        target = layout.candidates / actual
        write_brief(target, brief, body=body)
        typer.echo(f"created {target}")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import discover as discover_module
from mr.synth.budget import BudgetExceeded


@app.command(name="discover")
def discover_cmd(
    lane: str = typer.Option(None, "--lane"),
    n: int = typer.Option(5, "--n"),
    budget: float = typer.Option(5.0, "--budget"),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Generate candidate briefs from WISHLIST + live web tools."""
    try:
        discover_module.discover(root, lane, n, budget)
    except BudgetExceeded as e:
        typer.echo(f"budget aborted: {e}", err=True)
        raise typer.Exit(code=2)
    except RuntimeError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_discover.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/discover.py mr/cli/main.py tests/cli/test_discover.py
git commit -m "$(cat <<'EOF'
feat(cli): mr discover — generate candidates from WISHLIST + web tools

Implements mr discover per spec §7 + §8. Cold-corpus preflight, tier-1
ceiling check, flock-protected synth loop with prompt caching, custom
tool dispatch, host-computed niche_key, atomic candidate writes with
collision-suffix resolution. Aborts cleanly on BudgetExceeded.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 42: mr score — score, verify, route to scored/ or rejected/

**Spec sections:** §6 (lifecycle), §6.4 (host-driven verification), §5 (rubric), §8.2 (no web_search)

**Files:**
- Create: `mr/cli/score.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_score.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_score.py`:

```python
from datetime import date
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _candidate_with_verdicts(layout: RepoLayout, slug: str, hw_result: dict) -> Path:
    target = layout.candidates / f"20260507-{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title=slug, slug=slug, lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": hw_result},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    write_brief(target, brief, body="## Thesis\nFoo bar.\n")
    return target


@patch("mr.cli.score.run_score_loop")
def test_score_routes_to_rejected_when_hw_keys_missing(mock_loop, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = _candidate_with_verdicts(layout, "foo", hw_result={"peak_gpu_gb": 4})  # missing keys
    # mock the LLM scoring call to return scores 7/7/7/7
    mock_loop.return_value = {"defensibility": 7, "financial": 7, "implementation": 7, "hardware": 7}

    result = runner.invoke(app, ["score", str(src), "--budget", "3.0"])
    assert result.exit_code == 0
    # Brief should be in rejected/ with composite=00000
    assert any(layout.rejected.glob("00000-*-foo*.md"))


@patch("mr.cli.score.run_score_loop")
def test_score_routes_to_scored_when_predicates_pass(mock_loop, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = _candidate_with_verdicts(layout, "foo",
                                   hw_result={"peak_gpu_gb": 4, "sustained_ram_gb": 32, "storage_tb": 0.5})
    mock_loop.return_value = {"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9}

    result = runner.invoke(app, ["score", str(src), "--budget", "3.0"])
    assert result.exit_code == 0
    # Brief should be in scored/ with composite-prefixed filename
    moved = list(layout.scored.glob("*-20260507-foo*.md"))
    assert len(moved) == 1


@patch("mr.cli.score.run_score_loop")
def test_score_floor_rejection_low_defensibility(mock_loop, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = _candidate_with_verdicts(layout, "foo",
                                   hw_result={"peak_gpu_gb": 4, "sustained_ram_gb": 32, "storage_tb": 0.5})
    mock_loop.return_value = {"defensibility": 3, "financial": 8, "implementation": 8, "hardware": 8}

    result = runner.invoke(app, ["score", str(src), "--budget", "3.0"])
    assert result.exit_code == 0
    # defensibility=3 → tier-2 floor rejection → rejected/ with 00000- prefix
    assert any(layout.rejected.glob("00000-*-foo*.md"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_score.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/score.py`**

```python
"""mr score — score, verify, route to scored/ or rejected/."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer

from mr.dedup.seen import is_stale, regenerate_seen
from mr.lifecycle.filename import resolve_collision, scored_filename
from mr.lifecycle.frontmatter import Brief, read_brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import move_brief
from mr.scoring.auto_reject import (
    AutoRejectReason, REASON_STRINGS, decide_floor_rejection,
)
from mr.scoring.rubric import Scores, composite
from mr.synth.budget import BudgetTracker, worst_case_ceiling
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.synth.verify import verify_disqualifier_check
from mr.util.config import Config, load_config
from mr.util.costs import CostRecord, append_cost
from mr.util.lock import exclusive_lock


def score(paths: list[Path], root: Path, budget: float) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    cli = SynthClient(cfg=cfg, command="score")
    ceiling = worst_case_ceiling(cfg, "score", cli.model)
    if ceiling > budget:
        typer.echo(f"error: tier-1 ceiling ${ceiling:.2f} exceeds budget ${budget:.2f}", err=True)
        raise typer.Exit(code=2)

    with exclusive_lock(layout.lock_path):
        if is_stale(layout):
            regenerate_seen(layout, niche_aliases=cfg.niche_aliases)
        for path in paths:
            _score_one(path, layout=layout, cfg=cfg, budget=budget, client=cli)


def _score_one(src: Path, *, layout: RepoLayout, cfg: Config, budget: float, client: SynthClient) -> None:
    brief = read_brief(src)

    # Step 1: host-driven disqualifier verification (off tool-turn budget)
    outcome = verify_disqualifier_check(brief, cfg=cfg)
    if outcome.missing_hw_keys:
        _route_to_rejected(brief, src, layout, REASON_STRINGS[AutoRejectReason.MISSING_HW_KEYS])
        return
    if outcome.fabrication_detected:
        _route_to_rejected(brief, src, layout, REASON_STRINGS[AutoRejectReason.FABRICATION])
        return
    if outcome.flipped_to_fail("single_source"):
        _route_to_rejected(brief, src, layout, REASON_STRINGS[AutoRejectReason.SINGLE_SOURCE])
        return
    if outcome.flipped_to_fail("unrestricted_archives"):
        _route_to_rejected(brief, src, layout, REASON_STRINGS[AutoRejectReason.UNRESTRICTED_ARCHIVES])
        return
    if outcome.flipped_to_fail("hardware_over_envelope"):
        _route_to_rejected(brief, src, layout, REASON_STRINGS[AutoRejectReason.HARDWARE_OVER])
        return

    # Step 2: LLM scoring (rubric)
    scores_dict = run_score_loop(brief=brief, layout=layout, cfg=cfg, budget=budget, client=client)
    s = Scores(
        defensibility=scores_dict["defensibility"],
        financial=scores_dict["financial"],
        implementation=scores_dict["implementation"],
        hardware=scores_dict["hardware"],
    )

    # Step 3: floor decisions
    floor = decide_floor_rejection(s)
    if floor is not None:
        _route_to_rejected(brief, src, layout, REASON_STRINGS[floor], scores=s)
        return

    # Step 4: route to scored/
    comp = composite(s, weights=cfg.weights)
    brief.scores = {
        "defensibility": s.defensibility, "financial": s.financial,
        "implementation": s.implementation, "hardware": s.hardware,
        "composite": round(comp, 3), "auto_reject_reason": None,
    }
    write_brief(src, brief)

    desired = scored_filename(comp, brief.date_created, brief.slug)
    actual = resolve_collision(layout.scored, desired)
    dst = layout.scored / actual
    move_brief(src, dst)
    typer.echo(f"scored: {dst} (composite {comp:.3f})")


def run_score_loop(
    *, brief: Brief, layout: RepoLayout, cfg: Config, budget: float, client: SynthClient,
) -> dict[str, int]:
    """Run the LLM scoring conversation. Returns the four axis scores."""
    system_text = load_prompt(layout.prompts_dir, "score")
    system_blocks = build_cached_blocks(system_text=system_text)

    tracker = BudgetTracker(
        cfg=cfg, command="score", model=client.model,
        budget_usd=budget, costs_path=layout.costs_path,
    )
    tools = tools_for_command("score", firecrawl_available=False)

    user_msg = (
        "Score the following candidate brief on the 4-axis rubric (defensibility, financial, "
        "implementation, hardware), each 0-10 integer. Output ONLY a JSON object "
        '{"defensibility": int, "financial": int, "implementation": int, "hardware": int}.\n\n'
        f"Brief:\n```\n{_serialize_brief(brief)}\n```"
    )
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_msg}]
    max_tokens = cfg.budgets["max_tokens_per_turn"]

    while True:
        tracker.note_tool_turn()
        tracker.check_wallclock()
        tracker.check_pre_call(input_tokens_estimate=8000, max_output_tokens=max_tokens)

        response = client.create_message(
            system_blocks=system_blocks, messages=messages, tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(timezone.utc), command="score", model=client.model,
            input_tokens=usage["input_tokens"], cached_input_tokens=0,
            output_tokens=usage["output_tokens"],
            cache_hits=usage["cache_hits"], cache_misses=usage["cache_misses"],
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
        tracker.note_turn_cache_status(missed=usage["cache_misses"] > 0, fingerprint="score_system")

        assistant = list(response.content)
        messages.append({"role": "assistant", "content": [_block_to_dict(b) for b in assistant]})

        if response.stop_reason != "tool_use":
            return _extract_scores(assistant)

        tool_uses = [b for b in assistant if getattr(b, "type", None) == "tool_use"]
        tool_results = []
        for tu in tool_uses:
            result = dispatch_tool_call(name=tu.name, args=tu.input, seen_path=layout.seen_path)
            tool_results.append({
                "type": "tool_result", "tool_use_id": tu.id,
                "content": json.dumps(result),
            })
        messages.append({"role": "user", "content": tool_results})


def _block_to_dict(block: Any) -> dict[str, Any]:
    btype = getattr(block, "type", None)
    if btype == "text":
        return {"type": "text", "text": block.text}
    if btype == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return {"type": btype}


def _extract_scores(content: list[Any]) -> dict[str, int]:
    text = " ".join(b.text for b in content if getattr(b, "type", None) == "text")
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"score response did not contain a JSON object: {text!r}")
    parsed = json.loads(text[start : end + 1])
    return {
        "defensibility": int(parsed["defensibility"]),
        "financial": int(parsed["financial"]),
        "implementation": int(parsed["implementation"]),
        "hardware": int(parsed["hardware"]),
    }


def _serialize_brief(brief: Brief) -> str:
    """Render a brief for inclusion in the scoring prompt."""
    return f"""title: {brief.title}
slug: {brief.slug}
lane: {brief.lane}
niche: {brief.niche}
sources: {brief.sources}
disqualifier_verdicts: {brief.disqualifier_verdicts}
{brief.body}"""


def _route_to_rejected(
    brief: Brief, src: Path, layout: RepoLayout, reason: str, scores: Scores | None = None,
) -> None:
    """Auto-reject: write 00000- prefixed filename, set auto_reject_reason."""
    if brief.scores is None:
        brief.scores = {}
    if scores is not None:
        brief.scores.update({
            "defensibility": scores.defensibility, "financial": scores.financial,
            "implementation": scores.implementation, "hardware": scores.hardware,
            "composite": 0.0,
        })
    else:
        brief.scores.setdefault("composite", 0.0)
    brief.scores["auto_reject_reason"] = reason
    write_brief(src, brief)

    desired = scored_filename(0.0, brief.date_created, brief.slug)
    actual = resolve_collision(layout.rejected, desired)
    dst = layout.rejected / actual
    move_brief(src, dst)
    typer.echo(f"rejected: {dst} ({reason})")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import score as score_module


@app.command(name="score")
def score_cmd(
    paths: list[Path] = typer.Argument(..., exists=True),
    budget: float = typer.Option(3.0, "--budget"),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Score candidates: route to scored/ or rejected/ with auto-reject."""
    try:
        score_module.score(paths, root, budget)
    except BudgetExceeded as e:
        typer.echo(f"budget aborted: {e}", err=True)
        raise typer.Exit(code=2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_score.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/score.py mr/cli/main.py tests/cli/test_score.py
git commit -m "$(cat <<'EOF'
feat(cli): mr score — verify, score, route to scored/ or rejected/

Implements mr score per spec §6 + §6.4 + §5. Host-driven verification
first (no tool-turn cost; checks single_source, unrestricted_archives,
hardware_over_envelope predicates against cited evidence; detects
fabrication). LLM scoring loop returns 4 axis scores. Routes to
scored/ with composite-prefixed filename or rejected/ with 00000-
on auto-reject.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 43: mr gain — costs.jsonl summary

**Spec sections:** §10 (mr gain modeled on rtk gain)

**Files:**
- Create: `mr/cli/gain.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_gain.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_gain.py`:

```python
from datetime import datetime, timezone
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout
from mr.util.costs import CostRecord, append_cost

runner = CliRunner()


def test_gain_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0
    assert "$0.00" in result.stdout or "0.00" in result.stdout


def test_gain_summarizes_costs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    for cost in [0.10, 0.20, 0.05]:
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(timezone.utc), command="discover",
            model="claude-opus-4-7",
            input_tokens=100, cached_input_tokens=0, output_tokens=50,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0
    assert "0.35" in result.stdout
    assert "discover" in result.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_gain.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/gain.py`**

```python
"""mr gain — summarize spend from costs.jsonl."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.util.costs import read_cost_history


def gain(root: Path) -> None:
    layout = RepoLayout(root)
    records = read_cost_history(layout.costs_path)
    if not records:
        typer.echo("no recorded API calls — total $0.00")
        return

    per_command: dict[str, float] = defaultdict(float)
    per_model: dict[str, float] = defaultdict(float)
    total = 0.0
    for r in records:
        per_command[r.command] += r.cost_usd
        per_model[r.model] += r.cost_usd
        total += r.cost_usd

    typer.echo(f"## Total spend: ${total:.4f}")
    typer.echo(f"## Calls: {len(records)}")

    typer.echo("\n## By command")
    for cmd, c in sorted(per_command.items(), key=lambda x: -x[1]):
        typer.echo(f"  {cmd}: ${c:.4f}")

    typer.echo("\n## By model")
    for m, c in sorted(per_model.items(), key=lambda x: -x[1]):
        typer.echo(f"  {m}: ${c:.4f}")
```

Add to `mr/cli/main.py`:

```python
from mr.cli import gain as gain_module


@app.command(name="gain")
def gain_cmd(root: Path = typer.Option(Path.cwd(), "--root")) -> None:
    """Summarize API spend from .moat-research/costs.jsonl."""
    gain_module.gain(root)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_gain.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/gain.py mr/cli/main.py tests/cli/test_gain.py
git commit -m "$(cat <<'EOF'
feat(cli): mr gain — spend summary from costs.jsonl

Implements mr gain per spec §10. Reports total + per-command +
per-model breakdowns. Modeled on rtk gain.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 44: mr wishlist subcommand group (add, expand, refresh)

**Spec sections:** §7 (wishlist subcommands), §11 (full semantics)

**Files:**
- Create: `mr/cli/wishlist.py`
- Modify: `mr/cli/main.py`
- Create: `tests/cli/test_wishlist_cli.py`

- [ ] **Step 1: Write the failing tests**

`tests/cli/test_wishlist_cli.py`:

```python
from datetime import date
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def test_wishlist_add_via_cli(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    yaml_text = """id: my-source
url: https://example.com/
lane: niche_vertical
rationale: testing
last_verified: 2026-05-07
dead_link: false
"""
    result = runner.invoke(app, ["wishlist", "add", "--yaml", yaml_text])
    assert result.exit_code == 0


@patch("mr.cli.wishlist.refresh_wishlist")
def test_wishlist_refresh_via_cli(mock_refresh, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["wishlist", "refresh"])
    assert result.exit_code == 0
    mock_refresh.assert_called_once()


@patch("mr.cli.wishlist.expand_wishlist")
def test_wishlist_expand_via_cli(mock_expand, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    mock_expand.return_value = "(no proposals)"
    result = runner.invoke(app, ["wishlist", "expand", "--seed", "--budget", "0.5"])
    assert result.exit_code == 0
    mock_expand.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_wishlist_cli.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `mr/cli/wishlist.py`**

```python
"""mr wishlist {add, expand, refresh} subcommand group."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.synth.budget import BudgetExceeded
from mr.util.config import load_config
from mr.util.lock import exclusive_lock
from mr.wishlist.add import add_source
from mr.wishlist.expand import expand_wishlist
from mr.wishlist.refresh import refresh_wishlist

wishlist_app = typer.Typer(no_args_is_help=True, help="Wishlist management subcommands.")


@wishlist_app.command("add")
def add_cmd(
    yaml: str = typer.Option(..., "--yaml", help="YAML fragment for the new source"),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """Append a validated source to WISHLIST.md."""
    layout = RepoLayout(root)
    add_source(layout.wishlist_path, yaml)
    typer.echo("source added")


@wishlist_app.command("refresh")
def refresh_cmd(root: Path = typer.Option(Path.cwd(), "--root")) -> None:
    """Re-verify all WISHLIST sources (HEAD + robots + Wayback)."""
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)
    window = cfg.status.get("dead_link_window_days", 14)
    refresh_wishlist(layout.wishlist_path, today=date.today(), dead_link_window_days=window)
    typer.echo("refreshed")


@wishlist_app.command("expand")
def expand_cmd(
    seed: bool = typer.Option(False, "--seed", help="Bootstrap from empty WISHLIST"),
    budget: float = typer.Option(2.0, "--budget"),
    root: Path = typer.Option(Path.cwd(), "--root"),
) -> None:
    """LLM proposes new WISHLIST sources for operator review."""
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)
    try:
        with exclusive_lock(layout.lock_path):
            output = expand_wishlist(layout, cfg, seed=seed, budget_usd=budget)
        typer.echo(output)
    except BudgetExceeded as e:
        typer.echo(f"budget aborted: {e}", err=True)
        raise typer.Exit(code=2)
```

Add to `mr/cli/main.py`:

```python
from mr.cli.wishlist import wishlist_app

app.add_typer(wishlist_app, name="wishlist")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_wishlist_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mr/cli/wishlist.py mr/cli/main.py tests/cli/test_wishlist_cli.py
git commit -m "$(cat <<'EOF'
feat(cli): mr wishlist {add, expand, refresh} subcommands

Implements the wishlist subcommand group per spec §7 and §11. Add
takes --yaml, refresh runs deterministic re-verification with
dead_link_window_days from mr.yaml, expand drives the LLM proposal
loop under flock + budget guard.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 11: Prompts (shipped templates)

### Task 45: prompts/discover.md

**Spec sections:** §6.4 (frontmatter contract), §8.4.1 (prompt content requirements)

**Files:**
- Create: `prompts/discover.md`
- Create: `tests/test_prompts_content.py`

- [ ] **Step 1: Write a smoke test for the prompt's required keywords**

`tests/test_prompts_content.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they skip (files not yet written)**

Run: `uv run pytest tests/test_prompts_content.py -v`
Expected: SKIPPED.

- [ ] **Step 3: Write `prompts/discover.md`**

```markdown
# moat-research: mr discover

You generate **candidate moat briefs** for a single solo operator. Each candidate must be a project (or feature) with structural defensibility against well-funded competitors.

## What you produce

For each candidate, output a fenced YAML block in this format:

````
```yaml-brief
frontmatter:
  schema_version: 1
  title: <human title>
  slug: <kebab-slug-≤40-chars>
  lane: ephemeral_public | soon_to_be_restricted | cross_source_fusion | derived_artifact | niche_vertical | other
  lane_note: <required iff lane == other>
  niche: <1-3-word human-readable tag>
  delivery_form: project | feature
  parent_project: <slug>          # required iff delivery_form == feature
  date_created: <yyyy-mm-dd>
  sources:
    - url: https://...
      role: primary | corroborating | counter_evidence
      archive_status: none | partial | unrestricted
  verification_evidence:
    - id: e1
      tool: wayback_check
      args: {url: <primary_url>}
      result: {count: <int>, first: <yyyy-mm-dd>, last: <yyyy-mm-dd>}
    - id: e3
      tool: code_execution
      args: {code: "<utilization estimate computation>"}
      result: {peak_gpu_gb: <number>, sustained_ram_gb: <number>, storage_tb: <number>}
  disqualifier_verdicts:
    defensibility_threshold: n/a
    any_axis_zero: n/a
    single_source: {verdict: pass | fail}
    unrestricted_archives:
      verdict: pass | fail
      wayback_evidence_id: e1
      publisher_archive_evidence_id: null
    tos_redistribution:
      verdict: pass | fail | n/a
      evidence_id: <e2 if applicable, else null>
    hardware_over_envelope:
      verdict: pass | fail
      evidence_id: e3
body: |
  ## Thesis
  <2–4 sentences: what is the project and why does the moat hold>

  ## Why this is a moat
  <defensibility argument with cited counter-evidence>

  ## Sources
  <table: URL · what it provides · archive status · access constraints>

  ## Financial sketch
  <TAM, pricing, ops cost>

  ## Implementation sketch
  <MVP scope, weeks to MVP, ongoing maintenance>

  ## Hardware fit
  <utilization plan vs. operator envelope>

  ## Disqualifier check
  <summary prose; the structured contract is in disqualifier_verdicts>
```
````

## Hard requirements (non-negotiable)

1. **Every brief MUST emit a `code_execution` evidence row** whose `result` contains all three keys `peak_gpu_gb`, `sustained_ram_gb`, `storage_tb` as numeric values (use `0` for unused resources). The `hardware_over_envelope.evidence_id` references this row's `id`. Missing keys cause `mr score` to auto-reject.

2. **Use `seen_lookup` before committing each candidate.** Call `seen_lookup(slug=…, source_set=[…], lane_niche=[…])`. If `matches` is non-empty, the candidate is a duplicate — drop it and propose a different one.

3. **Diversity bias.** When `--lane` is not specified, prefer `(lane, niche_key)` cells underrepresented in the frequency table. **`lane: other` is fully exempt** — repetition there is encouraged, not penalized. Do not propose candidates whose niche overlaps `mr.yaml: interests.avoid`. Prefer niches in `interests.affirm`.

4. **`soon_to_be_restricted` lane** candidates must cite a dated public artifact (board minutes, regulatory docket, published roadmap, official statement). Speculation without a dated artifact must lead to either a re-classified lane or a dropped candidate.

5. **`delivery_form: feature`** when the candidate's moat materially depends on extending an existing project named in `mr.yaml: interests.affirm` (e.g., adding aviation alerts to a `somd-cameras` repo). Set `parent_project: <slug>`. Otherwise `delivery_form: project`.

6. **`lane: other`** is the escape hatch for genuinely novel moat shapes. Set `lane_note:` with a one-sentence justification.

## Five canonical lanes (lane #6 is `other`)

1. `ephemeral_public` — published by an authority but expires/rotates without archive.
2. `soon_to_be_restricted` — currently public but on a credible path to paywall, ToS lockdown, or removal.
3. `cross_source_fusion` — multiple public sources whose join produces a non-obvious derived artifact.
4. `derived_artifact` — single public source plus a transformation hard to reverse.
5. `niche_vertical` — domain so narrow that incumbents will not bother.

## Definition of "moat" (strict)

A moat is a structural barrier that cannot be overcome by spending money, acquiring compute, hiring staff, or acquiring competing entities. If a well-funded company can replicate the project after one focused quarter, the project does not have a moat. Defensibility ≤ 4 is auto-rejected.

## Hardware envelope

40 cores / 80 threads (2× Intel Xeon E5-2698 v4), 250 GB RAM, NVIDIA P4 GPU (8 GB shared), 17 TB NAS, residential broadband. Briefs whose hardware demand exceeds this envelope are auto-rejected.

## Tool use

You have access to `web_search` (broad scan), `web_fetch` (targeted retrieval with dynamic filtering), `code_execution` (free Python sandbox when bundled with web tools — use it for utilization estimates and dedup-against-source_set arithmetic), `wayback_check` (archive evidence), `seen_lookup` (corpus dedup), and optionally `firecrawl_scrape` (fallback for JS-heavy pages). Use `code_execution` aggressively — it's free.
```

- [ ] **Step 4: Run prompt smoke tests for the discover prompt**

Run: `uv run pytest tests/test_prompts_content.py::test_discover_prompt_mandates_seen_lookup tests/test_prompts_content.py::test_discover_prompt_lists_all_lanes tests/test_prompts_content.py::test_discover_prompt_mandates_hardware_keys tests/test_prompts_content.py::test_discover_prompt_mentions_diversity_bias tests/test_prompts_content.py::test_discover_prompt_mentions_interests tests/test_prompts_content.py::test_discover_prompt_mentions_yaml_brief_fence -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add prompts/discover.md tests/test_prompts_content.py
git commit -m "$(cat <<'EOF'
feat(prompts): discover.md system prompt

Implements the discover.md template per spec §6.4 + §8.4.1. Encodes
the YAML brief format, hardware-key contract, seen_lookup mandate,
diversity bias, soon_to_be_restricted evidence requirement,
delivery_form heuristic, lane vocabulary (incl. `other` escape hatch),
and tool-use guidance.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 46: prompts/score.md

- [ ] **Step 1: Write `prompts/score.md`**

```markdown
# moat-research: mr score

You score a candidate moat brief on a 4-axis rubric. **Output ONLY a single JSON object** with the four integer scores. No prose, no markdown.

## Output format

```
{"defensibility": <int 0-10>, "financial": <int 0-10>, "implementation": <int 0-10>, "hardware": <int 0-10>}
```

## Rubric

The composite score is a weighted geometric mean: `composite = d^0.35 × f^0.30 × i^0.20 × h^0.15`. Each axis is 0–10 integer. Composite ranges [0, 10].

### Defensibility (35% weight)

*Can a well-funded competitor replicate this in one focused quarter?*

- **0–2:** Pure data resale, single source, no transformation. Anyone with budget wins.
- **3–4:** Some aggregation or processing, but a competitor can match it within a quarter. **Auto-reject zone.**
- **5–6:** Real but bounded moat — geographic exclusivity, single transformative pipeline, niche relationship.
- **7–8:** Multi-layered moat — combines two or more of: archive history, geographic exclusivity, multi-source fusion, derived artifacts hard to reverse.
- **9–10:** Structural inevitability — moat compounds with use, or is contractually exclusive.

### Financial (30% weight)

*Annualized profit potential vs. operating cost?*

- **0–2:** Cannot cover its own inference bill.
- **3–4:** Marginally positive, no operator surplus.
- **5–6:** $5–25k/yr net.
- **7–8:** $25–100k/yr net.
- **9–10:** $100k+/yr net or low-effort recurring revenue.

### Implementation (20% weight)

*Time/effort to MVP and ongoing maintenance?*

- **0–2:** Multi-quarter MVP; ongoing ≥20 hrs/wk.
- **3–4:** 6–12 weeks to MVP; ongoing 5–10 hrs/wk.
- **5–6:** 2–6 weeks to MVP; ongoing 1–4 hrs/wk.
- **7–8:** 1–2 weeks to MVP; ongoing <1 hr/wk.
- **9–10:** <1 week to MVP; near-zero ongoing.

### Hardware (15% weight)

*Fits the operator's envelope (40c/80t, 250 GB RAM, P4 8 GB shared, 17 TB NAS)?*

- **0–2:** Requires GPU class above P4, or >250 GB RAM, or >17 TB.
- **3–4:** Squeezes the envelope — sustained >50% utilization needed.
- **5–6:** Comfortable at peak, idle most of the time.
- **7–8:** Trivial fit; runs alongside existing workloads.
- **9–10:** Could run on a Raspberry Pi.

## Tool use

You have `web_fetch` (re-verify cited URLs, look for counter-evidence) and `code_execution` (storage growth math, rate-budget arithmetic, predicate checks). **You do NOT have `web_search`** — this prevents drift into adjacent opportunities mid-evaluation. Score the brief in front of you, not the brief you wish you were scoring.

## Authority

The rubric above is the only allowed scoring authority. Disqualifier verification is performed host-side before this prompt runs — assume the brief in front of you has already passed structured disqualifier checks (single_source, unrestricted_archives, tos_redistribution, hardware_over_envelope predicates) or you would not be scoring it. Your job is purely to assign the four axis scores.

Output the JSON object on a single line. Nothing else.
```

- [ ] **Step 2: Run prompt content test for score.md**

Run: `uv run pytest tests/test_prompts_content.py::test_score_prompt_mentions_rubric -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add prompts/score.md
git commit -m "$(cat <<'EOF'
feat(prompts): score.md system prompt

Implements the score.md template per spec §5 + §8.4.1. Encodes the
4-axis rubric anchors, JSON-only output format, no-web_search rule,
and authority statement (rubric is the only scoring authority;
disqualifier verification is host-side).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 47: prompts/wishlist_expand.md

- [ ] **Step 1: Write `prompts/wishlist_expand.md`**

```markdown
# moat-research: mr wishlist expand

You propose new candidate sources to add to `WISHLIST.md`. Output one or more YAML blocks separated by `---`. Each block is a fragment suitable for `mr wishlist add --yaml <fragment>`.

## Output format

```
---
id: <kebab-id, lowercase, hyphen-separated>
url: https://...
lane: ephemeral_public | soon_to_be_restricted | cross_source_fusion | derived_artifact | niche_vertical | other
rationale: |
  <1-3 sentences on why this source is moat-relevant>
last_verified: <today's date in yyyy-mm-dd>
dead_link: false
---
<more proposals as needed>
```

## Hard requirements

1. **Use `seen_lookup` before each proposal.** Call `seen_lookup(source_set=[<host>])`. If the host appears in 3+ briefs across canonical lanes (not `other`), the source is "mined" — propose it ONLY if you can articulate a fusion or transformation pairing whose `source_set` is novel. If you cannot, drop the proposal.

2. **Source-set fusion focus.** Re-using a familiar host in a new combination is *encouraged*. The dedup key is the `source_set` of every produced brief, not any single host. A host appearing solo 5 times but never in fusion is a strong candidate for new fusion proposals.

3. **Same lane vocabulary as discover.** Five canonical lanes plus `other`. For `soon_to_be_restricted`, cite a dated public artifact (board minutes, regulatory docket, roadmap, official statement) in the rationale.

4. **Domain interests.** Consume `mr.yaml: interests.affirm` and `interests.avoid`. Do not propose sources whose primary domain falls in `avoid`.

5. **Bootstrap mode.** When invoked with `--seed`, the WISHLIST is empty. Propose 5–10 diverse sources spanning at least 3 different lanes. Aim for solo-operator-shaped opportunities (financial axis 5+, implementation 5+, hardware 5+).

## Tool use

You have `web_search`, `web_fetch`, `code_execution` (free when bundled), `seen_lookup`, and optionally `firecrawl_scrape`. Use `code_execution` aggressively for dedup arithmetic against the seen-summary frequency table.
```

- [ ] **Step 2: Run prompt content test for wishlist_expand.md**

Run: `uv run pytest tests/test_prompts_content.py::test_wishlist_expand_prompt_mentions_seen_lookup -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add prompts/wishlist_expand.md
git commit -m "$(cat <<'EOF'
feat(prompts): wishlist_expand.md system prompt

Implements the wishlist_expand.md template per spec §11 + §8.4.1.
Encodes the YAML output format, source-set fusion rule, seen_lookup
mandate, lane vocabulary, soon_to_be_restricted evidence requirement,
domain interests filter, and --seed bootstrap mode.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 12: Integration smoke test + final review

### Task 48: End-to-end smoke test (mocked LLM)

**Spec sections:** §16 (success criteria)

**Files:**
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_e2e.py`

- [ ] **Step 1: Write the failing tests**

`tests/integration/test_e2e.py`:

```python
"""End-to-end smoke test: init → seeded WISHLIST → discover (mocked LLM)
→ score (mocked LLM) → promote → graduate."""
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _seed_wishlist(layout: RepoLayout) -> None:
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))


def _mock_discover_loop_to_emit_one_candidate(layout: RepoLayout):
    """Patch the discover loop to write a candidate file directly,
    bypassing the LLM."""
    def fake(*args, **kwargs):
        target = layout.candidates / "20260507-test-brief.md"
        brief = Brief(
            schema_version=1, title="Test Brief", slug="test-brief",
            lane="ephemeral_public", niche="aviation alerts",
            niche_key="alerts_aviation", delivery_form="project",
            date_created=date(2026, 5, 7),
            sources=[
                {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
                {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
            ],
            verification_evidence=[
                {"id": "e3", "tool": "code_execution", "args": {"code": "x"},
                 "result": {"peak_gpu_gb": 4, "sustained_ram_gb": 32, "storage_tb": 0.5}},
            ],
            disqualifier_verdicts={
                "single_source": {"verdict": "pass"},
                "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
            },
        )
        write_brief(target, brief, body="## Thesis\nTest thesis.\n")
    return fake


def test_full_lifecycle_e2e(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    # init
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0

    layout = RepoLayout(tmp_path)
    _seed_wishlist(layout)

    # discover (mocked)
    with patch("mr.cli.discover.run_discover_loop",
               side_effect=_mock_discover_loop_to_emit_one_candidate(layout)):
        result = runner.invoke(app, ["discover", "--lane", "ephemeral_public",
                                     "--n", "1", "--budget", "5.0"])
        assert result.exit_code == 0

    candidate_files = list(layout.candidates.glob("*.md"))
    assert len(candidate_files) == 1

    # score (mocked LLM scores)
    with patch("mr.cli.score.run_score_loop",
               return_value={"defensibility": 7, "financial": 6,
                             "implementation": 8, "hardware": 9}):
        result = runner.invoke(app, ["score", str(candidate_files[0]), "--budget", "3.0"])
        assert result.exit_code == 0

    scored_files = list(layout.scored.glob("*.md"))
    assert len(scored_files) == 1
    assert scored_files[0].name.startswith("0")  # composite-padded prefix

    # promote
    result = runner.invoke(app, ["promote", str(scored_files[0])])
    assert result.exit_code == 0
    approved_files = list(layout.approved.glob("*.md"))
    assert len(approved_files) == 1

    # graduate
    result = runner.invoke(app, ["graduate", str(approved_files[0])])
    assert result.exit_code == 0
    assert "You are starting test-brief" in result.stdout
    graduated_files = list(layout.graduated.glob("*.md"))
    assert len(graduated_files) == 1
    handoff_files = list(layout.graduated.glob("*.handoff.txt"))
    assert len(handoff_files) == 1

    # status
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "graduated" in result.stdout.lower()

    # gain
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0


def test_full_test_suite_runs_under_30_seconds(tmp_path: Path):
    """Sanity: the full unit + integration suite is fast enough for CI."""
    import time
    import subprocess
    start = time.monotonic()
    subprocess.run(["uv", "run", "pytest", "-q", "--no-header", "tests/"],
                   check=False, capture_output=True)
    elapsed = time.monotonic() - start
    # Loose check; mostly catches accidental network calls
    assert elapsed < 60.0
```

- [ ] **Step 2: Run tests to verify the e2e test fails initially**

Run: `uv run pytest tests/integration/test_e2e.py -v`
Expected: FAIL initially if any prior task wasn't fully completed; this test exists to catch integration-level breakage.

- [ ] **Step 3: Iterate on any failing pieces**

Re-run the failing tests in their respective Phase tasks until each passes individually. Then re-run the e2e test. Common gotchas:
- `mr discover` aborts because tier-1 ceiling > budget — adjust `mr.yaml` or pass `--budget 5.0`.
- Frontmatter validation rejects the candidate — ensure mocked candidate has all required keys.
- `mr score` rejects on missing-hardware-keys — ensure mocked verification_evidence has all three keys.

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/__init__.py tests/integration/test_e2e.py
git commit -m "$(cat <<'EOF'
test(integration): end-to-end smoke test (mocked LLM)

Exercises init → seeded WISHLIST → discover → score → promote →
graduate → status → gain with the LLM mocked. Validates spec §16
success criteria 1-3 within a single test run. Adds suite-runtime
sanity check.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 49: README + plan completeness check

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# moat-research

A solo-operator CLI tool plus structured corpus for discovering, scoring, and graduating **data-moat opportunities** — projects whose structural advantage cannot be overcome by capital and compute alone.

See `docs/superpowers/specs/2026-05-07-moat-research-design.md` for the full design.

## Install

```bash
uv sync
mr init
```

## First-session walkthrough

```bash
mr wishlist expand --seed --budget 0.50    # populate WISHLIST from empty
mr discover --lane ephemeral_public --n 5 --budget 5.0
mr score candidates/*.md --budget 3.0
mr status                                   # see counts
mr promote scored/<top-composite>.md        # accept best brief
mr graduate approved/<top>.md > /tmp/init.txt
mkdir ~/<slug> && cd ~/<slug> && git init
claude < /tmp/init.txt                      # spawn the new project
```

## Subcommands

| Command | LLM? | Purpose |
|---|---|---|
| `mr init` | no | Bootstrap dirs, mr.yaml, prompts/ (idempotent) |
| `mr discover` | yes | Generate candidates from WISHLIST + live web tools |
| `mr score` | yes | Score candidates; route to scored/ or rejected/ |
| `mr promote` | no | Move scored → approved |
| `mr graduate` | no | Emit hand-off prompt; move approved → graduated |
| `mr reject` | no | Move scored → rejected with operator reason |
| `mr wishlist add` | no | Append validated source to WISHLIST.md |
| `mr wishlist expand` | yes | LLM proposes new sources for review |
| `mr wishlist refresh` | no | Re-verify sources (HEAD + robots + Wayback) |
| `mr status` | no | Counts + stale-approved + exploration flags |
| `mr gain` | no | Spend summary from costs.jsonl |

## Configuration

`mr.yaml` controls model selection, weights, budgets, lanes, niche aliases, interest filters, and hardware envelope. Defaults are baked-in; only override what you need to change. Schema is JSON-Schema-validated at load.

## License

UNLICENSED. Personal-use tool.
```

- [ ] **Step 2: Run plan completeness check against the spec**

Walk the spec's section list and confirm each requirement maps to at least one task:

| Spec section | Implemented in |
|---|---|
| §1 Purpose | overall design, README |
| §2 Definition of moat (strict) | `prompts/discover.md` |
| §3 Architecture decisions | overall design |
| §4 Operational envelope | `mr/util/config.py` (DEFAULT_CONFIG.hardware) |
| §5 Scoring rubric | Task 12 (`mr/scoring/rubric.py`) |
| §5.5 Auto-reject + reason strings | Task 13 (`mr/scoring/auto_reject.py`) |
| §5.6 Sensitivity note | (documentation only) |
| §6.1 Filename convention | Task 9 (`mr/lifecycle/filename.py`) |
| §6.2 Transitions | Task 11 (`mr/lifecycle/transitions.py`) + CLI commands |
| §6.3 Re-scoring (mv not cp) | Task 10 frontmatter; documented in CLI behavior |
| §6.4 Brief frontmatter contract | Task 10 (`mr/lifecycle/frontmatter.py`); Task 28 (verification) |
| §7 CLI commands | Tasks 36-44 |
| §8.1 Models + caching | Task 25 (`mr/synth/client.py`) |
| §8.2 Tool set per subcommand | Task 26 (`mr/synth/tools.py`) |
| §8.3 Custom tool implementations | Tasks 17-21 |
| §8.4 Prompts | Tasks 45-47 |
| §8.4.1 Prompt content requirements | Tasks 45-47 + smoke tests in Task 45 |
| §8.5 Five lanes + other | Task 26 + prompts |
| §9 mr.yaml | Task 4 (`mr/util/config.py`) |
| §10 State, concurrency, costs | Tasks 6, 7, 8, 15 |
| §11 WISHLIST | Tasks 29-32 + 44 |
| §12.1 seen.jsonl | Task 15 (`mr/dedup/seen.py`) |
| §12.2 Bounded summary | Task 16 (`mr/dedup/summary.py`) |
| §12.3 seen_lookup tool | Task 20 + Task 26 |
| §12.4 Heuristics | Task 20 (host-side); prompts (LLM-side) |
| §12.5 Frontmatter contract | Task 14 + Task 10 |
| §13 Hand-off | Tasks 33-35 + Task 40 |
| §14 Migration | Task 1 |
| §15 Out of scope | (no implementation needed) |
| §16 Success criteria | Task 48 (e2e test) |

If any row above lacks a task, add a remediation task before proceeding.

- [ ] **Step 3: Run all tests**

Run: `uv run pytest -v`
Expected: All tests PASS.

- [ ] **Step 4: Run linting**

Run: `uv run ruff check mr/ tests/`
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "$(cat <<'EOF'
docs: README with first-session walkthrough and subcommand index

Adds operator-facing README pointing to the spec for design rationale
and providing a copy-pastable first-session walkthrough (init → seed
WISHLIST → discover → score → promote → graduate).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-07-moat-research-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration. Use `superpowers:subagent-driven-development`.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints for review.

Which approach?

