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
    FirecrawlNotConfiguredError,
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
            except FirecrawlNotConfiguredError as e:
                return {"error": str(e)}

        return {"error": f"unknown tool: {name}"}
    except Exception as e:  # noqa: BLE001
        return {"error": f"{name} failed: {e}"}
