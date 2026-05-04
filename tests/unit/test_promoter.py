import shutil
from pathlib import Path
import pytest
from workers.promoter import promoter
from workers.common import brief as brief_lib

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    """Build a temp repo with briefs/{scored,rejected,_quarantine} dirs."""
    for sub in ("scored", "rejected", "_quarantine"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


def _place(repo, fixture_name, target_subdir, target_filename):
    src = FIXTURES / fixture_name
    dst = repo / "briefs" / target_subdir / target_filename
    shutil.copy(src, dst)
    return dst


class TestPromoter:
    def test_valid_brief_stays_in_scored(self, repo):
        _place(repo, "brief_valid_scored.md", "scored", "08.031-20260504-fcc.md")
        moved = promoter.sweep(repo)
        assert moved == []
        assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
        assert list((repo / "briefs" / "rejected").iterdir()) == []

    def test_zero_financial_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_financial.md", "scored", "00.000-20260504-bad.md")
        moved = promoter.sweep(repo)
        assert len(moved) == 1
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert len(rejected) == 1
        assert rejected[0].name == "00.000-financial-20260504-bad.md"
        assert not (repo / "briefs" / "scored" / "00.000-20260504-bad.md").exists()
        raw = rejected[0].read_text()
        assert "rejection_reason" in raw
        assert "financial" in raw

    def test_zero_implementation_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_implementation.md", "scored", "00.000-20260504-bad.md")
        promoter.sweep(repo)
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert rejected[0].name == "00.000-implementation-20260504-bad.md"

    def test_zero_hardware_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_hardware.md", "scored", "00.000-20260504-bad.md")
        promoter.sweep(repo)
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert rejected[0].name == "00.000-hardware-20260504-bad.md"

    def test_malformed_brief_quarantined(self, repo):
        bad = repo / "briefs" / "scored" / "08.000-20260504-malformed.md"
        bad.write_text("no frontmatter here, just text")
        promoter.sweep(repo)
        assert not bad.exists()
        quarantined = list((repo / "briefs" / "_quarantine").iterdir())
        assert len(quarantined) == 1
        assert quarantined[0].name == "08.000-20260504-malformed.md"

    def test_idempotent(self, repo):
        _place(repo, "brief_valid_scored.md", "scored", "08.031-20260504-fcc.md")
        promoter.sweep(repo)
        promoter.sweep(repo)
        assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
