"""mr wishlist expand — LLM-driven source proposal.

Spec §11: emits candidate entries to stdout for operator review;
operator runs `mr wishlist add` on the ones they like. With --seed,
bootstraps from an empty list.
"""
from __future__ import annotations

import asyncio
from typing import Any

import yaml

from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.dedup.summary import build_summary_block
from mr.lifecycle.paths import RepoLayout
from mr.synth import mcp_server, session
from mr.synth.limits import run_limits_from_config
from mr.synth.prompts import load_prompt
from mr.util.config import Config


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
) -> str:
    """Run the LLM to propose new WISHLIST sources. Returns stdout text."""
    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    proposals = asyncio.run(_async_expand(layout=layout, cfg=cfg, seed=seed))
    return format_proposal(proposals)


async def _async_expand(
    *, layout: RepoLayout, cfg: Config, seed: bool,
) -> list[dict[str, Any]]:
    summary = build_summary_block(read_seen(layout.seen_path))

    wishlist_text = layout.wishlist_path.read_text() if layout.wishlist_path.exists() else "sources: []\n"
    if seed:
        wishlist_text = "sources: []\n"

    system_text = load_prompt(layout.prompts_dir, "wishlist_expand")

    system_prompt = (
        f"{system_text}\n\n"
        f"## Current WISHLIST\n```yaml\n{wishlist_text}\n```\n\n"
        f"## Seen Summary\n{summary}\n"
    )

    user_prompt = (
        "Propose 3-7 new WISHLIST sources following the diversity bias. "
        "For each, output a YAML block with id/url/lane/rationale. "
        "Use seen_lookup to verify novelty before final commit."
    )

    server = mcp_server.build_server(seen_path=layout.seen_path, command="wishlist_expand")
    allowed = mcp_server.allowed_tools_for("wishlist_expand")
    limits = run_limits_from_config(cfg.limits, command="wishlist_expand")

    final_text = await session.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=cfg.models.get("per_command", {}).get("wishlist_expand", cfg.models["default"]),
        mcp_server=server,
        allowed_tools=allowed,
        max_turns=limits.max_tool_turns,
        wallclock_seconds=limits.max_wallclock_seconds,
    )
    return _extract_proposals(final_text)


def _extract_proposals(full: str) -> list[dict[str, Any]]:
    """Parse YAML blocks from the assistant's final text."""
    proposals: list[dict[str, Any]] = []
    for chunk in full.split("---"):
        chunk = chunk.strip()  # noqa: PLW2901
        if not chunk:
            continue
        try:
            parsed = yaml.safe_load(chunk)
        except yaml.YAMLError:
            continue
        if isinstance(parsed, dict) and "id" in parsed:
            proposals.append(parsed)
    return proposals
