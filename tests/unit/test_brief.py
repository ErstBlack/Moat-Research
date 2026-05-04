import math
import pytest
from workers.common import brief


class TestCompositeScore:
    def test_all_tens_returns_ten(self):
        assert brief.composite_score(10, 10, 10) == pytest.approx(10.0)

    def test_zero_financial_returns_zero(self):
        assert brief.composite_score(0, 10, 10) == 0.0

    def test_zero_implementation_returns_zero(self):
        assert brief.composite_score(10, 0, 10) == 0.0

    def test_zero_hardware_returns_zero(self):
        assert brief.composite_score(10, 10, 0) == 0.0

    def test_known_values_match_formula(self):
        # financial=6.5, implementation=9.0, hardware=9.5 — example from spec §7.1
        result = brief.composite_score(6.5, 9.0, 9.5)
        expected = (6.5 ** 0.4) * (9.0 ** 0.3) * (9.5 ** 0.3)
        assert result == pytest.approx(expected, rel=1e-9)
        assert result == pytest.approx(8.031, abs=0.005)

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            brief.composite_score(-1, 5, 5)

    def test_rejects_above_ten(self):
        with pytest.raises(ValueError):
            brief.composite_score(10.1, 5, 5)


class TestFilename:
    def test_format_score_prefix_padding(self):
        assert brief.format_score_prefix(8.031) == "08.031"
        assert brief.format_score_prefix(10.0) == "10.000"
        assert brief.format_score_prefix(0.0) == "00.000"
        assert brief.format_score_prefix(0.001) == "00.001"

    def test_format_score_prefix_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            brief.format_score_prefix(-0.1)
        with pytest.raises(ValueError):
            brief.format_score_prefix(10.001)

    def test_filename_for_scored(self):
        assert brief.filename_for(8.031, "20260504", "fcc-eas-alerts") == "08.031-20260504-fcc-eas-alerts.md"

    def test_filename_for_unscored(self):
        assert brief.filename_for(None, "20260504", "fcc-eas-alerts") == "--.----20260504-fcc-eas-alerts.md"

    def test_filename_for_rejected(self):
        assert brief.filename_for(0.0, "20260504", "some-thing", failed_axis="financial") == "00.000-financial-20260504-some-thing.md"

    def test_filename_for_rejected_requires_zero_score(self):
        with pytest.raises(ValueError):
            brief.filename_for(5.0, "20260504", "x", failed_axis="financial")

    def test_parse_score_prefix_scored(self):
        assert brief.parse_score_prefix("08.031-20260504-fcc-eas-alerts.md") == 8.031

    def test_parse_score_prefix_unscored(self):
        assert brief.parse_score_prefix("--.----20260504-fcc-eas-alerts.md") is None

    def test_parse_score_prefix_rejected(self):
        assert brief.parse_score_prefix("00.000-financial-20260504-x.md") == 0.0

    def test_parse_score_prefix_invalid_raises(self):
        with pytest.raises(ValueError):
            brief.parse_score_prefix("nope.md")

    def test_natural_sort_order(self):
        names = [
            brief.filename_for(7.115, "20260504", "a"),
            brief.filename_for(9.412, "20260504", "b"),
            brief.filename_for(8.730, "20260503", "c"),
        ]
        sorted_desc = sorted(names, reverse=True)
        assert sorted_desc[0].startswith("09.412")
        assert sorted_desc[1].startswith("08.730")
        assert sorted_desc[2].startswith("07.115")


from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestParse:
    def test_parse_scored_brief(self):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        assert b.id == "brief_2026_05_04_fcc_eas_alerts"
        assert b.lane == 1
        assert b.secondary_lanes == [3]
        assert b.status == "scored"
        assert b.composite_score == pytest.approx(8.031, abs=0.005)
        assert b.feasibility_scores["financial"]["composite"] == 6.5
        assert b.body.strip() == "Body text goes here."

    def test_parse_unscored_candidate(self):
        b = brief.parse_brief(FIXTURES / "brief_candidate_unscored.md")
        assert b.status == "candidate"
        assert b.composite_score is None
        assert b.feasibility_scores is None

    def test_any_axis_zero_detected(self):
        b = brief.parse_brief(FIXTURES / "brief_zero_financial.md")
        assert brief.failed_axis(b) == "financial"
        b2 = brief.parse_brief(FIXTURES / "brief_zero_implementation.md")
        assert brief.failed_axis(b2) == "implementation"
        b3 = brief.parse_brief(FIXTURES / "brief_zero_hardware.md")
        assert brief.failed_axis(b3) == "hardware"

    def test_no_failed_axis_for_valid_brief(self):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        assert brief.failed_axis(b) is None

    def test_no_failed_axis_for_unscored(self):
        b = brief.parse_brief(FIXTURES / "brief_candidate_unscored.md")
        assert brief.failed_axis(b) is None


class TestSerialize:
    def test_round_trip(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        out = tmp_path / "out.md"
        brief.write_brief(b, out)
        b2 = brief.parse_brief(out)
        assert b2.id == b.id
        assert b2.composite_score == pytest.approx(b.composite_score)
        assert b2.body.strip() == b.body.strip()

    def test_lane_validation(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        b.lane = 99
        with pytest.raises(ValueError, match="lane"):
            brief.write_brief(b, tmp_path / "x.md")

    def test_status_validation(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        b.status = "wat"
        with pytest.raises(ValueError, match="status"):
            brief.write_brief(b, tmp_path / "x.md")
