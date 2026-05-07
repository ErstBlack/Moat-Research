"""mr discover — generate candidate briefs from WISHLIST + live web tools."""
from __future__ import annotations

import json
from datetime import UTC, date, datetime
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
from mr.synth.budget import BudgetTracker, cold_corpus_preflight, worst_case_ceiling
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.tools.firecrawl import is_firecrawl_available
from mr.util.config import Config, load_config
from mr.util.costs import CostRecord, append_cost
from mr.util.lock import exclusive_lock
from mr.util.slug import slugify

_INPUT_TOKENS_ESTIMATE = 12000


def discover(root: Path, lane: str | None, n: int, budget: float) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    cold_corpus_preflight(layout.wishlist_path)

    cli = SynthClient(cfg=cfg, command="discover")
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

    lane_clause = (
        f"Generate exactly {n} candidates in lane `{lane}`."
        if lane else
        f"Generate exactly {n} candidates, distributing across underrepresented (lane, niche_key) cells."
    )
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


def _run_loop(  # noqa: PLR0913
    *, client: SynthClient, tracker: BudgetTracker, layout: RepoLayout,
    system_blocks: list[dict[str, Any]], user_text: str,
    tools: list[dict[str, Any]], cfg: Config,
) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    max_tokens = cfg.budgets["max_tokens_per_turn"]

    while True:
        tracker.note_tool_turn()
        tracker.check_wallclock()
        tracker.check_pre_call(input_tokens_estimate=_INPUT_TOKENS_ESTIMATE, max_output_tokens=max_tokens)

        response = client.create_message(
            system_blocks=system_blocks, messages=messages, tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(UTC), command="discover", model=client.model,
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
