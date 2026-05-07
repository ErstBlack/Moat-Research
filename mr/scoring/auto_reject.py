"""Auto-reject decisions and the §5.5 normative reason-string table.

Spec §5.5 (auto-reject conditions + normative strings + severity tiers)
and §13.3 (severity tiers consumed by adjacent-rejection appendix).
"""
from __future__ import annotations

from enum import Enum

from mr.scoring.rubric import Scores


class AutoRejectReason(Enum):
    DEFENSIBILITY_LOW = "defensibility_low"
    AXIS_ZERO = "axis_zero"
    SINGLE_SOURCE = "single_source"
    UNRESTRICTED_ARCHIVES = "unrestricted_archives"
    TOS_PROHIBITS = "tos_prohibits"
    HARDWARE_OVER = "hardware_over"
    MISSING_HW_KEYS = "missing_hw_keys"
    FABRICATION = "fabrication"


# Spec §5.5 normative table — these strings are stored in scores.auto_reject_reason
# and referenced by §13.3 severity classification. DO NOT change the strings without
# also updating the spec.
REASON_STRINGS: dict[AutoRejectReason, str] = {
    AutoRejectReason.DEFENSIBILITY_LOW: "defensibility ≤ 4",  # noqa: RUF001
    AutoRejectReason.AXIS_ZERO: "any axis = 0",
    AutoRejectReason.SINGLE_SOURCE: "single source",
    AutoRejectReason.UNRESTRICTED_ARCHIVES: "unrestricted archives",
    AutoRejectReason.TOS_PROHIBITS: "TOS prohibits redistribution",
    AutoRejectReason.HARDWARE_OVER: "hardware over envelope",
    AutoRejectReason.MISSING_HW_KEYS: "code_execution result missing required hardware keys",
    AutoRejectReason.FABRICATION: "claimed verdict inconsistent with cited evidence",
}


# Spec §13.3 severity tiers (after pass-6 merge of tier 4 into tier 1)
# Tier 1: hard-disqualifier rejections + missing-hw-keys + fabrication
# Tier 2: floor rejections (defensibility, axis-zero)
# Tier 3: manual rejections (string starting with "manual: ")
SEVERITY_TIERS: dict[AutoRejectReason, int] = {
    AutoRejectReason.SINGLE_SOURCE: 1,
    AutoRejectReason.UNRESTRICTED_ARCHIVES: 1,
    AutoRejectReason.TOS_PROHIBITS: 1,
    AutoRejectReason.HARDWARE_OVER: 1,
    AutoRejectReason.MISSING_HW_KEYS: 1,
    AutoRejectReason.FABRICATION: 1,
    AutoRejectReason.DEFENSIBILITY_LOW: 2,
    AutoRejectReason.AXIS_ZERO: 2,
}


def decide_floor_rejection(scores: Scores) -> AutoRejectReason | None:
    """Return the auto-reject reason if scores trigger §5.5 floor; else None.

    Defensibility ≤ 4 takes priority over any-axis-zero per spec §5.5
    enumeration order.
    """
    if scores.defensibility <= 4:
        return AutoRejectReason.DEFENSIBILITY_LOW
    if any(s == 0 for s in (
        scores.defensibility, scores.financial, scores.implementation, scores.hardware
    )):
        return AutoRejectReason.AXIS_ZERO
    return None


# Reverse map for severity_tier(): reason string → tier
_STRING_TO_TIER: dict[str, int] = {
    REASON_STRINGS[r]: SEVERITY_TIERS[r] for r in AutoRejectReason
}


def severity_tier(reason: str | None) -> int | None:
    """Map an auto_reject_reason string to its severity tier (1-3) per §13.3.

    Returns None if the string is unrecognized. Manual rejections with the
    "manual: " prefix return tier 3.
    """
    if reason is None:
        return None
    if reason.startswith("manual: "):
        return 3
    return _STRING_TO_TIER.get(reason)
