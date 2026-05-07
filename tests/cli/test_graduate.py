from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _setup_approved(tmp_path: Path, *, delivery_form: str = "project",
                    parent: str | None = None) -> tuple[RepoLayout, Path]:
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = layout.approved / "07500-20260507-foo.md"
    src.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title="foo", slug="foo", lane="ephemeral_public",
        niche="aviation alerts", niche_key="alerts_aviation",
        delivery_form=delivery_form, parent_project=parent,
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.5},
    )
    write_brief(src, brief, body="## Thesis\nFoo bar baz.\n")
    return layout, src


def test_graduate_project_emits_init_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path)
    result = runner.invoke(app, ["graduate", str(src)])
    assert result.exit_code == 0
    assert "You are starting foo" in result.stdout
    assert "Xeon E5-2698 v4" in result.stdout
    moved = layout.graduated / src.name
    assert moved.exists()
    assert (layout.graduated / "foo.handoff.txt").exists()


def test_graduate_feature_emits_patch_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path, delivery_form="feature", parent="somd-cameras")
    result = runner.invoke(app, ["graduate", str(src)])
    assert result.exit_code == 0
    assert "extending the `somd-cameras` repo" in result.stdout


def test_graduate_idempotent_on_already_graduated(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    layout, src = _setup_approved(tmp_path)
    runner.invoke(app, ["graduate", str(src)])
    moved = layout.graduated / src.name
    result = runner.invoke(app, ["graduate", str(moved)])
    assert result.exit_code == 0
    assert "You are starting foo" in result.stdout
