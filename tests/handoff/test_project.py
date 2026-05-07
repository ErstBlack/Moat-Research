from datetime import date

from mr.handoff.project import build_project_handoff
from mr.lifecycle.frontmatter import Brief
from mr.util.config import DEFAULT_CONFIG, Config


def _brief() -> Brief:
    return Brief(
        schema_version=1, title="FAA NOTAMs", slug="faa-notams",
        lane="ephemeral_public", niche="aviation alerts",
        niche_key="alerts_aviation", delivery_form="project",
        date_created=date(2026, 5, 4),
        sources=[{"url": "https://notams.aim.faa.gov/", "role": "primary", "archive_status": "none"}],
        scores={"defensibility": 7, "financial": 6, "implementation": 8, "hardware": 9, "composite": 7.13},
        body="## Thesis\nNOTAMs expire and are not archived by the FAA.\n",
    )


def test_project_handoff_includes_hardware_envelope():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="(no adjacent rejections)")
    assert "Xeon E5-2698 v4" in out
    assert "250 GB" in out
    assert "P4" in out


def test_project_handoff_includes_brief_body():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "FAA NOTAMs" in out
    assert "NOTAMs expire" in out


def test_project_handoff_first_action_prompt():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="x")
    assert "First action" in out
    assert "CLAUDE.md" in out


def test_project_handoff_includes_appendix():
    cfg = Config(**DEFAULT_CONFIG)
    out = build_project_handoff(_brief(), cfg=cfg, adjacent_appendix="## Adjacent rejections\n(none)")
    assert "Adjacent rejections" in out
