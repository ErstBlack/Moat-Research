from mr.scoring.auto_reject import (
    REASON_STRINGS,
    SEVERITY_TIERS,
    AutoRejectReason,
    decide_floor_rejection,
    severity_tier,
)
from mr.scoring.rubric import Scores


def test_reason_strings_are_normative():
    # Match spec §5.5 normative table verbatim
    assert REASON_STRINGS[AutoRejectReason.DEFENSIBILITY_LOW] == "defensibility ≤ 4"
    assert REASON_STRINGS[AutoRejectReason.AXIS_ZERO] == "any axis = 0"
    assert REASON_STRINGS[AutoRejectReason.SINGLE_SOURCE] == "single source"
    assert REASON_STRINGS[AutoRejectReason.UNRESTRICTED_ARCHIVES] == "unrestricted archives"
    assert REASON_STRINGS[AutoRejectReason.TOS_PROHIBITS] == "TOS prohibits redistribution"
    assert REASON_STRINGS[AutoRejectReason.HARDWARE_OVER] == "hardware over envelope"
    assert (
        REASON_STRINGS[AutoRejectReason.MISSING_HW_KEYS]
        == "code_execution result missing required hardware keys"
    )
    assert REASON_STRINGS[AutoRejectReason.FABRICATION] == "claimed verdict inconsistent with cited evidence"


def test_decide_floor_rejection_low_defensibility():
    s = Scores(defensibility=4, financial=10, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.DEFENSIBILITY_LOW


def test_decide_floor_rejection_axis_zero():
    s = Scores(defensibility=10, financial=0, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.AXIS_ZERO


def test_decide_floor_rejection_defensibility_priority():
    # When both d≤4 AND axis=0, defensibility takes priority (spec §5.5 order)
    s = Scores(defensibility=3, financial=0, implementation=10, hardware=10)
    assert decide_floor_rejection(s) == AutoRejectReason.DEFENSIBILITY_LOW


def test_decide_floor_rejection_passes():
    s = Scores(defensibility=5, financial=5, implementation=5, hardware=5)
    assert decide_floor_rejection(s) is None


def test_severity_tier_classification():
    assert severity_tier("single source") == 1
    assert severity_tier("unrestricted archives") == 1
    assert severity_tier("TOS prohibits redistribution") == 1
    assert severity_tier("hardware over envelope") == 1
    assert severity_tier("code_execution result missing required hardware keys") == 1
    assert severity_tier("claimed verdict inconsistent with cited evidence") == 1
    assert severity_tier("defensibility ≤ 4") == 2
    assert severity_tier("any axis = 0") == 2
    assert severity_tier("manual: not the right time") == 3
    assert severity_tier("manual: bad fit") == 3


def test_severity_tier_unknown_string_returns_none():
    assert severity_tier("some other reason") is None


def test_severity_tiers_are_complete():
    # Every named reason has a tier assignment
    for reason in AutoRejectReason:
        assert reason in SEVERITY_TIERS
