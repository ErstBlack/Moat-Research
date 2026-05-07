"""Brief frontmatter parser, writer, and validator.

Spec §6.4 brief schema. Closed-set lane vocabulary (5 canonical + other).
schema_version 1 only (§15.2).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
_THESIS_RE = re.compile(r"##\s+Thesis\s*\n+(.+?)(?:\n##|\Z)", re.DOTALL)

LANES = frozenset({
    "ephemeral_public",
    "soon_to_be_restricted",
    "cross_source_fusion",
    "derived_artifact",
    "niche_vertical",
    "other",
})

DELIVERY_FORMS = frozenset({"project", "feature"})

SOURCE_ROLES = frozenset({"primary", "corroborating", "counter_evidence"})


class FrontmatterError(Exception):
    """Raised on invalid frontmatter content."""


@dataclass
class Brief:
    schema_version: int
    title: str
    slug: str
    lane: str
    niche: str
    niche_key: str
    delivery_form: str
    date_created: date
    sources: list[dict[str, Any]]
    verification_evidence: list[dict[str, Any]] = field(default_factory=list)
    disqualifier_verdicts: dict[str, Any] = field(default_factory=dict)
    scores: dict[str, Any] | None = None
    lane_note: str | None = None
    parent_project: str | None = None
    body: str = ""


def _parse_split(raw: str) -> tuple[dict[str, Any], str]:
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        raise FrontmatterError("missing or malformed YAML frontmatter")
    fm_text, body = m.group(1), m.group(2)
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return fm, body


def _validate(fm: dict[str, Any]) -> None:
    if fm.get("schema_version") != 1:
        raise FrontmatterError(
            f"unsupported schema_version {fm.get('schema_version')!r} (v1 only)"
        )
    for required in (
        "title",
        "slug",
        "lane",
        "niche",
        "niche_key",
        "delivery_form",
        "date_created",
        "sources",
    ):
        if required not in fm:
            raise FrontmatterError(f"missing required key: {required}")

    if fm["lane"] not in LANES:
        raise FrontmatterError(f"lane {fm['lane']!r} not in {sorted(LANES)}")
    if fm["lane"] == "other" and not fm.get("lane_note"):
        raise FrontmatterError("lane: other requires lane_note")

    if fm["delivery_form"] not in DELIVERY_FORMS:
        raise FrontmatterError(
            f"delivery_form {fm['delivery_form']!r} not in {sorted(DELIVERY_FORMS)}"
        )
    if fm["delivery_form"] == "feature" and not fm.get("parent_project"):
        raise FrontmatterError("delivery_form: feature requires parent_project")

    for s in fm["sources"]:
        if s.get("role") not in SOURCE_ROLES:
            raise FrontmatterError(f"source role {s.get('role')!r} not in {sorted(SOURCE_ROLES)}")


def read_brief(path: Path) -> Brief:
    """Parse a brief markdown file. Raises FrontmatterError on schema violation."""
    raw = path.read_text()
    fm, body = _parse_split(raw)
    _validate(fm)

    dc = fm["date_created"]
    parsed_date = dc if isinstance(dc, date) else date.fromisoformat(str(dc))

    return Brief(
        schema_version=fm["schema_version"],
        title=fm["title"],
        slug=fm["slug"],
        lane=fm["lane"],
        niche=fm["niche"],
        niche_key=fm["niche_key"],
        delivery_form=fm["delivery_form"],
        date_created=parsed_date,
        sources=fm["sources"],
        verification_evidence=fm.get("verification_evidence", []),
        disqualifier_verdicts=fm.get("disqualifier_verdicts", {}),
        scores=fm.get("scores"),
        lane_note=fm.get("lane_note"),
        parent_project=fm.get("parent_project"),
        body=body,
    )


def write_brief(path: Path, brief: Brief, body: str | None = None) -> None:
    """Write a brief to disk with frontmatter + body."""
    fm: dict[str, Any] = {
        "schema_version": brief.schema_version,
        "title": brief.title,
        "slug": brief.slug,
        "lane": brief.lane,
        "niche": brief.niche,
        "niche_key": brief.niche_key,
        "delivery_form": brief.delivery_form,
        "date_created": brief.date_created.isoformat(),
        "sources": brief.sources,
        "verification_evidence": brief.verification_evidence,
        "disqualifier_verdicts": brief.disqualifier_verdicts,
    }
    if brief.lane_note:
        fm["lane_note"] = brief.lane_note
    if brief.parent_project:
        fm["parent_project"] = brief.parent_project
    if brief.scores:
        fm["scores"] = brief.scores

    fm_text = yaml.safe_dump(fm, sort_keys=False, default_flow_style=False)
    body_text = body if body is not None else brief.body
    path.write_text(f"---\n{fm_text}---\n{body_text}")


def extract_thesis_first_sentence(path: Path) -> str:
    """Pull the first sentence from the brief's `## Thesis` body section."""
    raw = path.read_text()
    _, body = _parse_split(raw)
    m = _THESIS_RE.search(body)
    if not m:
        return ""
    para = m.group(1).strip().split("\n")[0].strip()
    # Split on '. ' for sentence boundary; keep terminal punctuation.
    if "." in para:
        first = para.split(".")[0].strip() + "."
        return first
    return para


def source_set(sources: list[dict[str, Any]]) -> set[str]:
    """Distinct hostnames across all sources (any role)."""
    out: set[str] = set()
    for s in sources:
        url = s.get("url", "")
        if not url:
            continue
        host = urlparse(url).hostname
        if host:
            out.add(host)
    return out
