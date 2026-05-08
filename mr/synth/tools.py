"""Tool definitions for Anthropic API requests.

Spec §8.2: tool set per subcommand.
Spec §12.3: seen_lookup custom tool schema.
"""
from __future__ import annotations

from typing import Any

NATIVE_TOOL_DEFS: dict[str, dict[str, Any]] = {
    "web_search": {"type": "web_search_20260209"},
    "web_fetch": {"type": "web_fetch_20260209"},
    "code_execution": {"type": "code_execution_20260209"},
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
        "description": (
            "Query Wayback Machine CDX for snapshot count and date range. "
            "Returns {count, first, last, years}."
        ),
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
        "description": (
            "Check robots.txt for the URL's origin. Returns {allowed, robots_url, error}."
        ),
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
}

# Per-command tool inclusion (§8.2)
_COMMAND_TOOLS: dict[str, list[str]] = {
    "discover": [
        "web_search",
        "web_fetch",
        "code_execution",
        "seen_lookup",
        "wayback_check",
    ],
    "score": [
        "web_fetch",
        "code_execution",
        "wayback_check",
        "robots_check",
        "head_check",
    ],
    "wishlist_expand": [
        "web_search",
        "web_fetch",
        "code_execution",
        "seen_lookup",
    ],
}


def tools_for_command(command: str) -> list[dict[str, Any]]:
    """Return the tool definitions list for `command`, in API request shape."""
    out: list[dict[str, Any]] = []
    for name in _COMMAND_TOOLS.get(command, []):
        if name in NATIVE_TOOL_DEFS:
            out.append(NATIVE_TOOL_DEFS[name])
        elif name in CUSTOM_TOOL_DEFS:
            out.append(CUSTOM_TOOL_DEFS[name])
    return out
