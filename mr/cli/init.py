"""mr init — bootstrap repo layout, mr.yaml, prompts/, WISHLIST.md."""
from __future__ import annotations

from pathlib import Path

import typer
import yaml

from mr.lifecycle.paths import RepoLayout

_DEFAULT_CONFIG_V2: dict = {
    "schema_version": 2,
    "models": {
        "default": "claude-opus-4-7",
        "bulk": "claude-sonnet-4-6",
        "per_command": {"wishlist_expand": "claude-sonnet-4-6"},
        "pricing": {
            "claude-opus-4-7": {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_write": 18.75},
            "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
            "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cache_read": 0.10, "cache_write": 1.25},
        },
    },
    "weights": {
        "defensibility": 0.35,
        "financial": 0.30,
        "implementation": 0.20,
        "hardware": 0.15,
    },
    "disqualifiers": {
        "defensibility_min": 5,
        "any_axis_zero": True,
        "unrestricted_archive_min_snapshots": 100,
        "unrestricted_archive_min_years": 3,
    },
    "lanes": [
        "ephemeral_public",
        "soon_to_be_restricted",
        "cross_source_fusion",
        "derived_artifact",
        "niche_vertical",
        "other",
    ],
    "niche_aliases": {},
    "interests": {"affirm": [], "avoid": []},
    "hardware": {
        "cpu": "2× Intel Xeon E5-2698 v4 (40c/80t)",
        "ram_gb": 250,
        "gpu": "NVIDIA P4 (8GB), shared",
        "storage_tb": 17,
        "network": "residential broadband",
    },
    "limits": {
        "max_tool_turns": {
            "default": 12,
            "discover": 20,
            "score": 8,
            "wishlist_expand": 10,
        },
        "max_wallclock_seconds": 600,
    },
    "status": {
        "stale_approved_days": 90,
        "dead_link_window_days": 14,
    },
}


def _write_default_config(config_path: Path) -> None:
    config_path.write_text(yaml.safe_dump(_DEFAULT_CONFIG_V2, sort_keys=False))


def init(root: Path, migrate: bool = False) -> None:
    """Create lifecycle dirs, .moat-research/, prompts/, and seed defaults."""
    layout = RepoLayout(root)
    layout.ensure_dirs()

    if layout.config_path.exists():
        if not migrate:
            typer.echo(f"{layout.config_path} already exists; pass --migrate to overwrite.")
            raise typer.Exit(code=1)
        backup = layout.config_path.with_suffix(".yaml.bak")
        layout.config_path.rename(backup)
        typer.echo(f"backed up existing config to {backup}")
        _write_default_config(layout.config_path)
        typer.echo(f"created {layout.config_path}")
    else:
        _write_default_config(layout.config_path)
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
