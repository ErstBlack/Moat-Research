"""mr score — score, verify, route to scored/ or rejected/."""
from __future__ import annotations

import json
from datetime import UTC, datetime
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
from mr.synth.budget import BudgetTracker, worst_case_ceiling
from mr.synth.client import SynthClient, build_cached_blocks
from mr.synth.dispatch import dispatch_tool_call
from mr.synth.prompts import load_prompt
from mr.synth.tools import tools_for_command
from mr.synth.verify import verify_disqualifier_check
from mr.util.config import Config, load_config
from mr.util.costs import CostRecord, append_cost
from mr.util.lock import exclusive_lock

_INPUT_TOKENS_ESTIMATE = 8000


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


def _score_one(  # noqa: PLR0912
    src: Path,
    *,
    layout: RepoLayout,
    cfg: Config,
    budget: float,
    client: SynthClient,
) -> None:
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

    scores_dict = run_score_loop(brief=brief, layout=layout, cfg=cfg, budget=budget, client=client)
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


def run_score_loop(  # noqa: PLR0913
    *,
    brief: Brief,
    layout: RepoLayout,
    cfg: Config,
    budget: float,
    client: SynthClient,
) -> dict[str, int]:
    """Run the LLM scoring conversation. Returns the four axis scores."""
    system_text = load_prompt(layout.prompts_dir, "score")
    system_blocks = build_cached_blocks(system_text=system_text)

    tracker = BudgetTracker(
        cfg=cfg, command="score", model=client.model,
        budget_usd=budget, costs_path=layout.costs_path,
    )
    tools = tools_for_command("score")

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
        tracker.check_pre_call(input_tokens_estimate=_INPUT_TOKENS_ESTIMATE, max_output_tokens=max_tokens)

        response = client.create_message(
            system_blocks=system_blocks, messages=messages, tools=tools,
            max_tokens=max_tokens,
        )
        usage = client.extract_usage(response)
        cost = client.compute_cost_usd(usage)
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(UTC), command="score", model=client.model,
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
    brief: Brief,
    src: Path,
    layout: RepoLayout,
    reason: str,
    scores: Scores | None = None,
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
