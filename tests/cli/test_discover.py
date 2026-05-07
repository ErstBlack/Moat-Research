from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def test_discover_aborts_on_empty_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1", "--budget", "1.0"])
    assert result.exit_code != 0
    assert "WISHLIST" in result.stdout or "WISHLIST" in result.stderr


def test_discover_aborts_when_anthropic_api_key_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1", "--budget", "1.0"])
    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.stdout or "ANTHROPIC_API_KEY" in result.stderr


@patch("mr.cli.discover.run_discover_loop")
def test_discover_dispatches_to_loop(mock_loop, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "3", "--budget", "5.0"])
    assert result.exit_code == 0
    mock_loop.assert_called_once()
