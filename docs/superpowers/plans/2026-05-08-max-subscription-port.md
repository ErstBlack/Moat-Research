# Max-Subscription Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the `mr` CLI from the metered Anthropic API to the Claude Max subscription via the Claude Agent SDK, while preserving all command behavior and trimming the financial cost-tracking layer.

**Architecture:** typer commands stay sync; each wraps a single `asyncio.run(session.run(...))` call. `session.run` invokes `claude_agent_sdk.query()` with an in-process MCP server that exposes the project's six custom tools (`seen_lookup`, `wayback`, `robots`, `head`, `firecrawl`, `code_eval`) plus Claude Code's `WebSearch`/`WebFetch`. The SDK owns the tool-use loop. Wallclock is enforced with `asyncio.wait_for`; turn cap is the SDK's `max_turns` option.

**Tech Stack:** Python 3.12, `claude-agent-sdk`, typer, pytest, pytest-anyio, pyyaml, jsonschema, httpx.

**Spec:** [`docs/superpowers/specs/2026-05-08-max-subscription-port-design.md`](../specs/2026-05-08-max-subscription-port-design.md)

---

## Task 1: Add `claude-agent-sdk` and `pytest-anyio` dependencies

**Files:**
- Modify: `pyproject.toml`

**Rationale:** `claude-agent-sdk` is the runtime; `pytest-anyio` enables `@pytest.mark.anyio` so we can test async tool functions and `session.run`. Both go in before any new code lands. We do **not** remove `anthropic` here — the existing `mr/synth/client.py` keeps importing it through Task 12.

- [ ] **Step 1: Edit `pyproject.toml` dependencies**

Replace the `dependencies` list and `dev` group:

```toml
dependencies = [
    "anthropic>=0.50.0",
    "claude-agent-sdk>=0.0.20",
    "typer>=0.12.0",
    "pyyaml>=6.0",
    "httpx>=0.27.0",
    "jsonschema>=4.21.0",
    "waybackpy>=3.0.6",
    "rich>=13.7.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-anyio>=0.0.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.5.0",
]
```

- [ ] **Step 2: Add anyio config to pytest section**

Append to `[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --strict-markers --strict-config"
filterwarnings = ["error"]
anyio_backends = ["asyncio"]
```

- [ ] **Step 3: Install and verify**

Run:
```bash
pip install -e ".[dev]" || python -m pip install -e ".[dev]"
python -c "from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server; print('ok')"
```
Expected: `ok`

- [ ] **Step 4: Run full test suite to confirm green baseline**

Run: `rtk pytest`
Expected: all existing tests pass (no behavior change yet).

- [ ] **Step 5: Commit**

```bash
rtk git add pyproject.toml
rtk git commit -m "deps: add claude-agent-sdk and pytest-anyio"
```

---

## Task 2: Create `mr/synth/mcp_server.py` skeleton with delegating tools

**Files:**
- Create: `mr/synth/mcp_server.py`
- Create: `tests/synth/test_mcp_server.py`

**Rationale:** Define the four delegating MCP tools that wrap existing domain functions (`seen_lookup`, `wayback`, `robots`, `head`). These have no new logic — just bridging from the SDK's `@tool` shape to the existing returns. Defer `code_eval` (Task 3) and `firecrawl` + `build_server` factory (Task 4).

- [ ] **Step 1: Write failing test for `seen_lookup` tool**

Create `tests/synth/test_mcp_server.py`:

```python
"""Tests for mr.synth.mcp_server tool factories."""
import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from mr.synth import mcp_server


def _text_payload(result: dict) -> dict:
    """Extract and JSON-decode the text content from a @tool return."""
    assert "content" in result
    assert result["content"][0]["type"] == "text"
    return json.loads(result["content"][0]["text"])


@pytest.mark.anyio
async def test_seen_lookup_returns_matches(tmp_path: Path):
    seen_path = tmp_path / "seen.jsonl"
    seen_path.write_text("")
    fn = mcp_server._make_seen_lookup(seen_path)
    result = await fn({"slug": "foo"})
    payload = _text_payload(result)
    assert "matches" in payload
    assert "near_matches" in payload
```

- [ ] **Step 2: Run test to verify it fails**

Run: `rtk pytest tests/synth/test_mcp_server.py::test_seen_lookup_returns_matches -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'mr.synth.mcp_server'` (or similar).

- [ ] **Step 3: Write minimal `mr/synth/mcp_server.py`**

Create `mr/synth/mcp_server.py`:

```python
"""In-process MCP server wrapping the project's custom tools.

Tools delegate to existing implementations under mr.tools.* and
mr.dedup.seen_lookup. The factory `build_server` captures `seen_path`
via closure so per-invocation state stays out of the tool signature.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from claude_agent_sdk import create_sdk_mcp_server, tool


def _wrap_text(payload: dict[str, Any]) -> dict[str, Any]:
    """Encode a domain dict as an MCP text content block."""
    return {"content": [{"type": "text", "text": json.dumps(payload, default=str)}]}


def _make_seen_lookup(seen_path: Path) -> Callable:
    @tool(
        "seen_lookup",
        "Look up matches in seen.jsonl for a candidate brief before commit. "
        "Returns matches (exact_slug, exact_source_set, exact_lane_niche) and "
        "near_matches (subset/superset/single_host_overlap/partial_niche).",
        {"slug": str, "source_set": list, "lane_niche": list},
    )
    async def seen_lookup_tool(args: dict[str, Any]) -> dict[str, Any]:
        from mr.tools.seen_lookup import seen_lookup

        result = seen_lookup(
            seen_path=seen_path,
            slug=args.get("slug"),
            source_set=args.get("source_set"),
            lane_niche=tuple(args["lane_niche"]) if args.get("lane_niche") else None,
        )
        return _wrap_text(result)

    return seen_lookup_tool
```

- [ ] **Step 4: Run test to verify it passes**

Run: `rtk pytest tests/synth/test_mcp_server.py::test_seen_lookup_returns_matches -v`
Expected: PASS.

- [ ] **Step 5: Add wayback test + impl**

Append to `tests/synth/test_mcp_server.py`:

```python
@pytest.mark.anyio
@patch("mr.tools.wayback.wayback_check")
async def test_wayback_returns_count(mock_wayback):
    from mr.tools.wayback import WaybackResult
    mock_wayback.return_value = WaybackResult(count=42, first=date(2023, 1, 1), last=date(2026, 4, 30))
    result = await mcp_server._wayback({"url": "https://example.com/"})
    payload = _text_payload(result)
    assert payload["count"] == 42
    assert payload["first"] == "2023-01-01"
```

Append to `mr/synth/mcp_server.py`:

