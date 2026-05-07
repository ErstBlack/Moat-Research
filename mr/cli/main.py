"""Entry point for the `mr` CLI."""
from pathlib import Path

import typer

from mr.cli import init as init_module

app = typer.Typer(
    name="mr",
    help="Discover, score, and graduate data-moat opportunities.",
    no_args_is_help=True,
)


# Force multi-command mode: typer >= 0.12 collapses single-command apps,
# which would route `mr version` to the root and reject the subcommand.
@app.callback()
def _callback() -> None: ...


@app.command()
def version() -> None:
    """Print the installed mr version."""
    from mr import __version__
    typer.echo(f"mr {__version__}")


@app.command(name="init")
def init_cmd(
    root: Path = typer.Argument(None, help="Repo root (default: cwd)"),  # noqa: B008
) -> None:
    """Bootstrap dirs, mr.yaml, prompts/, WISHLIST.md (idempotent)."""
    init_module.init(root or Path.cwd())
