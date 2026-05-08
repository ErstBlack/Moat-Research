"""mr wishlist {add, expand, refresh} subcommand group."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.synth.limits import LimitExceeded
from mr.util.config import load_config
from mr.util.lock import exclusive_lock
from mr.wishlist.add import add_source
from mr.wishlist.expand import expand_wishlist
from mr.wishlist.refresh import refresh_wishlist

wishlist_app = typer.Typer(no_args_is_help=True, help="Wishlist management subcommands.")


@wishlist_app.command("add")
def add_cmd(
    yaml: str = typer.Option(..., "--yaml", help="YAML fragment for the new source"),  # noqa: B008
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """Append a validated source to WISHLIST.md."""
    layout = RepoLayout(root or Path.cwd())
    add_source(layout.wishlist_path, yaml)
    typer.echo("source added")


@wishlist_app.command("refresh")
def refresh_cmd(
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """Re-verify all WISHLIST sources (HEAD + robots + Wayback)."""
    layout = RepoLayout(root or Path.cwd())
    cfg = load_config(layout.config_path)
    window = cfg.status.get("dead_link_window_days", 14)
    refresh_wishlist(layout.wishlist_path, today=date.today(), dead_link_window_days=window)
    typer.echo("refreshed")


@wishlist_app.command("expand")
def expand_cmd(
    seed: bool = typer.Option(False, "--seed", help="Bootstrap from empty WISHLIST"),  # noqa: B008
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """LLM proposes new WISHLIST sources for operator review."""
    layout = RepoLayout(root or Path.cwd())
    cfg = load_config(layout.config_path)
    try:
        with exclusive_lock(layout.lock_path):
            output = expand_wishlist(layout, cfg, seed=seed)
    except LimitExceeded as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2) from e
    except RuntimeError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=1) from e
    typer.echo(output)
