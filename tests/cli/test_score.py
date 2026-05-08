from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.frontmatter import Brief, write_brief
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _candidate_with_verdicts(layout: RepoLayout, slug: str, hw_result: dict) -> Path:
    target = layout.candidates / f"20260507-{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    brief = Brief(
        schema_version=1, title=slug, slug=slug, lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {"id": "e3", "tool": "code_execution", "args": {"code": "x"}, "result": hw_result},
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    write_brief(target, brief, body="## Thesis\nFoo bar.\n")
    return target


def test_score_routes_to_rejected_when_hw_keys_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    # hw_result missing required keys → verify step rejects before LLM is called
    src = _candidate_with_verdicts(layout, "foo", hw_result={"peak_gpu_gb": 4})

    result = runner.invoke(app, ["score", str(src)])
    assert result.exit_code == 0
    assert any(layout.rejected.glob("00000-*-foo*.md"))


@patch("mr.cli.score.session.run", new_callable=AsyncMock)
def test_score_routes_to_scored_when_predicates_pass(mock_run, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = _candidate_with_verdicts(layout, "foo",
                                   hw_result={"peak_gpu_gb": 4, "sustained_ram_gb": 32, "storage_tb": 0.5})
    mock_run.return_value = '{"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 5}'

    result = runner.invoke(app, ["score", str(src)])
    assert result.exit_code == 0
    moved = list(layout.scored.glob("*-20260507-foo*.md"))
    assert len(moved) == 1


@patch("mr.cli.score.session.run", new_callable=AsyncMock)
def test_score_floor_rejection_low_defensibility(mock_run, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    src = _candidate_with_verdicts(layout, "foo",
                                   hw_result={"peak_gpu_gb": 4, "sustained_ram_gb": 32, "storage_tb": 0.5})
    mock_run.return_value = '{"defensibility": 2, "financial": 8, "implementation": 8, "hardware": 8}'

    result = runner.invoke(app, ["score", str(src)])
    assert result.exit_code == 0
    assert any(layout.rejected.glob("00000-*-foo*.md"))
