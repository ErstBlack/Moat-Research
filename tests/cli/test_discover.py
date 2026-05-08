from pathlib import Path
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from mr.cli.discover import _extract_candidates
from mr.cli.main import app
from mr.lifecycle.paths import RepoLayout

runner = CliRunner()


def _seed_wishlist(layout: RepoLayout) -> None:
    layout.wishlist_path.write_text("sources:\n" + "\n".join(
        f"  - id: s-{i}\n    url: https://e{i}.com/\n    lane: niche_vertical\n"
        f"    rationale: x\n    last_verified: '2026-05-07'\n    dead_link: false"
        for i in range(5)
    ))


def test_discover_aborts_on_empty_wishlist(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "1"])
    assert result.exit_code != 0
    assert "WISHLIST" in result.stdout or "WISHLIST" in result.stderr


@patch("mr.cli.discover.session.run", new_callable=AsyncMock)
def test_discover_dispatches_to_session_run(mock_run, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    runner.invoke(app, ["init", str(tmp_path)])
    layout = RepoLayout(tmp_path)
    _seed_wishlist(layout)

    mock_run.return_value = ""  # no candidates emitted — that's fine for dispatch check

    result = runner.invoke(app, ["discover", "--lane", "ephemeral_public", "--n", "3"])
    assert result.exit_code == 0
    mock_run.assert_awaited_once()
    call_kwargs = mock_run.call_args.kwargs
    assert "system_prompt" in call_kwargs
    assert "user_prompt" in call_kwargs
    assert "max_turns" in call_kwargs
    assert "wallclock_seconds" in call_kwargs


def test_extract_candidates_parses_yaml_brief_blocks():
    text = """
some preamble
```yaml-brief
frontmatter:
  title: Foo
  slug: foo
  lane: a
  niche: b
  sources: [{host: example.com}]
body: |
  Foo body.
```
trailing
"""
    out = _extract_candidates(text)
    assert len(out) == 1
    assert out[0]["frontmatter"]["title"] == "Foo"


def test_extract_candidates_skips_malformed_yaml():
    text = "```yaml-brief\nnot: [valid: yaml\n```"
    assert _extract_candidates(text) == []
