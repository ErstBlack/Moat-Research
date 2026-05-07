"""mr status — counts per dir, stale-approved warning, top-mined hosts."""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import typer

from mr.dedup.seen import is_stale, read_seen, regenerate_seen
from mr.lifecycle.paths import DISPOSITIONS, LIFECYCLE_DIRS, RepoLayout
from mr.util.config import load_config

_STALE_APPROVED_DAYS_FALLBACK = 90
_TOP_HOSTS = 3


def status(root: Path) -> None:
    """Print lifecycle counts, stale-approved warnings, exploration flags."""
    layout = RepoLayout(root)
    cfg = load_config(layout.config_path)

    if is_stale(layout):
        regenerate_seen(layout, niche_aliases=cfg.niche_aliases)

    entries = read_seen(layout.seen_path)

    counts = Counter(e.disposition for e in entries)
    typer.echo("## Lifecycle counts")
    for dirname, disposition in zip(LIFECYCLE_DIRS, DISPOSITIONS, strict=True):
        typer.echo(f"  {dirname}: {counts.get(disposition, 0)}")

    stale_days = cfg.status.get("stale_approved_days", _STALE_APPROVED_DAYS_FALLBACK)
    today = date.today()
    stale_threshold = today - timedelta(days=stale_days)
    stale_briefs = [
        e for e in entries
        if e.disposition == "approved"
        and date.fromisoformat(e.date_created) < stale_threshold
    ]
    if stale_briefs:
        typer.echo(f"\n## Stale approved (older than {stale_days} days)")
        for e in stale_briefs:
            typer.echo(f"  {e.slug} (created {e.date_created})")

    other_briefs = [e for e in entries if e.lane == "other"]
    if other_briefs:
        typer.echo(f"\n## Exploration (lane: other) — {len(other_briefs)} briefs")
        for e in other_briefs[:_TOP_HOSTS]:
            typer.echo(f"  {e.slug} ({e.disposition})")

    host_counts: Counter[str] = Counter()
    for e in entries:
        for h in e.source_set:
            host_counts[h] += 1
    if host_counts:
        typer.echo("\n## Top-3 most-mined hosts")
        for host, c in host_counts.most_common(_TOP_HOSTS):
            typer.echo(f"  {host}: {c}")
