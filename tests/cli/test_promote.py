from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup(tmp_path: Path) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.scored / "07221-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 7, "hardware": 8, "composite": 7.221},
    )
    write_brief(src, brief, body="## Thesis\nFoo.\n")
    return layout, src


def test_promote_moves_to_approved(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["promote", str(src)])
    assert result.exit_code == 0
    assert not src.exists()
    assert (layout.approved / "07221-20260507-foo.md").exists()


def test_promote_nonexistent_fails(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["promote", str(tmp_path / "scored" / "absent.md")])
    assert result.exit_code != 0
