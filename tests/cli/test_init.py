from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app

runner = CliRunner()


def test_init_creates_dirs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    for d in ("candidates", "scored", "rejected", "approved", "graduated"):
        assert (tmp_path / d).is_dir()
    assert (tmp_path / ".moat-research").is_dir()
    assert (tmp_path / "prompts").is_dir()


def test_init_creates_default_mr_yaml(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "mr.yaml").exists()
    text = (tmp_path / "mr.yaml").read_text()
    assert "schema_version: 1" in text


def test_init_creates_default_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "WISHLIST.md").exists()
    assert "sources: []" in (tmp_path / "WISHLIST.md").read_text()


def test_init_idempotent(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    (tmp_path / "mr.yaml").write_text("schema_version: 1\nweights:\n  defensibility: 0.50\n")
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "0.50" in (tmp_path / "mr.yaml").read_text()
