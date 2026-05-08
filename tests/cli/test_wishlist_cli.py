from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app

runner = CliRunner()


def test_wishlist_add_via_cli(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    yaml_text = """id: my-source
url: https://example.com/
lane: niche_vertical
rationale: testing
last_verified: 2026-05-07
dead_link: false
"""
    result = runner.invoke(app, ["wishlist", "add", "--yaml", yaml_text])
    assert result.exit_code == 0


@patch("mr.cli.wishlist.refresh_wishlist")
def test_wishlist_refresh_via_cli(mock_refresh, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["wishlist", "refresh"])
    assert result.exit_code == 0
    mock_refresh.assert_called_once()


@patch("mr.cli.wishlist.expand_wishlist")
def test_wishlist_expand_via_cli(mock_expand, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    mock_expand.return_value = "(no proposals)"
    result = runner.invoke(app, ["wishlist", "expand", "--seed"])
    assert result.exit_code == 0
    mock_expand.assert_called_once()
