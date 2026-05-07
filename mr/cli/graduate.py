"""mr graduate — emit hand-off prompt and move approved → graduated."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.handoff.adjacent_rejections import build_appendix
from mr.handoff.feature import build_feature_handoff
from mr.handoff.project import build_project_handoff
from mr.lifecycle.frontmatter import read_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief
from mr.util.config import load_config


def graduate(src_path: Path, root: Path) -> None:
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    in_approved = src_path.parent.resolve() == layout.approved.resolve()
    in_graduated = src_path.parent.resolve() == layout.graduated.resolve()

    if not in_approved and not in_graduated:
        typer.echo(f"error: {src_path} is not in approved/ or graduated/", err=True)
        raise typer.Exit(code=2)

    brief = read_brief(src_path)
    appendix = build_appendix(
        read_seen(layout.seen_path),
        target_lane=brief.lane,
        target_niche_key=brief.niche_key,
    )

    if brief.delivery_form == "feature":
        prompt = build_feature_handoff(brief, cfg=cfg, adjacent_appendix=appendix)
    else:
        prompt = build_project_handoff(brief, cfg=cfg, adjacent_appendix=appendix)

    if in_graduated:
        typer.echo(prompt)
        return

    dst = layout.graduated / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2) from e

    sidecar = layout.graduated / f"{brief.slug}.handoff.txt"
    sidecar.write_text(prompt)
    typer.echo(prompt)
