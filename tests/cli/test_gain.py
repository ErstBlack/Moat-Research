from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout
from mr.util.costs import CostRecord, append_cost

runner = CliRunner()


def test_gain_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0
    assert "$0.00" in result.stdout or "0.00" in result.stdout


def test_gain_summarizes_costs(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    for cost in [0.10, 0.20, 0.05]:
        append_cost(layout.costs_path, CostRecord(
            ts=datetime.now(UTC), command="discover",
            model="claude-opus-4-7",
            input_tokens=100, cached_input_tokens=0, output_tokens=50,
            cache_hits=0, cache_misses=0,
            code_execution_container_seconds=0.0, cost_usd=cost,
        ))
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0
    assert "0.35" in result.stdout
    assert "discover" in result.stdout