```python
@tool(
    "wayback",
    "Query Wayback Machine CDX for snapshot count and date range. Returns {count, first, last, years}.",
    {"url": str},
)
async def _wayback(args: dict[str, Any]) -> dict[str, Any]:
    from mr.tools.wayback import wayback_check
    result = wayback_check(args["url"])
    return _wrap_text({
        "count": result.count,
        "first": result.first.isoformat() if result.first else None,
        "last": result.last.isoformat() if result.last else None,
        "years": result.last.year - result.first.year if result.first and result.last else 0,
    })
```

Run: `rtk pytest tests/synth/test_mcp_server.py -v`
Expected: 2 tests PASS.

- [ ] **Step 6: Add robots test + impl**

Append to `tests/synth/test_mcp_server.py`:

```python
@pytest.mark.anyio
@patch("mr.tools.robots.robots_check")
async def test_robots_returns_allowed(mock_robots):
    from mr.tools.robots import RobotsResult
    mock_robots.return_value = RobotsResult(
        allowed=True, robots_url="https://example.com/robots.txt", error=None,
    )
    result = await mcp_server._robots({"url": "https://example.com/", "user_agent": "test"})
    payload = _text_payload(result)
    assert payload["allowed"] is True
```

Append to `mr/synth/mcp_server.py`:

```python
@tool(
    "robots",
    "Check robots.txt for the URL's origin. Returns {allowed, robots_url, error}.",
    {"url": str, "user_agent": str},
)
async def _robots(args: dict[str, Any]) -> dict[str, Any]:
    from mr.tools.robots import robots_check
    result = robots_check(args["url"], user_agent=args.get("user_agent", "moat-research"))
    return _wrap_text({
        "allowed": result.allowed,
        "robots_url": result.robots_url,
        "error": result.error,
    })
```

Run: `rtk pytest tests/synth/test_mcp_server.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Add head test + impl**

Append to `tests/synth/test_mcp_server.py`:

```python
@pytest.mark.anyio
@patch("mr.tools.head.head_check")
async def test_head_returns_status(mock_head):
    from mr.tools.head import HeadResult
    mock_head.return_value = HeadResult(
        status=200, content_type="text/html", last_modified=None, error=None,
    )
    result = await mcp_server._head({"url": "https://example.com/"})
    payload = _text_payload(result)
    assert payload["status"] == 200
    assert payload["content_type"] == "text/html"
```

Append to `mr/synth/mcp_server.py`:

```python
@tool(
    "head",
    "HTTP HEAD a URL. Returns {status, content_type, last_modified, error}.",
    {"url": str},
)
async def _head(args: dict[str, Any]) -> dict[str, Any]:
    from mr.tools.head import head_check
    result = head_check(args["url"])
    return _wrap_text({
        "status": result.status,
        "content_type": result.content_type,
        "last_modified": result.last_modified.isoformat() if result.last_modified else None,
        "error": result.error,
    })
```

Run: `rtk pytest tests/synth/test_mcp_server.py -v`
Expected: 4 tests PASS.

- [ ] **Step 8: Commit**

```bash
rtk git add mr/synth/mcp_server.py tests/synth/test_mcp_server.py
rtk git commit -m "feat(synth): mcp_server.py with seen_lookup, wayback, robots, head tools"
```

---

## Task 3: Add `code_eval` MCP tool with subprocess sandbox

**Files:**
- Modify: `mr/synth/mcp_server.py`
- Modify: `tests/synth/test_mcp_server.py`

**Rationale:** `prompts/discover.md` makes `code_execution` a hard requirement — every brief must emit a `code_execution` evidence row. Replace it with a subprocess Python runner with `RLIMIT_AS` (256 MB) and `RLIMIT_CPU` (30s) caps. The MCP tool is named `code_eval` (string), and the underlying Python function is `_run_code` (no namespace collision with Python's builtin).

- [ ] **Step 1: Write failing tests**

Append to `tests/synth/test_mcp_server.py`:

```python
@pytest.mark.anyio
async def test_run_code_simple():
    result = await mcp_server._run_code({"code": "print(1 + 1)"})
    payload = _text_payload(result)
    assert payload["exit_code"] == 0
    assert payload["stdout"].strip() == "2"


@pytest.mark.anyio
async def test_run_code_handles_timeout():
    result = await mcp_server._run_code(
        {"code": "import time; time.sleep(10)", "timeout_seconds": 1},
    )
    payload = _text_payload(result)
    assert payload.get("error") == "timeout"


