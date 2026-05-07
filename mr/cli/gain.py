"""mr gain — summarize spend from costs.jsonl."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import typer

from mr.lifecycle.paths import RepoLayout
from mr.util.costs import read_cost_history


def gain(root: Path) -> None:
    layout = RepoLayout(root)
    records = read_cost_history(layout.costs_path)
    if not records:
        typer.echo("no recorded API calls — total $0.00")
        return

    per_command: dict[str, float] = defaultdict(float)
    per_model: dict[str, float] = defaultdict(float)
    total = 0.0
    for r in records:
        per_command[r.command] += r.cost_usd
        per_model[r.model] += r.cost_usd
        total += r.cost_usd

    typer.echo(f"## Total spend: ${total:.4f}")
    typer.echo(f"## Calls: {len(records)}")

    typer.echo("\n## By command")
    for cmd, c in sorted(per_command.items(), key=lambda x: -x[1]):
        typer.echo(f"  {cmd}: ${c:.4f}")

    typer.echo("\n## By model")
    for m, c in sorted(per_model.items(), key=lambda x: -x[1]):
        typer.echo(f"  {m}: ${c:.4f}")
