from datetime import date, timedelta
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _scaffold(tmp_path: Path) -> RepoLayout:
    runner.invoke(app, ["init", str(tmp_path)])
    return RepoLayout(tmp_path)


def _write_brief(layout: RepoLayout, dirname: str, slug: str, *, lane="ephemeral_public",
                 days_old: int = 0) -> Path:
    target = layout.root / dirname / f"20260507-{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title=slug, slug=slug, lane=lane,
        niche="x", niche_key="x", delivery_form="project",
        date_created=date.today() - timedelta(days=days_old),
        sources=[{"url": f"https://{slug}.com/", "role": "primary", "archive_status": "none"}],
    )
    write_brief(target, brief, body=f"## Thesis\n{slug}.\n")
    return target


def test_status_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _scaffold(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "candidates: 0" in result.stdout
    assert "scored: 0" in result.stdout


def test_status_counts(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    _write_brief(layout, "candidates", "a")
    _write_brief(layout, "candidates", "b")
    _write_brief(layout, "scored", "c")
    result = runner.invoke(app, ["status"])
    assert "candidates: 2" in result.stdout
    assert "scored: 1" in result.stdout


def test_status_stale_approved_warning(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    _write_brief(layout, "approved", "old", days_old=120)
    result = runner.invoke(app, ["status"])
    assert "stale" in result.stdout.lower()
    assert "old" in result.stdout


def test_status_other_lane_flagged(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout = _scaffold(tmp_path)
    target = layout.candidates / "20260507-explore.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="explore", slug="explore", lane="other",
        lane_note="novel moat shape",
        niche="weird", niche_key="weird", delivery_form="project",
        date_created=date.today(),
        sources=[{"url": "https://x.com/", "role": "primary", "archive_status": "none"}],
    )
    write_brief(target, brief, body="## Thesis\nx.\n")
    result = runner.invoke(app, ["status"])
    assert "other" in result.stdout.lower() or "exploration" in result.stdout.lower()
