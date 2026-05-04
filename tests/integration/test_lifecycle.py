import json
import shutil
from pathlib import Path
import pytest
from workers.promoter import promoter
from workers.indexer import indexer
from workers.init_prompt_gen import init_prompt_gen

FIXTURES = Path(__file__).parent.parent / "fixtures"

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(tmp_path):
    for sub in ("candidates", "scored", "rejected", "approved", "graduated"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


def test_scored_to_rejected_path(repo):
    """Brief with axis=0 lands in scored/, promoter moves it to rejected/, indexer reflects."""
    shutil.copy(FIXTURES / "brief_zero_financial.md", repo / "briefs" / "scored" / "00.000-20260504-bad.md")
    promoter.sweep(repo)
    indexer.rebuild(repo)

    rejected = list((repo / "briefs" / "rejected").iterdir())
    assert len(rejected) == 1
    assert rejected[0].name == "00.000-financial-20260504-bad.md"

    idx = json.loads((repo / "briefs" / "index.json").read_text())
    assert len(idx["briefs"]) == 1
    assert idx["briefs"][0]["lifecycle_dir"] == "rejected"


def test_scored_to_approved_to_init_prompt_path(repo):
    """Brief in scored/ stays put on first promoter pass; operator moves to approved/; init-prompt is rendered."""
    src = repo / "briefs" / "scored" / "08.031-20260504-fcc.md"
    shutil.copy(FIXTURES / "brief_valid_scored.md", src)

    promoter.sweep(repo)
    assert src.exists()

    text = src.read_text().replace("status: scored", "status: approved")
    src.write_text(text)
    dst = repo / "briefs" / "approved" / "08.031-20260504-fcc.md"
    src.rename(dst)

    init_prompt_gen.sweep(repo)
    artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
    assert artifact.exists()
    text = artifact.read_text()
    assert "Operational envelope" in text
    assert "FCC EAS alert metadata archive" in text

    indexer.rebuild(repo)
    idx = json.loads((repo / "briefs" / "index.json").read_text())
    brief_entries = [b for b in idx["briefs"] if b["id"] == "brief_2026_05_04_fcc_eas_alerts"]
    assert len(brief_entries) == 1
    assert brief_entries[0]["lifecycle_dir"] == "approved"


def test_promoter_indexer_init_prompt_gen_idempotent(repo):
    shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
    shutil.copy(FIXTURES / "brief_zero_hardware.md", repo / "briefs" / "scored" / "00.000-20260504-bad.md")
    shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-app.md")

    for _ in range(3):
        promoter.sweep(repo)
        indexer.rebuild(repo)
        init_prompt_gen.sweep(repo)

    assert (repo / "briefs" / "rejected" / "00.000-hardware-20260504-bad.md").exists()
    assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
    assert (repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md").exists()
