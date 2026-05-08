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
    assert "schema_version: 2" in text
    assert "limits:" in text
    assert "budgets:" not in text


def test_init_creates_default_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "WISHLIST.md").exists()
    assert "sources: []" in (tmp_path / "WISHLIST.md").read_text()


def test_init_aborts_when_config_exists_without_migrate(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("schema_version: 1\n")
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_init_migrate_overwrites_existing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("schema_version: 1\n")
    result = runner.invoke(app, ["init", "--migrate"])
    assert result.exit_code == 0
    assert (tmp_path / "mr.yaml.bak").exists()
    new_content = cfg_path.read_text()
    assert "schema_version: 2" in new_content
    assert "limits:" in new_content
    assert "budgets:" not in new_content


def test_init_migrate_backs_up_old_content(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg_path = tmp_path / "mr.yaml"
    cfg_path.write_text("schema_version: 1\ncustom_key: old_value\n")
    runner.invoke(app, ["init", "--migrate"])
    bak_content = (tmp_path / "mr.yaml.bak").read_text()
    assert "old_value" in bak_content