@pytest.mark.anyio
async def test_run_code_handles_nonzero_exit():
    result = await mcp_server._run_code({"code": "raise ValueError('boom')"})
    payload = _text_payload(result)
    assert payload["exit_code"] != 0
    assert "ValueError" in payload["stderr"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `rtk pytest tests/synth/test_mcp_server.py -k run_code -v`
Expected: 3 tests FAIL with `AttributeError`.

- [ ] **Step 3: Implement `_run_code`**

Append imports to `mr/synth/mcp_server.py`:

```python
import os
import resource
import subprocess
import sys
import tempfile
```

Append constants and helper:

```python
_CODE_MEM_BYTES = 256 * 1024 * 1024
_CODE_CPU_SECONDS = 30
_CODE_DEFAULT_TIMEOUT = 30


def _apply_rlimits() -> None:
    """preexec_fn target — applies memory and CPU caps to the child process."""
    resource.setrlimit(resource.RLIMIT_AS, (_CODE_MEM_BYTES, _CODE_MEM_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (_CODE_CPU_SECONDS, _CODE_CPU_SECONDS))
```

Append the tool:

```python
@tool(
    "code_eval",
    "Run a short Python snippet in a sandboxed subprocess. "
    "Use for arithmetic, dedup math, and per-brief resource estimation. "
    "Memory cap 256MB, CPU cap 30s, no PATH inheritance. "
    "Returns {stdout, stderr, exit_code} or {error, stdout, stderr} on timeout.",
    {"code": str, "timeout_seconds": int},
)
async def _run_code(args: dict[str, Any]) -> dict[str, Any]:
    code = args["code"]
    timeout = int(args.get("timeout_seconds") or _CODE_DEFAULT_TIMEOUT)
    timeout = min(timeout, _CODE_DEFAULT_TIMEOUT)

    tmpdir = tempfile.mkdtemp(prefix="moat-code-")
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env={"PATH": "", "HOME": tmpdir, "TMPDIR": tmpdir},
            timeout=timeout,
            preexec_fn=_apply_rlimits if os.name == "posix" else None,
            check=False,
        )
        return _wrap_text({
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
        })
    except subprocess.TimeoutExpired as ex:
        return _wrap_text({
            "error": "timeout",
            "stdout": ex.stdout or "",
            "stderr": ex.stderr or "",
        })
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `rtk pytest tests/synth/test_mcp_server.py -k run_code -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add mr/synth/mcp_server.py tests/synth/test_mcp_server.py
rtk git commit -m "feat(synth): code_eval MCP tool with subprocess sandbox"
```

---

## Task 4: Add `firecrawl` tool and `build_server` factory

**Files:**
- Modify: `mr/synth/mcp_server.py`
- Modify: `tests/synth/test_mcp_server.py`

**Rationale:** `firecrawl` is conditional on `MR_FIRECRAWL_API_KEY` (mirrors current `tools_for_command` behavior). The `build_server` factory composes tools per-command and exposes the SDK MCP server object. Tools-per-command map preserves the spec's `score`-excludes-`WebSearch` rule.

- [ ] **Step 1: Write failing tests for firecrawl + build_server**

Append to `tests/synth/test_mcp_server.py`:

```python
@pytest.mark.anyio
@patch("mr.tools.firecrawl.scrape")
@patch("mr.tools.firecrawl.is_firecrawl_available", return_value=True)
async def test_firecrawl_when_available(_mock_avail, mock_scrape, tmp_path: Path):
    mock_scrape.return_value = {"markdown": "# Hello", "url": "https://example.com/"}
    fn = mcp_server._make_firecrawl()
    result = await fn({"url": "https://example.com/"})
    payload = _text_payload(result)
    assert payload["markdown"] == "# Hello"


def test_build_server_discover_includes_seen_and_code_tool(tmp_path: Path):
    server = mcp_server.build_server(
        seen_path=tmp_path / "seen.jsonl",
        firecrawl_available=False,
        command="discover",
    )
    names = mcp_server.tool_names_for(server)
    assert "seen_lookup" in names
    assert "code_eval" in names
    assert "wayback" in names
    assert "firecrawl" not in names


def test_build_server_score_excludes_seen(tmp_path: Path):
    server = mcp_server.build_server(
        seen_path=tmp_path / "seen.jsonl",
        firecrawl_available=False,
        command="score",
    )
    names = mcp_server.tool_names_for(server)
    assert "seen_lookup" not in names
    assert "wayback" in names
    assert "robots" in names
    assert "head" in names
    assert "code_eval" in names


def test_build_server_includes_firecrawl_when_available(tmp_path: Path):
    server = mcp_server.build_server(
        seen_path=tmp_path / "seen.jsonl",
        firecrawl_available=True,
        command="discover",
    )
    names = mcp_server.tool_names_for(server)
    assert "firecrawl" in names
```

- [ ] **Step 2: Run to verify they fail**

Run: `rtk pytest tests/synth/test_mcp_server.py -k 'firecrawl or build_server' -v`
Expected: 4 tests FAIL with `AttributeError`.

- [ ] **Step 3: Implement `_make_firecrawl`, `build_server`, `tool_names_for`, `allowed_tools_for`**

Append to `mr/synth/mcp_server.py`:

```python
def _make_firecrawl() -> Callable:
    @tool(
        "firecrawl",
        "Fallback for JS-rendered pages. Returns {markdown, url}. "
        "Only registered when MR_FIRECRAWL_API_KEY is set.",
        {"url": str},
    )
    async def firecrawl_tool(args: dict[str, Any]) -> dict[str, Any]:
        from mr.tools.firecrawl import scrape
        result = scrape(args["url"])
        return _wrap_text(result)

    return firecrawl_tool


_COMMAND_TOOLS: dict[str, list[str]] = {
    "discover": ["seen_lookup", "wayback", "code_eval", "firecrawl"],
    "score": ["wayback", "robots", "head", "code_eval"],
    "wishlist_expand": ["seen_lookup", "code_eval", "firecrawl"],
}


def build_server(
    *,
    seen_path: Path,
    firecrawl_available: bool,
    command: str,
):
    """Build an in-process MCP server with the tools needed for `command`.

    `seen_path` is captured by closure for `seen_lookup`. `firecrawl` is
    only registered when `firecrawl_available` is True.
    """
    wanted = _COMMAND_TOOLS.get(command, [])
    tools_list: list[Callable] = []
    for name in wanted:
        if name == "seen_lookup":
            tools_list.append(_make_seen_lookup(seen_path))
        elif name == "wayback":
            tools_list.append(_wayback)
        elif name == "robots":
            tools_list.append(_robots)
        elif name == "head":
            tools_list.append(_head)
        elif name == "code_eval":
            tools_list.append(_run_code)
        elif name == "firecrawl" and firecrawl_available:
            tools_list.append(_make_firecrawl())
    return create_sdk_mcp_server(name="moat", version="1.0.0", tools=tools_list)


def tool_names_for(server) -> set[str]:
    """Extract registered tool names from an SDK MCP server (for tests).

    The SDK exposes tools via `tools` (preferred) or `_tools` (older versions).
    Each tool callable is decorated by @tool and stores its name on
    `_tool_name` (verify against installed SDK version).
    """
    raw = getattr(server, "tools", None) or getattr(server, "_tools", None) or []
    names: set[str] = set()
    for t in raw:
        n = getattr(t, "_tool_name", None) or getattr(t, "name", None)
        if n:
            names.add(n)
    return names


MCP_TOOL_PREFIX = "mcp__moat__"


def allowed_tools_for(command: str, firecrawl_available: bool) -> list[str]:
    """Whitelist passed as `allowed_tools` to ClaudeAgentOptions.

    Includes our MCP tools plus Claude Code's `WebFetch` (always) and
    `WebSearch` (excluded for `score` to prevent drift into adjacent
    opportunities mid-evaluation, per prompts/score.md).
    """
    wanted = _COMMAND_TOOLS.get(command, [])
    out: list[str] = []
    for name in wanted:
        if name == "firecrawl" and not firecrawl_available:
            continue
        out.append(f"{MCP_TOOL_PREFIX}{name}")
    out.append("WebFetch")
    if command in ("discover", "wishlist_expand"):
        out.append("WebSearch")
    return out
```

- [ ] **Step 4: Run all mcp_server tests**

Run: `rtk pytest tests/synth/test_mcp_server.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Add allowed_tools tests**

Append to `tests/synth/test_mcp_server.py`:

```python
def test_allowed_tools_score_excludes_websearch():
    out = mcp_server.allowed_tools_for("score", firecrawl_available=False)
    assert "WebSearch" not in out
    assert "WebFetch" in out
    assert "mcp__moat__wayback" in out


def test_allowed_tools_discover_includes_websearch():
    out = mcp_server.allowed_tools_for("discover", firecrawl_available=False)
    assert "WebSearch" in out
    assert "mcp__moat__seen_lookup" in out
    assert "mcp__moat__firecrawl" not in out


def test_allowed_tools_includes_firecrawl_when_available():
    out = mcp_server.allowed_tools_for("discover", firecrawl_available=True)
    assert "mcp__moat__firecrawl" in out
```

Run: `rtk pytest tests/synth/test_mcp_server.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
rtk git add mr/synth/mcp_server.py tests/synth/test_mcp_server.py
rtk git commit -m "feat(synth): firecrawl tool, build_server factory, allowed_tools_for"
```

**Note for executor:** `tool_names_for` introspects SDK internals. If the installed SDK exposes a different attribute path than `_tool_name`, fix the helper before moving on — don't suppress failing tests.

---

## Task 5: Create `mr/synth/limits.py` (replaces budget.py)

**Files:**
- Create: `mr/synth/limits.py`
- Create: `tests/synth/test_limits.py`

**Rationale:** Slim runtime-limit module, no money. Holds `LimitExceeded`, `RunLimits` dataclass, and the `cold_corpus_preflight` function moved over from `budget.py`.

- [ ] **Step 1: Write failing tests**

Create `tests/synth/test_limits.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify failure**

Run: `rtk pytest tests/synth/test_limits.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create `mr/synth/limits.py`**

```python
"""Runtime limits (wallclock + tool-turn cap) and cold-corpus preflight.

Replaces mr.synth.budget for the Max-subscription port. No financial
tracking; SDK enforces tool turns via max_turns; wallclock is enforced
in mr.synth.session via asyncio.wait_for.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_MIN_WISHLIST_SOURCES = 5


class LimitExceeded(Exception):  # noqa: N818
    """Raised when any limit or preflight check fails."""


@dataclass
class RunLimits:
    max_tool_turns: int
    max_wallclock_seconds: int
    max_output_tokens: int


def run_limits_from_config(cfg: dict[str, Any], *, command: str) -> RunLimits:
    """Resolve per-command tool turn cap; flat values for the rest."""
    turns = cfg["max_tool_turns"]
    return RunLimits(
        max_tool_turns=turns.get(command, turns["default"]),
        max_wallclock_seconds=cfg["max_wallclock_seconds"],
        max_output_tokens=cfg["max_output_tokens"],
    )


def cold_corpus_preflight(wishlist_path: Path) -> None:
    """Refuse mr discover if WISHLIST.md has fewer than 5 sources."""
    if not wishlist_path.exists():
        raise LimitExceeded(
            f"WISHLIST.md not found at {wishlist_path}. "
            f"Run `mr wishlist expand --seed` to bootstrap."
        )
    raw = yaml.safe_load(wishlist_path.read_text()) or {}
    sources = raw.get("sources", []) or []
    if len(sources) < _MIN_WISHLIST_SOURCES:
        raise LimitExceeded(
            f"WISHLIST.md has {len(sources)} sources; minimum {_MIN_WISHLIST_SOURCES}. "
            f"Run `mr wishlist expand --seed` first."
        )
```

- [ ] **Step 4: Run tests to verify pass**

Run: `rtk pytest tests/synth/test_limits.py -v`
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add mr/synth/limits.py tests/synth/test_limits.py
rtk git commit -m "feat(synth): limits.py with RunLimits and cold_corpus_preflight"
```

---

## Task 6: Create `mr/synth/session.py`

**Files:**
- Create: `mr/synth/session.py`
- Create: `tests/synth/conftest.py`
- Create: `tests/synth/test_session.py`

**Rationale:** Single async entrypoint that wraps `claude_agent_sdk.query()` with a wallclock timeout and collects the final assistant text. Tests mock `query()` directly via a shared fixture.

- [ ] **Step 1: Create the shared `mock_query` fixture**

Create `tests/synth/conftest.py`:

```python
"""Shared fixtures for synth tests."""
from __future__ import annotations

from typing import Any, Callable
from unittest.mock import patch

import pytest


def _make_async_iter(messages: list[Any]):
    async def _iter(*_args, **_kwargs):
        for m in messages:
            yield m
    return _iter


@pytest.fixture
def mock_query() -> Callable:
    """Patch claude_agent_sdk.query to yield a fixed list of messages."""
    def _factory(messages: list[Any]):
        return patch(
            "mr.synth.session.query",
            side_effect=_make_async_iter(messages),
        )
    return _factory
```

- [ ] **Step 2: Write failing test for `session.run` happy path**

Create `tests/synth/test_session.py`:

```python
"""Tests for mr.synth.session.run."""
import asyncio
from types import SimpleNamespace

import pytest

from mr.synth import session
from mr.synth.limits import LimitExceeded


def _assistant_msg(*texts: str) -> SimpleNamespace:
    """Stand-in for AssistantMessage with TextBlock content."""
    blocks = [SimpleNamespace(text=t) for t in texts]
    msg = SimpleNamespace(content=blocks)
    return msg


@pytest.mark.anyio
async def test_session_run_returns_concatenated_text(mock_query):
    msgs = [_assistant_msg("Part 1. "), _assistant_msg("Part 2.")]
    with mock_query(msgs):
        out = await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            max_output_tokens=1024,
            wallclock_seconds=60,
        )
    assert "Part 1." in out
    assert "Part 2." in out


