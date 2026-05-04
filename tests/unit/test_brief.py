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
