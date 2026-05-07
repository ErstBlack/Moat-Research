from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, read_brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup(tmp_path: Path) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.scored / "06000-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 6, "financial": 6, "implementation": 6, "hardware": 6, "composite": 6.0},
    )
    write_brief(src, brief, body="## Thesis\nFoo.\n")
    return layout, src


def test_reject_writes_manual_reason(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["reject", str(src), "--reason", "not the right time"])
    assert result.exit_code == 0
    moved = layout.rejected / "06000-20260507-foo.md"
    assert moved.exists()
    b = read_brief(moved)
    assert b.scores["auto_reject_reason"] == "manual: not the right time"


def test_reject_without_reason_uses_blank(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup(tmp_path)
    result = runner.invoke(app, ["reject", str(src)])
    assert result.exit_code == 0
    moved = layout.rejected / "06000-20260507-foo.md"
    b = read_brief(moved)
    assert b.scores["auto_reject_reason"].startswith("manual:")