@pytest.mark.anyio
async def test_session_run_wallclock_timeout(monkeypatch):
    async def _slow(*_a, **_kw):
        await asyncio.sleep(5)
        if False:
            yield

    monkeypatch.setattr("mr.synth.session.query", _slow)
    with pytest.raises(LimitExceeded, match="wallclock cap exceeded"):
        await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            max_output_tokens=1024,
            wallclock_seconds=1,
        )


@pytest.mark.anyio
async def test_session_run_propagates_sdk_errors(monkeypatch):
    async def _boom(*_a, **_kw):
        raise RuntimeError("sdk down")
        yield

    monkeypatch.setattr("mr.synth.session.query", _boom)
    with pytest.raises(RuntimeError, match="sdk down"):
        await session.run(
            system_prompt="sys",
            user_prompt="usr",
            model="claude-sonnet-4-6",
            mcp_server=None,
            allowed_tools=[],
            max_turns=5,
            max_output_tokens=1024,
            wallclock_seconds=60,
        )
```

- [ ] **Step 3: Run tests to verify failure**

Run: `rtk pytest tests/synth/test_session.py -v`
Expected: 3 tests FAIL.

- [ ] **Step 4: Implement `mr/synth/session.py`**

```python
"""Single async entrypoint for Claude Agent SDK query.

Each `run()` call is a fresh, stateless one-shot session. Wallclock is
enforced via asyncio.wait_for; turn cap is delegated to the SDK's
max_turns option. Tool dispatch is delegated to the in-process MCP
server passed in.
"""
from __future__ import annotations

import asyncio
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from mr.synth.limits import LimitExceeded


