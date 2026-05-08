"""mr wishlist expand — LLM-driven source proposal.

Spec §11: emits candidate entries to stdout for operator review;
operator runs `mr wishlist add` on the ones they like. With --seed,
bootstraps from an empty list.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import yaml

from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.dedup.summary import build_summary_block
from mr.lifecycle.paths import RepoLayout
from mr.synth.budget import BudgetTracker
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.util.config import Config
from mr.util.costs import CostRecord, append_cost


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

    tools = tools_for_command("wishlist_expand")

    user_msg = (
        "Propose 3-7 new WISHLIST sources following the diversity bias. "
        "For each, output a YAML block with id/url/lane/rationale. "
        "Use seen_lookup to verify novelty before final commit."
    )

    proposals = _run_loop(client, tracker, layout, system_blocks, user_msg, tools, cfg)
    return format_proposal(proposals)


def _run_loop(  # noqa: PLR0913
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
        tracker.check_pre_call(input_tokens_estimate=10000, max_output_tokens=max_tokens)  # noqa: PLR2004

        response = client.create_message(
            system_blocks=system_blocks,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)

        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(UTC), command="wishlist_expand",
            model=client.model, input_tokens=usage["input_tokens"],
            cached_input_tokens=0, output_tokens=usage["output_tokens"],
            cache_hits=usage["cache_hits"], cache_misses=usage["cache_misses"],
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))

        tracker.note_turn_cache_status(missed=usage["cache_misses"] > 0, fingerprint="wishlist_expand_system")

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
