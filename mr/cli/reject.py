"""mr reject — move scored brief to rejected/ with operator reason."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.lifecycle.frontmatter import read_brief, write_brief
from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def reject(src_path: Path, root: Path, reason: str | None) -> None:
    layout = RepoLayout(root)
    if src_path.parent.resolve() != layout.scored.resolve():
        typer.echo(f"error: {src_path} is not in scored/", err=True)
        raise typer.Exit(code=2)

    brief = read_brief(src_path)
    reason_text = reason.strip() if reason else "(no reason provided)"
    if brief.scores is None:
        brief.scores = {}
    brief.scores["auto_reject_reason"] = f"manual: {reason_text}"
    write_brief(src_path, brief)

    dst = layout.rejected / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2) from e
    typer.echo(f"rejected: {dst}")