async def run(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    mcp_server: Any,
    allowed_tools: list[str],
    max_turns: int,
    max_output_tokens: int,
    wallclock_seconds: int,
) -> str:
    """Run a single, one-shot Claude Agent SDK query and return the final text."""
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=model,
        mcp_servers={"moat": mcp_server} if mcp_server is not None else {},
        allowed_tools=allowed_tools,
        max_turns=max_turns,
        permission_mode="bypassPermissions",
    )

    async def _collect() -> str:
        parts: list[str] = []
        async for message in query(prompt=user_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
                    else:
                        text = getattr(block, "text", None)
                        if text:
                            parts.append(text)
            else:
                # Tolerate test stand-ins that aren't AssistantMessage.
                content = getattr(message, "content", None)
                if content:
                    for block in content:
                        text = getattr(block, "text", None)
                        if text:
                            parts.append(text)
        return "".join(parts)

    try:
        return await asyncio.wait_for(_collect(), timeout=wallclock_seconds)
    except asyncio.TimeoutError as ex:
        raise LimitExceeded(
            f"wallclock cap exceeded: {wallclock_seconds}s"
        ) from ex
```

- [ ] **Step 5: Run tests to verify pass**

Run: `rtk pytest tests/synth/test_session.py -v`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
rtk git add mr/synth/session.py tests/synth/conftest.py tests/synth/test_session.py
rtk git commit -m "feat(synth): session.run async entrypoint over Agent SDK query"
```

---

## Task 7: Update config schema and loader for `limits` section

**Files:**
- Modify: `mr/util/config_schema.json`
- Modify: `mr/util/config.py`
- Modify: `tests/util/test_config.py`

**Rationale:** Add `limits` alongside the existing `budgets` section (kept temporarily for back-compat with v1 configs). v2 schema bump and migrate flag come in Task 13.

- [ ] **Step 1: Add `limits` to schema**

In `mr/util/config_schema.json`, add this property block alongside the existing `budgets`:

```json
"limits": {
  "type": "object",
  "required": ["max_tool_turns", "max_wallclock_seconds", "max_output_tokens"],
  "properties": {
    "max_tool_turns": {
      "type": "object",
      "required": ["default"],
      "additionalProperties": {"type": "integer", "minimum": 1},
      "properties": {"default": {"type": "integer", "minimum": 1}}
    },
    "max_wallclock_seconds": {"type": "integer", "minimum": 1},
    "max_output_tokens": {"type": "integer", "minimum": 1}
  }
}
```

- [ ] **Step 2: Expose `limits` on `Config`**

Read `mr/util/config.py` first to match the existing accessor style. If `Config` is a dataclass with explicit fields, add a `limits: dict[str, Any]` field. If it stores the raw parsed dict and exposes properties, add:

```python
@property
def limits(self) -> dict[str, Any]:
    return self._raw.get("limits", {
        "max_tool_turns": {"default": 12, "discover": 20, "score": 8, "wishlist_expand": 10},
        "max_wallclock_seconds": 600,
        "max_output_tokens": 8192,
    })
```

- [ ] **Step 3: Add a test that loads a config with `limits`**

Append to `tests/util/test_config.py`:

```python
def test_config_exposes_limits(tmp_path: Path):
    from mr.util.config import load_config
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("""\
schema_version: 1
models:
  default: claude-opus-4-7
budgets:
  max_tokens_per_turn: 4096
  base_input_tokens: 12000
  avg_tool_result_tokens: 800
  max_tool_turns: {default: 8}
  max_wallclock_seconds: 600
limits:
  max_tool_turns: {default: 12, discover: 20}
  max_wallclock_seconds: 600
  max_output_tokens: 8192
""")
    cfg = load_config(cfg_path)
    assert cfg.limits["max_tool_turns"]["discover"] == 20
    assert cfg.limits["max_wallclock_seconds"] == 600
```

- [ ] **Step 4: Run tests**

Run: `rtk pytest tests/util/test_config.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add mr/util/config_schema.json mr/util/config.py tests/util/test_config.py
rtk git commit -m "feat(config): add limits section alongside budgets"
```

---

## Task 8: Rewrite `mr/cli/discover.py` to use `session.run`

**Files:**
- Modify: `mr/cli/discover.py`
- Modify: `tests/cli/test_discover.py`
- Modify: `tests/integration/test_e2e.py`
- Modify: `mr/cli/main.py`

**Rationale:** Highest-risk task — replaces the actual runtime path. Drops the hand-rolled tool-use loop, the cost ledger, and the `--budget` flag. Keeps `_extract_candidates` and `_write_candidates` (parsers/writers don't change).

- [ ] **Step 1: Rewrite `mr/cli/discover.py`**

Replace the entire file with:

```python
"""mr discover — generate candidate briefs from WISHLIST + Agent SDK."""
from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

from mr.dedup.niche_key import resolve_niche_key
from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.dedup.summary import build_summary_block
from mr.lifecycle.filename import candidate_filename, resolve_collision
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.synth import mcp_server, session
from mr.synth.limits import cold_corpus_preflight, run_limits_from_config
from mr.synth.prompts import load_prompt
from mr.tools.firecrawl import is_firecrawl_available
from mr.util.config import Config, load_config
from mr.util.lock import exclusive_lock
from mr.util.slug import slugify


def discover(root: Path, lane: str | None, n: int) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    cold_corpus_preflight(layout.wishlist_path)

    with exclusive_lock(layout.lock_path):
        if is_stale(layout):
            regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

        candidates = asyncio.run(_async_discover(layout=layout, cfg=cfg, lane=lane, n=n))
        _write_candidates(candidates, layout=layout, cfg=cfg)


async def _async_discover(
    *, layout: RepoLayout, cfg: Config, lane: str | None, n: int,
) -> list[dict[str, Any]]:
    summary = build_summary_block(read_seen(layout.seen_path))
    wishlist_text = layout.wishlist_path.read_text()
    system_text = load_prompt(layout.prompts_dir, "discover")

    system_prompt = (
        f"{system_text}\n\n"
        f"## Current WISHLIST\n```yaml\n{wishlist_text}\n```\n\n"
        f"## Seen Summary\n{summary}\n"
    )

    lane_clause = (
        f"Generate exactly {n} candidates in lane `{lane}`."
        if lane else
        f"Generate exactly {n} candidates, distributing across underrepresented (lane, niche_key) cells."
    )
    user_prompt = (
        f"{lane_clause} For each, output the full YAML frontmatter + body per spec §6.4. "
        f"Wrap each candidate in fenced ```yaml-brief blocks so the runner can extract them. "
        f"Use seen_lookup before commit; populate verification_evidence; honor the affirm/avoid "
        f"interest filter; obey the diversity bias."
    )

    fc_avail = is_firecrawl_available()
    server = mcp_server.build_server(
        seen_path=layout.seen_path,
        firecrawl_available=fc_avail,
        command="discover",
    )
    allowed = mcp_server.allowed_tools_for("discover", firecrawl_available=fc_avail)
    limits = run_limits_from_config(cfg.limits, command="discover")

    final_text = await session.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=cfg.models.get("per_command", {}).get("discover", cfg.models["default"]),
        mcp_server=server,
        allowed_tools=allowed,
        max_turns=limits.max_tool_turns,
        max_output_tokens=limits.max_output_tokens,
        wallclock_seconds=limits.max_wallclock_seconds,
    )
    return _extract_candidates(final_text)


