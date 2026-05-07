"""mr promote — move a scored brief to approved/."""
from __future__ import annotations

from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.lifecycle.transitions import TransitionError, move_brief


def promote(src_path: Path, root: Path) -> None:
    layout = RepoLayout(root)
    if not src_path.exists():
        typer.echo(f"error: {src_path} not found", err=True)
        raise typer.Exit(code=2)
    if src_path.parent.resolve() != layout.scored.resolve():
        typer.echo(f"error: {src_path} is not in scored/", err=True)
        raise typer.Exit(code=2)
    dst = layout.approved / src_path.name
    try:
        move_brief(src_path, dst)
    except TransitionError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2) from e
    typer.echo(f"promoted: {dst}")
