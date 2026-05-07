"""Entry point for the `mr` CLI."""
from pathlib import Path

import typer

from mr.cli import graduate as graduate_module
from mr.cli import init as init_module
from mr.cli import promote as promote_module
from mr.cli import reject as reject_module
from mr.cli import status as status_module

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


@app.command(name="status")
def status_cmd(
    root: Path = typer.Argument(None, help="Repo root"),  # noqa: B008
) -> None:
    """Show lifecycle counts and operator-relevant warnings."""
    status_module.status(root or Path.cwd())


@app.command(name="promote")
def promote_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),  # noqa: B008
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """Move a scored brief to approved/."""
    promote_module.promote(path, root or Path.cwd())


@app.command(name="reject")
def reject_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),  # noqa: B008
    reason: str = typer.Option(None, "--reason", help="Operator's rejection reason"),  # noqa: B008
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """Move a scored brief to rejected/ with optional reason."""
    reject_module.reject(path, root or Path.cwd(), reason)


@app.command(name="graduate")
def graduate_cmd(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),  # noqa: B008
    root: Path = typer.Option(None, "--root"),  # noqa: B008
) -> None:
    """Emit hand-off prompt and move approved → graduated. Idempotent."""
    graduate_module.graduate(path, root or Path.cwd())