def _extract_candidates(full: str) -> list[dict[str, Any]]:
    """Parse ```yaml-brief fenced blocks from the assistant's final text."""
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
    for c in candidates:
        fm = c["frontmatter"]
        body = c["body"]
        slug = slugify(fm.get("slug") or fm.get("title", "untitled"))
        niche_key = resolve_niche_key(fm.get("niche", "untagged"), cfg.niche_aliases)
        date_created = fm.get("date_created", date.today().isoformat())
        if isinstance(date_created, str):
            date_created = date.fromisoformat(date_created)
        brief = Brief(
            schema_version=1,
            title=fm["title"], slug=slug, lane=fm["lane"], niche=fm["niche"],
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

- [ ] **Step 2: Update `tests/cli/test_discover.py`**

Read the existing file first. Remove the `discover_aborts_when_anthropic_api_key_missing` test (no longer relevant). Add pure-function tests for `_extract_candidates`:

```python
from mr.cli.discover import _extract_candidates


def test_extract_candidates_parses_yaml_brief_blocks():
    text = """
some preamble
```yaml-brief
frontmatter:
  title: Foo
  slug: foo
  lane: a
  niche: b
  sources: [{host: example.com}]
body: |
  Foo body.
```
trailing
"""
    out = _extract_candidates(text)
    assert len(out) == 1
    assert out[0]["frontmatter"]["title"] == "Foo"


def test_extract_candidates_skips_malformed_yaml():
    text = "```yaml-brief\nnot: [valid: yaml\n```"
    assert _extract_candidates(text) == []
```

For the existing `discover_dispatches_to_loop` test, replace with `discover_invokes_session_run` that mocks `mr.cli.discover.session.run` (use `unittest.mock.AsyncMock`) and asserts it was awaited with `command="discover"` propagated to `mcp_server.build_server` and `mcp_server.allowed_tools_for`.

- [ ] **Step 3: Update `tests/integration/test_e2e.py`**

Replace the existing `SynthClient` mock seam with a `session.run` mock seam. Read the existing file first; preserve fixture wiring. Patch target changes from `mr.synth.client.SynthClient.create_message` (or wherever it's mocked) to `mr.cli.discover.session.run` returning a fixed `final_text` containing one or more ```yaml-brief blocks.

- [ ] **Step 4: Update typer command registration**

In `mr/cli/main.py`, find the `mr discover` command registration and remove the `--budget` parameter. Confirm the typer command body calls `discover(root, lane, n)` with the new signature.

- [ ] **Step 5: Run all relevant tests**

Run: `rtk pytest tests/cli/test_discover.py tests/integration/test_e2e.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
rtk git add mr/cli/discover.py mr/cli/main.py tests/cli/test_discover.py tests/integration/test_e2e.py
rtk git commit -m "feat(cli): rewrite discover on Claude Agent SDK session"
```

---

## Task 9: Rewrite `mr/cli/score.py`

**Files:**
- Modify: `mr/cli/score.py`
- Modify: `tests/cli/test_score.py`
- Modify: `mr/cli/main.py`

**Rationale:** Same trim pattern as discover. Drops `BudgetTracker`, `append_cost`, the `while True:` loop, and the `--budget` flag. Keeps `_score_one`, `_extract_scores`, `_serialize_brief`, `_route_to_rejected` verbatim.

- [ ] **Step 1: Rewrite `mr/cli/score.py`**

Replace the file with:

```python
"""mr score — score, verify, route to scored/ or rejected/."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import typer

from mr.dedup.seen import is_stale, regenerate_seen
from mr.lifecycle.filename import resolve_collision, scored_filename
from mr.lifecycle.frontmatter import Brief, read_brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import move_brief
from mr.scoring.auto_reject import (
    REASON_STRINGS,
    AutoRejectReason,
    decide_floor_rejection,
)
from mr.scoring.rubric import Scores, composite
from mr.synth import mcp_server, session
from mr.synth.limits import run_limits_from_config
from mr.synth.prompts import load_prompt
from mr.synth.verify import verify_disqualifier_check
from mr.tools.firecrawl import is_firecrawl_available
from mr.util.config import Config, load_config
from mr.util.lock import exclusive_lock


def score(paths: list[Path], root: Path) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    with exclusive_lock(layout.lock_path):
        if is_stale(layout):
            regenerate_seen(layout, niche_aliases=cfg.niche_aliases)
        for path in paths:
            _score_one(path, layout=layout, cfg=cfg)


def _score_one(src: Path, *, layout: RepoLayout, cfg: Config) -> None:  # noqa: PLR0911
    brief = read_brief(src)

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

    scores_dict = asyncio.run(_async_score(brief=brief, layout=layout, cfg=cfg))
    s = Scores(
        defensibility=scores_dict["defensibility"],
        financial=scores_dict["financial"],
        implementation=scores_dict["implementation"],
        hardware=scores_dict["hardware"],
    )

    floor = decide_floor_rejection(s)
    if floor is not None:
        _route_to_rejected(brief, src, layout, REASON_STRINGS[floor], scores=s)
        return

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


async def _async_score(
    *, brief: Brief, layout: RepoLayout, cfg: Config,
) -> dict[str, int]:
    system_prompt = load_prompt(layout.prompts_dir, "score")

    user_prompt = (
        "Score the following candidate brief on the 4-axis rubric (defensibility, financial, "
        "implementation, hardware), each 0-10 integer. Output ONLY a JSON object "
        '{"defensibility": int, "financial": int, "implementation": int, "hardware": int}.\n\n'
        f"Brief:\n```\n{_serialize_brief(brief)}\n```"
    )

    fc_avail = is_firecrawl_available()
    server = mcp_server.build_server(
        seen_path=layout.seen_path,
        firecrawl_available=fc_avail,
        command="score",
    )
    allowed = mcp_server.allowed_tools_for("score", firecrawl_available=fc_avail)
    limits = run_limits_from_config(cfg.limits, command="score")

    final_text = await session.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=cfg.models.get("per_command", {}).get("score", cfg.models["default"]),
        mcp_server=server,
        allowed_tools=allowed,
        max_turns=limits.max_tool_turns,
        max_output_tokens=limits.max_output_tokens,
        wallclock_seconds=limits.max_wallclock_seconds,
    )
    return _extract_scores(final_text)


def _extract_scores(text: str) -> dict[str, int]:
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
    return f"""title: {brief.title}
slug: {brief.slug}
lane: {brief.lane}
niche: {brief.niche}
sources: {brief.sources}
disqualifier_verdicts: {brief.disqualifier_verdicts}
{brief.body}"""


def _route_to_rejected(
    brief: Brief, src: Path, layout: RepoLayout, reason: str,
    scores: Scores | None = None,
) -> None:
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

- [ ] **Step 2: Update `tests/cli/test_score.py`**

Mock `mr.cli.score.session.run` (using `unittest.mock.AsyncMock`) to return canned JSON-only assistant text. Adapt the existing test cases:
- `score_routes_to_rejected_when_hw_keys_missing` — unchanged (verify path is pre-LLM).
- `score_routes_to_scored_when_predicates_pass` — patch `session.run` to return `'{"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 5}'`.
- `score_floor_rejection_low_defensibility` — patch `session.run` to return `'{"defensibility": 2, "financial": 8, "implementation": 8, "hardware": 8}'`.

- [ ] **Step 3: Update typer command signature in `mr/cli/main.py`**

Remove the `--budget` flag from `mr score`. Confirm the typer command body calls `score(paths, root)` with the new signature.

- [ ] **Step 4: Run tests**

Run: `rtk pytest tests/cli/test_score.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add mr/cli/score.py mr/cli/main.py tests/cli/test_score.py
rtk git commit -m "feat(cli): rewrite score on Claude Agent SDK session"
```

---

## Task 10: Rewrite `mr/wishlist/expand.py`

**Files:**
- Modify: `mr/wishlist/expand.py`
- Modify: `tests/wishlist/test_expand.py`
- Modify: `tests/cli/test_wishlist_cli.py`
- Modify: `mr/cli/wishlist.py`

**Rationale:** Same trim pattern as discover/score. The expand subcommand uses the synth loop to propose new WISHLIST sources.

- [ ] **Step 1: Read the existing file**

Run: `rtk read mr/wishlist/expand.py`
Note the loop shape and any expand-specific parsing helpers (e.g., `format_proposal`).

- [ ] **Step 2: Rewrite `mr/wishlist/expand.py`**

Apply the same shape as discover: a pure async function `_async_expand` that builds prompts, calls `session.run`, and returns parsed proposals; sync entrypoint that wraps with `asyncio.run`.

Replace any `SynthClient` / `BudgetTracker` / `dispatch_tool_call` usage with:

```python
from mr.synth import mcp_server, session
from mr.synth.limits import run_limits_from_config

# Inside the new _async_expand:
fc_avail = is_firecrawl_available()
server = mcp_server.build_server(
    seen_path=layout.seen_path,
    firecrawl_available=fc_avail,
    command="wishlist_expand",
)
allowed = mcp_server.allowed_tools_for("wishlist_expand", firecrawl_available=fc_avail)
limits = run_limits_from_config(cfg.limits, command="wishlist_expand")

final_text = await session.run(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    model=cfg.models.get("per_command", {}).get("wishlist_expand", cfg.models["default"]),
    mcp_server=server,
    allowed_tools=allowed,
    max_turns=limits.max_tool_turns,
    max_output_tokens=limits.max_output_tokens,
    wallclock_seconds=limits.max_wallclock_seconds,
)
```

Keep `format_proposal` and any other parsing helpers verbatim.

- [ ] **Step 3: Update CLI entrypoint**

Remove the `--budget` flag from `mr wishlist expand` in `mr/cli/wishlist.py`.

- [ ] **Step 4: Update tests**

Mock `mr.wishlist.expand.session.run` (`AsyncMock`) in `tests/wishlist/test_expand.py` and `tests/cli/test_wishlist_cli.py`. Pure-function tests like `format_proposal_renders_yaml_blocks` and `format_proposal_empty` should still pass unmodified.

- [ ] **Step 5: Run tests**

Run: `rtk pytest tests/wishlist/ tests/cli/test_wishlist_cli.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
rtk git add mr/wishlist/expand.py mr/cli/wishlist.py tests/wishlist/test_expand.py tests/cli/test_wishlist_cli.py
rtk git commit -m "feat(wishlist): rewrite expand on Claude Agent SDK session"
```

---

## Task 11: Drop `gain` subcommand and delete cost-tracking files

**Files:**
- Delete: `mr/cli/gain.py`
- Delete: `mr/util/costs.py`
- Delete: `tests/cli/test_gain.py`
- Delete: `tests/util/test_costs.py`
- Modify: `mr/cli/main.py`

**Rationale:** Cost tracking is meaningless under Max. Remove the user-facing `gain` command and its supporting module.

- [ ] **Step 1: Remove `gain` registration from `mr/cli/main.py`**

Find the line that registers `mr gain` (likely `app.command("gain")(gain)` or via a Typer sub-app) and remove both the registration and the `from mr.cli.gain import gain` import.

- [ ] **Step 2: Delete the files**

```bash
rm mr/cli/gain.py mr/util/costs.py tests/cli/test_gain.py tests/util/test_costs.py
```

- [ ] **Step 3: Verify no dangling references**

Run: `rtk grep -rn 'from mr.util.costs\|from mr.cli.gain\|mr.util.costs\|mr.cli.gain\|append_cost\|CostRecord\|running_total' mr tests`
Expected: no matches.

- [ ] **Step 4: Run full test suite**

Run: `rtk pytest`
Expected: all remaining tests PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add -A
rtk git commit -m "feat(cli): remove gain command and cost-tracking modules"
```

---

## Task 12: Delete legacy synth files

**Files:**
- Delete: `mr/synth/client.py`
- Delete: `mr/synth/dispatch.py`
- Delete: `mr/synth/tools.py`
- Delete: `mr/synth/pricing.py`
- Delete: `mr/synth/budget.py`
- Delete: `tests/synth/test_client.py`
- Delete: `tests/synth/test_dispatch.py`
- Delete: `tests/synth/test_tools.py`
- Delete: `tests/synth/test_pricing.py`
- Delete: `tests/synth/test_budget.py`

**Rationale:** All callers were migrated in Tasks 8–10. These files are now dead.

- [ ] **Step 1: Verify no remaining imports**

Run: `rtk grep -rn 'from mr.synth.client\|from mr.synth.dispatch\|from mr.synth.tools\|from mr.synth.pricing\|from mr.synth.budget\|SynthClient\|build_cached_blocks\|dispatch_tool_call\|tools_for_command\|BudgetTracker\|BudgetExceeded\|worst_case_ceiling\|get_pricing' mr tests`

Expected: no matches. If any surface, they're missed callsites — fix them in this task before deleting.

- [ ] **Step 2: Delete the files**

```bash
rm mr/synth/client.py mr/synth/dispatch.py mr/synth/tools.py mr/synth/pricing.py mr/synth/budget.py
rm tests/synth/test_client.py tests/synth/test_dispatch.py tests/synth/test_tools.py tests/synth/test_pricing.py tests/synth/test_budget.py
```

- [ ] **Step 3: Run full test suite**

Run: `rtk pytest`
Expected: all remaining tests PASS.

- [ ] **Step 4: Commit**

```bash
rtk git add -A
rtk git commit -m "feat(synth): remove legacy Anthropic-SDK code paths"
```

---

## Task 13: Bump config schema to v2 and add `mr init --migrate`

**Files:**
- Modify: `mr/util/config_schema.json`
- Modify: `mr/util/config.py`
- Modify: `mr/cli/init.py`
- Modify: `tests/util/test_config.py`
- Modify: `tests/cli/test_init.py`

**Rationale:** Existing `mr.yaml` files have a `budgets` section that's no longer meaningful. Bump schema to v2 (no `budgets`, requires `limits`). Loader rejects v1 configs with a one-line message; on the user side, `mr init --migrate` backs up to `mr.yaml.bak` and writes a fresh v2 config.

- [ ] **Step 1: Update schema**

In `mr/util/config_schema.json`:
- Change `schema_version` (enum or const) to allow only `2`.
- Remove `budgets` from `properties` and `required`.
- Add `limits` to `required`.

- [ ] **Step 2: Update loader**

In `mr/util/config.py`, find the schema-version check (currently asserts `schema_version == 1`). Change to:

```python
if raw.get("schema_version") == 1:
    raise ConfigError(
        "mr.yaml uses schema_version 1 (pre Max-subscription port). "
        "Run `mr init --migrate` to upgrade. The old file will be saved as mr.yaml.bak."
    )
if raw.get("schema_version") != 2:
    raise ConfigError(f"unsupported schema_version: {raw.get('schema_version')}")
```

(Match the existing `ConfigError` symbol or whatever the file uses.)

- [ ] **Step 3: Add `--migrate` flag to `mr init`**

In `mr/cli/init.py`:

```python
def init(root: Path, migrate: bool = False) -> None:
    layout = RepoLayout(root)
    if layout.config_path.exists():
        if not migrate:
            typer.echo(f"{layout.config_path} already exists; pass --migrate to overwrite.")
            raise typer.Exit(code=1)
        backup = layout.config_path.with_suffix(".yaml.bak")
        layout.config_path.rename(backup)
        typer.echo(f"backed up existing config to {backup}")
    _write_default_config(layout.config_path)
    # ... existing dir/prompt/wishlist scaffolding ...
```

Update `_write_default_config` (or whatever writes the default `mr.yaml`) to emit `schema_version: 2` and a `limits` section, with no `budgets` section.

- [ ] **Step 4: Update tests**

In `tests/util/test_config.py`: change all test fixture `mr.yaml` strings to `schema_version: 2` and add a `limits` block. Add a new test:

```python
def test_v1_config_rejected_with_migrate_message(tmp_path: Path):
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("schema_version: 1\nmodels: {default: x}\n")
    with pytest.raises(Exception, match="mr init --migrate"):
        load_config(cfg_path)
```

In `tests/cli/test_init.py`: add `test_init_migrate_overwrites_existing` and `test_init_aborts_when_config_exists_without_migrate`.

- [ ] **Step 5: Run tests**

Run: `rtk pytest tests/util/test_config.py tests/cli/test_init.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
rtk git add mr/util/config_schema.json mr/util/config.py mr/cli/init.py tests/util/test_config.py tests/cli/test_init.py
rtk git commit -m "feat(config): bump schema to v2; add mr init --migrate"
```

---

## Task 14: Remove `anthropic` dependency

**Files:**
- Modify: `pyproject.toml`

**Rationale:** No code imports `anthropic` after Task 12. Drop the dependency.

- [ ] **Step 1: Verify no remaining imports**

Run: `rtk grep -rn 'import anthropic\|from anthropic' mr tests`
Expected: no matches.

- [ ] **Step 2: Remove from `pyproject.toml`**

Edit the `dependencies` list:

```toml
dependencies = [
    "claude-agent-sdk>=0.0.20",
    "typer>=0.12.0",
    "pyyaml>=6.0",
    "httpx>=0.27.0",
    "jsonschema>=4.21.0",
    "waybackpy>=3.0.6",
    "rich>=13.7.0",
]
```

- [ ] **Step 3: Reinstall and run tests**

Run:
```bash
pip install -e ".[dev]"
rtk pytest
```
Expected: all tests PASS, no `ImportError` for `anthropic`.

- [ ] **Step 4: Commit**

```bash
rtk git add pyproject.toml
rtk git commit -m "deps: drop anthropic; project is Max-only via claude-agent-sdk"
```

---

## Task 15: Update `README.md` for Max-only operation

**Files:**
- Modify: `README.md`
- Modify: `WISHLIST.md` (only if it contains API-key references)

**Rationale:** Surface the new runtime requirement and prerequisites so a future user (or future you) doesn't try `ANTHROPIC_API_KEY=...` and get a confusing failure.

- [ ] **Step 1: Read the existing README**

Run: `rtk read README.md`
Note any sections mentioning `ANTHROPIC_API_KEY`, "API access", costs, `mr gain`, or `--budget`.

- [ ] **Step 2: Update README**

Replace any "Prerequisites" section with:

```markdown
## Prerequisites

- Python 3.12+
- An active Claude Max subscription
- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and authenticated locally (`claude --version`)

The `mr` CLI uses the Claude Agent SDK to ride your Max subscription via the local `claude` binary. There is no `ANTHROPIC_API_KEY` configuration. Each invocation of `mr discover`, `mr score`, or `mr wishlist expand` opens a one-shot session through Claude Code.

Optional:
- `MR_FIRECRAWL_API_KEY` — enables the `firecrawl` MCP tool for JS-rendered pages.
```

Remove any other references to API keys, metered costs, `mr gain`, `--budget` flags, or `costs.jsonl`.

- [ ] **Step 3: Update WISHLIST.md only if needed**

Run: `rtk grep -n 'ANTHROPIC_API_KEY\|--budget\|costs.jsonl\|mr gain' WISHLIST.md`
If any matches, edit them out.

- [ ] **Step 4: Commit**

```bash
rtk git add README.md WISHLIST.md
rtk git commit -m "docs: document Max-subscription runtime; drop API-key references"
```

---

## Final verification

- [ ] **Step 1: Full test suite**

Run: `rtk pytest`
Expected: all tests PASS.

- [ ] **Step 2: Confirm no Anthropic-SDK residue**

Run: `rtk grep -rn 'anthropic\|ANTHROPIC_API_KEY\|SynthClient\|BudgetTracker\|costs.jsonl\|mr gain\|--budget' mr tests README.md`
Expected: zero matches outside historical docs/specs.

- [ ] **Step 3: Live smoke test (optional, requires Max + Claude Code)**

```bash
mr init --migrate
mr wishlist expand --seed
mr discover --lane experimental --n 1
```
Expected: `created candidates/...md` printed.

---

## Rollback note

The Anthropic-SDK path is preserved in git history through Task 11. To revert: `git revert` the range of commits, or `git reset --hard <pre-Task-1-sha>` if no other work has happened. The `anthropic` dependency would need to be re-added to `pyproject.toml`.
