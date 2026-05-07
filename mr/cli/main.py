"""Entry point for the `mr` CLI."""
import typer

app = typer.Typer(
    name="mr",
    help="Discover, score, and graduate data-moat opportunities.",
    no_args_is_help=True,
)


@app.callback()
def _callback() -> None:
    """moat-research: discover, score, and graduate data-moat opportunities."""


@app.command()
def version() -> None:
    """Print the installed mr version."""
    from mr import __version__
    typer.echo(f"mr {__version__}")
