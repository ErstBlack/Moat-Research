import shutil
from pathlib import Path
import pytest
from workers.init_prompt_gen import init_prompt_gen

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "briefs" / "approved").mkdir(parents=True)
    return tmp_path


class TestInitPromptGen:
    def test_renders_for_approved_brief(self, repo):
        src = FIXTURES / "brief_approved.md"
        dst = repo / "briefs" / "approved" / "08.031-20260504-fcc.md"
        shutil.copy(src, dst)
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        assert artifact.exists()
        text = artifact.read_text()
        assert "FCC EAS alert metadata archive" in text
        assert "Composite score: 8.031" in text
        assert "Lane: 1" in text

    def test_idempotent(self, repo):
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        first = artifact.read_text()
        init_prompt_gen.sweep(repo)
        second = artifact.read_text()
        assert first == second

    def test_skips_non_approved_status(self, repo):
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        assert not artifact.exists()

    def test_ignores_existing_init_prompt_files(self, repo):
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        init_prompt_gen.sweep(repo)
        init_prompt_gen.sweep(repo)
