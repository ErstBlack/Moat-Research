"""In-process MCP server wrapping the project's custom tools.

Tools delegate to existing implementations under mr.tools.* and
mr.dedup.seen_lookup. The factory `build_server` (Task 4) captures `seen_path`
via closure so per-invocation state stays out of the tool signature.

Module-level names ``_wayback``, ``_robots``, ``_head`` are ``SdkMcpTool``
objects (decorated with ``@tool``). Tests invoke them via ``.handler({...})``.
``_make_seen_lookup`` returns an ``SdkMcpTool`` for the same reason — the
inner function is decorated inside the factory so ``seen_path`` is captured.
"""
from __future__ import annotations

import asyncio
import json
import os
import resource
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import mcp.types as _mcp_types
from claude_agent_sdk import create_sdk_mcp_server, tool


def _wrap_text(payload: dict[str, Any]) -> dict[str, Any]:
    """Encode a domain dict as an MCP text content block."""
    return {"content": [{"type": "text", "text": json.dumps(payload, default=str)}]}


_CODE_MEM_BYTES = 256 * 1024 * 1024
_CODE_CPU_SECONDS = 30
_CODE_DEFAULT_TIMEOUT = 30


def _apply_rlimits() -> None:
    """preexec_fn target — applies memory and CPU caps to the child process."""
    resource.setrlimit(resource.RLIMIT_AS, (_CODE_MEM_BYTES, _CODE_MEM_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (_CODE_CPU_SECONDS, _CODE_CPU_SECONDS))


def _make_seen_lookup(seen_path: Path):
    """Return an SdkMcpTool for seen_lookup, capturing seen_path via closure."""

    @tool(
        "seen_lookup",
        "Query seen.jsonl for exact or near-matches by slug, source_set, or lane_niche.",
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
        return _wrap_text({
            "matches": result.matches,
            "near_matches": result.near_matches,
        })

    return seen_lookup_tool


@tool(
    "wayback",
    "Query Wayback Machine CDX for snapshot count and date range. Returns {count, first, last, years}.",
    {"url": str},
)
async def _wayback(args: dict[str, Any]) -> dict[str, Any]:
    """Query Wayback Machine CDX for snapshot count and date range."""
    from mr.tools.wayback import wayback_check
    result = wayback_check(args["url"])
    return _wrap_text({
        "count": result.count,
        "first": result.first.isoformat() if result.first else None,
        "last": result.last.isoformat() if result.last else None,
        "years": result.years,
    })


@tool(
    "robots",
    "Check robots.txt for the URL's origin. Returns {allowed, robots_url, error}.",
    {"url": str, "user_agent": str},
)
async def _robots(args: dict[str, Any]) -> dict[str, Any]:
    """Check robots.txt for the URL's origin."""
    from mr.tools.robots import robots_check
    result = robots_check(args["url"], user_agent=args.get("user_agent", "moat-research"))
    return _wrap_text({
        "allowed": result.allowed,
        "robots_url": result.robots_url,
        "error": result.error,
    })


@tool(
    "head",
    "HTTP HEAD a URL. Returns {status, content_type, last_modified, error}.",
    {"url": str},
)
async def _head(args: dict[str, Any]) -> dict[str, Any]:
    """HTTP HEAD a URL."""
    from mr.tools.head import head_check
    result = head_check(args["url"])
    return _wrap_text({
        "status": result.status,
        "content_type": result.content_type,
        "last_modified": result.last_modified.isoformat() if result.last_modified else None,
        "error": result.error,
    })


@tool(
    "code_eval",
    "Run a short Python snippet in a sandboxed subprocess. "
    "Use for arithmetic, dedup math, and per-brief resource estimation. "
    "Limits: 256MB memory (RLIMIT_AS), 30s wall-clock (subprocess timeout), "
    "30s CPU time (RLIMIT_CPU), no PATH inheritance, ephemeral working dir. "
    "Returns {stdout, stderr, exit_code} or {error: 'timeout', stdout, stderr} on wall-clock timeout.",
    {"code": str, "timeout_seconds": int},
)
async def _run_code(args: dict[str, Any]) -> dict[str, Any]:
    code = args["code"]
    timeout = int(args.get("timeout_seconds") or _CODE_DEFAULT_TIMEOUT)
    timeout = min(timeout, _CODE_DEFAULT_TIMEOUT)

    with tempfile.TemporaryDirectory(prefix="moat-code-") as tmpdir:
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
                close_fds=True,
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


def _make_firecrawl():
    """Return an SdkMcpTool for firecrawl. Only call when firecrawl is available."""

    @tool(
        "firecrawl",
        "Fallback for JS-rendered pages. Returns {markdown, url}. "
        "Only registered when MR_FIRECRAWL_API_KEY is set.",
        {"url": str},
    )
    async def firecrawl_tool(args: dict[str, Any]) -> dict[str, Any]:
        from mr.tools.firecrawl import firecrawl_scrape
        result = firecrawl_scrape(args["url"])
        return _wrap_text({"markdown": result.markdown, "url": result.url})

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

    `seen_path` is captured via closure for `seen_lookup`. `firecrawl` is
    only registered when `firecrawl_available` is True.
    """
    wanted = _COMMAND_TOOLS.get(command, [])
    tools_list = []
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


async def _collect_tool_names(server) -> set[str]:
    """Async helper: call the MCP server's list_tools handler and return names.

    SDK server is a McpSdkServerConfig dict with 'instance' key pointing to an
    mcp.server.lowlevel.server.Server. The ListToolsRequest handler returns a
    ServerResult whose .root is a ListToolsResult with a .tools list.
    """
    instance = server["instance"]
    handler = instance.request_handlers.get(_mcp_types.ListToolsRequest)
    if not handler:
        return set()
    result = await handler(None)
    # result is ServerResult; .root is ListToolsResult with .tools
    tools_list = getattr(result.root, "tools", [])
    return {t.name for t in tools_list}


def tool_names_for(server) -> set[str]:
    """Extract registered tool names from an SDK MCP server.

    The SDK MCP server (McpSdkServerConfig) is a dict with an 'instance' key
    holding an mcp.server.lowlevel.server.Server. Tool names are retrieved by
    calling the ListToolsRequest handler; result.root.tools holds Tool objects
    with .name attributes.
    """
    return asyncio.run(_collect_tool_names(server))


MCP_TOOL_PREFIX = "mcp__moat__"


def allowed_tools_for(command: str, firecrawl_available: bool) -> list[str]:
    """Whitelist passed as `allowed_tools` to ClaudeAgentOptions.

    Includes our MCP tools (prefixed `mcp__moat__`) plus Claude Code's
    `WebFetch` (always) and `WebSearch` (excluded for `score` to prevent
    drift into adjacent opportunities, per prompts/score.md).
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
