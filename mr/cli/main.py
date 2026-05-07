"""Entry point for the `mr` CLI."""
import typer

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
