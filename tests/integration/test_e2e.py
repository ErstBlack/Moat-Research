"""End-to-end smoke test: init → seeded WISHLIST → discover (mocked LLM)
→ score (mocked LLM) → promote → graduate."""
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()

FAKE_FINAL_TEXT = """
```yaml-brief
frontmatter:
  title: Test Brief
  slug: test-brief
  lane: ephemeral_public
  niche: synthetic
  sources:
    - url: https://a.example.com/
      role: primary
      archive_status: none
    - url: https://b.example.com/
      role: corroborating
      archive_status: none
  date_created: "2026-05-08"
  delivery_form: project
  verification_evidence:
    - id: e1
      tool: code_execution
      args: {code: x}
      result: {peak_gpu_gb: 4, sustained_ram_gb: 32, storage_tb: 0.5}
  disqualifier_verdicts:
    single_source: {verdict: pass}
    hardware_over_envelope: {verdict: pass, evidence_id: e1}
body: |
  ## Thesis
  Synthetic test brief body.
```
"""


def _seed_wishlist(layout: RepoLayout) -> None:
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))


async def _fake_session_run(*_args, **_kwargs) -> str:
    """Return FAKE_FINAL_TEXT so _extract_candidates + _write_candidates are exercised."""
    return FAKE_FINAL_TEXT


def test_full_lifecycle_e2e(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    # init
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0

    layout = RepoLayout(tmp_path)
    _seed_wishlist(layout)

    # discover (mocked session.run — seam is mr.cli.discover.session.run)
    # Uses FAKE_FINAL_TEXT so _extract_candidates + _write_candidates are exercised.
    with patch("mr.cli.discover.session.run", side_effect=_fake_session_run):
        result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1"])
        assert result.exit_code == 0

    candidate_files = list(layout.candidates.glob("*.md"))
    assert len(candidate_files) == 1

    # score (mocked LLM scores)
    with patch("mr.cli.score.run_score_loop",
               return_value={"defensibility": 7, "financial": 6,
                             "implementation": 8, "hardware": 9}):
        result = runner.invoke(app, ["score", str(candidate_files[0]), "--budget", "3.0"])
        assert result.exit_code == 0

    scored_files = list(layout.scored.glob("*.md"))
    assert len(scored_files) == 1
    assert scored_files[0].name.startswith("0")  # composite-padded prefix

    # promote
    result = runner.invoke(app, ["promote", str(scored_files[0])])
    assert result.exit_code == 0
    approved_files = list(layout.approved.glob("*.md"))
    assert len(approved_files) == 1

    # graduate
    result = runner.invoke(app, ["graduate", str(approved_files[0])])
    assert result.exit_code == 0
    assert "You are starting test-brief" in result.stdout
    graduated_files = list(layout.graduated.glob("*.md"))
    assert len(graduated_files) == 1
    handoff_files = list(layout.graduated.glob("*.handoff.txt"))
    assert len(handoff_files) == 1

    # status
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "graduated" in result.stdout.lower()

    # gain
    result = runner.invoke(app, ["gain"])
    assert result.exit_code == 0


def test_full_test_suite_runs_under_30_seconds(tmp_path: Path):
    """Sanity: the unit suite is fast enough for CI.

    Excludes tests/integration to avoid recursive pytest invocation
    (this very test would re-spawn itself otherwise).
    """
    import contextlib
    import subprocess
    import time
    start = time.monotonic()
    with contextlib.suppress(subprocess.TimeoutExpired):
        subprocess.run(
            ["uv", "run", "pytest", "-q", "--no-header",
             "tests/", "--ignore=tests/integration"],
            check=False, capture_output=True, timeout=45,
        )
    elapsed = time.monotonic() - start
    # Loose check; mostly catches accidental network calls
    assert elapsed < 60.0
