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
