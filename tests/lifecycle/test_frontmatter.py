from datetime import date
from pathlib import Path

import pytest

from mr.lifecycle.frontmatter import (
    FrontmatterError,
    extract_thesis_first_sentence,
    read_brief,
    source_set,
    write_brief,
)


def _minimal_brief_yaml() -> str:
    return """---
schema_version: 1
title: FAA NOTAMs
slug: faa-notams
lane: ephemeral_public
niche: aviation alerts
niche_key: alerts_aviation
delivery_form: project
date_created: 2026-05-04
sources:
  - url: https://notams.aim.faa.gov/notamSearch
    role: primary
    archive_status: none
verification_evidence:
  - id: e1
    tool: wayback_check
    args: {url: "https://notams.aim.faa.gov/notamSearch"}
    result: {count: 47, first: "2023-04-12", last: "2026-04-30"}
  - id: e3
    tool: code_execution
    args: {code: "estimate_utilization()"}
    result: {peak_gpu_gb: 0, sustained_ram_gb: 4, storage_tb: 0.1}
disqualifier_verdicts:
  defensibility_threshold: n/a
  any_axis_zero: n/a
  single_source:
    verdict: pass
  unrestricted_archives:
    verdict: pass
    wayback_evidence_id: e1
    publisher_archive_evidence_id: null
  tos_redistribution:
    verdict: n/a
    evidence_id: null
  hardware_over_envelope:
    verdict: pass
    evidence_id: e3
---

# FAA NOTAMs

## Thesis
NOTAMs expire and are not archived by the FAA. Aggregating them creates a unique time-series corpus.

## Why this is a moat
Multi-year accumulation creates archive-history defensibility.

## Sources
| URL | role |
| --- | ---- |
| notams.aim.faa.gov | primary |

## Financial sketch
Aviation lawyers + enthusiast subscribers; ~$20k/yr.

## Implementation sketch
1-2 weeks to MVP.

## Hardware fit
4 GB GPU steady-state, well under envelope.

## Disqualifier check
All hard disqualifiers pass.
"""


def test_read_minimal_brief(tmp_path: Path):
    p = tmp_path / "20260504-faa-notams.md"
    p.write_text(_minimal_brief_yaml())
    b = read_brief(p)
    assert b.slug == "faa-notams"
    assert b.lane == "ephemeral_public"
    assert b.niche == "aviation alerts"
    assert b.niche_key == "alerts_aviation"
    assert b.delivery_form == "project"
    assert b.date_created == date(2026, 5, 4)
    assert len(b.sources) == 1
    assert b.sources[0]["role"] == "primary"
    assert b.scores is None  # not yet scored


def test_extract_thesis_first_sentence(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml())
    sentence = extract_thesis_first_sentence(p)
    assert sentence == "NOTAMs expire and are not archived by the FAA."


def test_source_set_dedups_by_host(tmp_path: Path):
    sources = [
        {"url": "https://example.com/a", "role": "primary"},
        {"url": "https://example.com/b", "role": "corroborating"},
        {"url": "https://other.com/x", "role": "corroborating"},
        {"url": "https://archive.org/wayback/example.com", "role": "counter_evidence"},
    ]
    s = source_set(sources)
    assert s == {"example.com", "other.com", "archive.org"}


def test_write_then_read_roundtrip(tmp_path: Path):
    p = tmp_path / "20260507-test.md"
    p.write_text(_minimal_brief_yaml())
    b = read_brief(p)

    p2 = tmp_path / "out.md"
    write_brief(p2, b, body="# Test\n\n## Thesis\nFoo bar.\n")
    b2 = read_brief(p2)
    assert b2.slug == b.slug
    assert b2.lane == b.lane


def test_invalid_lane_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("lane: ephemeral_public", "lane: bogus_lane"))
    with pytest.raises(FrontmatterError, match="lane"):
        read_brief(p)


def test_other_lane_requires_lane_note(tmp_path: Path):
    p = tmp_path / "x.md"
    yaml_text = _minimal_brief_yaml().replace("lane: ephemeral_public", "lane: other")
    # Missing lane_note for lane: other
    p.write_text(yaml_text)
    with pytest.raises(FrontmatterError, match="lane_note"):
        read_brief(p)


def test_missing_schema_version_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("schema_version: 1\n", ""))
    with pytest.raises(FrontmatterError, match="schema_version"):
        read_brief(p)


def test_unsupported_schema_version_rejected(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(_minimal_brief_yaml().replace("schema_version: 1", "schema_version: 2"))
    with pytest.raises(FrontmatterError, match="schema_version"):
        read_brief(p)
