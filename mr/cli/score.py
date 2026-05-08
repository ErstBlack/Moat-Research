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

    server = mcp_server.build_server(seen_path=layout.seen_path, command="score")
    allowed = mcp_server.allowed_tools_for("score")
    limits = run_limits_from_config(cfg.limits, command="score")

    final_text = await session.run(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=cfg.models.get("per_command", {}).get("score", cfg.models["default"]),
        mcp_server=server,
        allowed_tools=allowed,
        max_turns=limits.max_tool_turns,
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
