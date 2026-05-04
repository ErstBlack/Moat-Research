import json
import shutil
from pathlib import Path
import pytest
from workers.indexer import indexer

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    for sub in ("candidates", "scored", "rejected", "approved", "graduated"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


class TestIndexer:
    def test_empty_repo_writes_empty_index(self, repo):
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        assert out == {"briefs": []}

    def test_single_brief_indexed(self, repo):
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        assert len(out["briefs"]) == 1
        entry = out["briefs"][0]
        assert entry["id"] == "brief_2026_05_04_fcc_eas_alerts"
        assert entry["lifecycle_dir"] == "scored"
        assert entry["filename"] == "08.031-20260504-fcc.md"
        assert entry["composite_score"] == pytest.approx(8.031)

    def test_briefs_from_all_dirs(self, repo):
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-a.md")
        shutil.copy(FIXTURES / "brief_candidate_unscored.md", repo / "briefs" / "candidates" / "--.----20260504-b.md")
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-c.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        dirs = {b["lifecycle_dir"] for b in out["briefs"]}
        assert dirs == {"scored", "candidates", "approved"}

    def test_sorted_by_score_descending(self, repo):
        for score, slug in [(8.031, "fcc"), (5.500, "lower"), (9.200, "higher")]:
            dst = repo / "briefs" / "scored" / f"{score:06.3f}-20260504-{slug}.md"
            shutil.copy(FIXTURES / "brief_valid_scored.md", dst)
            text = dst.read_text().replace("composite_score: 8.031", f"composite_score: {score}")
            dst.write_text(text)
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        scores = [b["composite_score"] for b in out["briefs"]]
        assert scores == sorted(scores, reverse=True)

    def test_malformed_brief_skipped_not_crash(self, repo):
        (repo / "briefs" / "scored" / "08.000-bad.md").write_text("garbage")
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        assert len(out["briefs"]) == 1
        assert out["briefs"][0]["id"] == "brief_2026_05_04_fcc_eas_alerts"
