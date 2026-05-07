"""mr init — bootstrap repo layout, mr.yaml, prompts/, WISHLIST.md."""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

from mr.lifecycle.paths import RepoLayout
from mr.util.config import DEFAULT_CONFIG


def init(root: Path) -> None:
    """Create lifecycle dirs, .moat-research/, prompts/, and seed defaults."""
    layout = RepoLayout(root)
    layout.ensure_dirs()

    if not layout.config_path.exists():
        layout.config_path.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))
        typer.echo(f"created {layout.config_path}")

    if not layout.wishlist_path.exists():
        layout.wishlist_path.write_text("sources: []\n")
        typer.echo(f"created {layout.wishlist_path}")

    for name in ("discover", "score", "wishlist_expand"):
        target = layout.prompts_dir / f"{name}.md"
        if not target.exists():
            target.write_text(f"# {name} prompt\n\n(replace with the shipped {name}.md)\n")
            typer.echo(f"created {target}")

    typer.echo("mr init: done")
