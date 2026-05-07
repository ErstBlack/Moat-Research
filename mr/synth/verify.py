"""Host-driven disqualifier verification.

Spec §6.4: re-execute cited tools, evaluate predicates against new
results, detect fabrications (claim doesn't match its own cited evidence).
Exempt from max_tool_turns; counts toward max_verification_calls.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import httpx

from mr.lifecycle.frontmatter import Brief
from mr.tools.wayback import wayback_check

_HARDWARE_KEYS = ("peak_gpu_gb", "sustained_ram_gb", "storage_tb")
_HARDWARE_LIMITS = {"peak_gpu_gb": 8, "sustained_ram_gb": 250, "storage_tb": 17}

_PUBLISHER_ARCHIVE_RE = re.compile(
    r"archive|history|past issues|back issues|backfile|rss|atom",
    re.IGNORECASE,
)
_PUBLISHER_FETCH_TIMEOUT_S = 10.0
_PUBLISHER_FETCH_MAX_BYTES = 100_000


def _publisher_archive_regex_matches(url: str) -> bool:
    """Fetch URL body and test for spec §6.4 publisher-archive language.

    Fail-open on network error (returns False = unverified, treat claim
    as model-emitted "pass" — host verification could not confirm).
    """
    try:
        with httpx.Client(timeout=_PUBLISHER_FETCH_TIMEOUT_S, follow_redirects=True) as client:
            resp = client.get(url)
    except httpx.HTTPError:
        return False
    body = resp.text[:_PUBLISHER_FETCH_MAX_BYTES]
    return bool(_PUBLISHER_ARCHIVE_RE.search(body))


@dataclass
class VerificationOutcome:
    new_verdicts: dict[str, str] = field(default_factory=dict)
    flipped: dict[str, tuple[str, str]] = field(default_factory=dict)
    missing_hw_keys: bool = False
    fabrication_detected: bool = False

    @property
    def any_failure(self) -> bool:
        return any(v == "fail" for v in self.new_verdicts.values())

    def flipped_to_fail(self, key: str) -> bool:
        return key in self.flipped and self.flipped[key][1] == "fail"


def _evidence_by_id(brief: Brief) -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in brief.verification_evidence}


def _distinct_primary_corroborating_hosts(brief: Brief) -> set[str]:
    out: set[str] = set()
    for s in brief.sources:
        if s.get("role") in ("primary", "corroborating"):
            host = urlparse(s.get("url", "")).hostname
            if host:
                out.add(host)
    return out


def verify_disqualifier_check(brief: Brief, cfg: Any) -> VerificationOutcome:
    """Re-evaluate predicates against re-executed evidence; detect fabrication."""
    outcome = VerificationOutcome()
    evidence = _evidence_by_id(brief)

    hosts = _distinct_primary_corroborating_hosts(brief)
    new_single = "fail" if len(hosts) <= 1 else "pass"
    claimed = brief.disqualifier_verdicts.get("single_source", {}).get("verdict")
    outcome.new_verdicts["single_source"] = new_single
    if claimed and claimed != new_single:
        outcome.flipped["single_source"] = (claimed, new_single)
        outcome.fabrication_detected = True

    ua = brief.disqualifier_verdicts.get("unrestricted_archives", {})
    if ua:
        wayback_evid_id = ua.get("wayback_evidence_id")
        publisher_evid_id = ua.get("publisher_archive_evidence_id")
        new_ua = "pass"
        if wayback_evid_id and wayback_evid_id in evidence:
            ev = evidence[wayback_evid_id]
            url = ev.get("args", {}).get("url")
            if url:
                wb = wayback_check(url)
                min_snapshots = (
                    getattr(cfg, "disqualifiers", {}).get("unrestricted_archive_min_snapshots", 100)
                    if cfg else 100
                )
                min_years = (
                    getattr(cfg, "disqualifiers", {}).get("unrestricted_archive_min_years", 3)
                    if cfg else 3
                )
                if wb.count >= min_snapshots and wb.years >= min_years:
                    new_ua = "fail"
        if publisher_evid_id and new_ua == "pass" and publisher_evid_id in evidence:
            pub_url = evidence[publisher_evid_id].get("args", {}).get("url")
            if pub_url and _publisher_archive_regex_matches(pub_url):
                new_ua = "fail"
        outcome.new_verdicts["unrestricted_archives"] = new_ua
        claimed_ua = ua.get("verdict")
        if claimed_ua and claimed_ua != new_ua:
            outcome.flipped["unrestricted_archives"] = (claimed_ua, new_ua)
            outcome.fabrication_detected = True

    hw = brief.disqualifier_verdicts.get("hardware_over_envelope", {})
    if hw:
        evid_id = hw.get("evidence_id")
        if evid_id and evid_id in evidence:
            ev = evidence[evid_id]
            result = ev.get("result", {})
            if not all(k in result for k in _HARDWARE_KEYS):
                outcome.missing_hw_keys = True
            else:
                fail = any(result[k] > _HARDWARE_LIMITS[k] for k in _HARDWARE_KEYS)
                new_hw = "fail" if fail else "pass"
                outcome.new_verdicts["hardware_over_envelope"] = new_hw
                claimed_hw = hw.get("verdict")
                if claimed_hw and claimed_hw != new_hw:
                    outcome.flipped["hardware_over_envelope"] = (claimed_hw, new_hw)
                    outcome.fabrication_detected = True

    return outcome
