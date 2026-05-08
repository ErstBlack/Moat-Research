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

    server = mcp_server.build_server(seen_path=layout.seen_path, command="discover")
    allowed = mcp_server.allowed_tools_for("discover")
    limits = run_limits_from_config(cfg.limits, command="discover")

    final_text = await session.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=cfg.models.get("per_command", {}).get("discover", cfg.models["default"]),
        mcp_server=server,
        allowed_tools=allowed,
        max_turns=limits.max_tool_turns,
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
        body_end = full.find("\n" + end_fence, body_start)
        if body_end < 0:
            break
        block_text = full[body_start:body_end].strip()
        try:
            parsed = yaml.safe_load(block_text)
        except yaml.YAMLError:
            pos = body_end + 1 + len(end_fence)
            continue
        if isinstance(parsed, dict) and "frontmatter" in parsed and "body" in parsed:
            candidates.append(parsed)
        pos = body_end + 1 + len(end_fence)
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
