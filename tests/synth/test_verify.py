from datetime import date
from unittest.mock import patch

from mr.lifecycle.frontmatter import Brief
from mr.synth.verify import verify_disqualifier_check


def _brief_with_verdicts(
    sources: list[dict],
    verification_evidence: list[dict],
    disqualifier_verdicts: dict,
) -> Brief:
    return Brief(
        schema_version=1, title="x", slug="x", lane="ephemeral_public",
        niche="x", niche_key="x", delivery_form="project",
        date_created=date(2026, 5, 7),
        sources=sources,
        verification_evidence=verification_evidence,
        disqualifier_verdicts=disqualifier_verdicts,
    )


def test_single_source_predicate_le_1():
    brief = _brief_with_verdicts(
        sources=[{"url": "https://a.com/", "role": "primary", "archive_status": "none"}],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.flipped_to_fail("single_source")


def test_single_source_passes_with_two_distinct_hosts():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert not outcome.any_failure


def test_single_source_counter_evidence_excluded():
    """Per spec §6.4: counter_evidence does NOT count toward distinct hosts."""
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://archive.org/", "role": "counter_evidence", "archive_status": "none"},
        ],
        verification_evidence=[],
        disqualifier_verdicts={"single_source": {"verdict": "pass"}},
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.flipped_to_fail("single_source")


@patch("mr.synth.verify.wayback_check")
def test_unrestricted_archives_predicate_meets_threshold(mock_wayback):
    from datetime import date as ddate

    from mr.tools.wayback import WaybackResult

    mock_wayback.return_value = WaybackResult(
        count=150, first=ddate(2020, 1, 1), last=ddate(2026, 1, 1)
    )

    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {
                "id": "e1",
                "tool": "wayback_check",
                "args": {"url": "https://a.com/"},
                "result": {"count": 47, "first": "2023-04-12", "last": "2026-04-30"},
            },
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "unrestricted_archives": {
                "verdict": "pass",
                "wayback_evidence_id": "e1",
                "publisher_archive_evidence_id": None,
            },
        },
    )
    cfg_dummy = type("Cfg", (), {
        "disqualifiers": {
            "unrestricted_archive_min_snapshots": 100,
            "unrestricted_archive_min_years": 3,
        },
    })()
    outcome = verify_disqualifier_check(brief, cfg=cfg_dummy)
    assert outcome.flipped_to_fail("unrestricted_archives")


def test_hardware_over_envelope_missing_keys_fails():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {
                "id": "e3",
                "tool": "code_execution",
                "args": {"code": "x"},
                "result": {"peak_gpu_gb": 4.0},
            },
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.missing_hw_keys


def test_hardware_over_envelope_predicate_pass():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {
                "id": "e3",
                "tool": "code_execution",
                "args": {"code": "x"},
                "result": {"peak_gpu_gb": 4.0, "sustained_ram_gb": 32, "storage_tb": 0.5},
            },
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert not outcome.any_failure
    assert not outcome.missing_hw_keys


def test_hardware_over_envelope_predicate_fail():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {
                "id": "e3",
                "tool": "code_execution",
                "args": {"code": "x"},
                "result": {"peak_gpu_gb": 16, "sustained_ram_gb": 32, "storage_tb": 0.5},
            },
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.flipped_to_fail("hardware_over_envelope")


def test_fabrication_when_claim_inconsistent_with_evidence():
    brief = _brief_with_verdicts(
        sources=[
            {"url": "https://a.com/", "role": "primary", "archive_status": "none"},
            {"url": "https://b.com/", "role": "corroborating", "archive_status": "none"},
        ],
        verification_evidence=[
            {
                "id": "e3",
                "tool": "code_execution",
                "args": {"code": "x"},
                "result": {"peak_gpu_gb": 16, "sustained_ram_gb": 32, "storage_tb": 0.5},
            },
        ],
        disqualifier_verdicts={
            "single_source": {"verdict": "pass"},
            "hardware_over_envelope": {"verdict": "pass", "evidence_id": "e3"},
        },
    )
    outcome = verify_disqualifier_check(brief, cfg=None)
    assert outcome.fabrication_detected
