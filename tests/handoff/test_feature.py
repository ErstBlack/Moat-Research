from datetime import date

from mr.handoff.feature import build_feature_handoff
from mr.lifecycle.frontmatter import Brief
from mr.util.config import DEFAULT_CONFIG, Config


def _brief() -> Brief:
    return Brief(
        schema_version=1, title="Aviation alerts in SoMD",
        slug="aviation-alerts-somd",
        lane="ephemeral_public", niche="aviation alerts",
        niche_key="alerts_aviation", delivery_form="feature",
        parent_project="somd-cameras",
        date_created=date(2026, 5, 7),
        sources=[{"url": "https://notams.aim.faa.gov/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.13},
        body="## Thesis\nAdd aviation NOTAMs to somd-cameras feed.\n",
    )


def test_feature_handoff_mentions_parent_project():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_feature_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "somd-cameras" in out
    assert "extending" in out.lower() or "feature" in out.lower()


def test_feature_handoff_first_action_reads_existing_repo():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_feature_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "CLAUDE.md" in out
    assert "do not create new files" in out.lower()
    assert "feature branch" in out.lower()
