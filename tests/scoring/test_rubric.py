import math

import pytest

from mr.scoring.rubric import Scores, composite, default_weights


def test_default_weights_sum_to_one():
    w = default_weights()
    assert math.isclose(sum(w.values()), 1.0)


def test_all_tens_gives_ten():
    s = Scores(defensibility=10, financial=10, implementation=10, hardware=10)
    assert math.isclose(composite(s), 10.0, rel_tol=1e-6)


def test_all_zeros_gives_zero():
    s = Scores(defensibility=0, financial=0, implementation=0, hardware=0)
    assert composite(s) == 0.0


def test_any_axis_zero_zeros_composite():
    s = Scores(defensibility=10, financial=0, implementation=10, hardware=10)
    assert composite(s) == 0.0


def test_d5_others10_around_785():
    s = Scores(defensibility=5, financial=10, implementation=10, hardware=10)
    assert math.isclose(composite(s), 7.847, abs_tol=0.01)


def test_d10_others5_around_637():
    s = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    assert math.isclose(composite(s), 6.372, abs_tol=0.01)


def test_d5_others10_ranks_above_d10_others5():
    a = Scores(defensibility=5, financial=10, implementation=10, hardware=10)
    b = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    assert composite(a) > composite(b)


def test_custom_weights_override_default():
    s = Scores(defensibility=10, financial=5, implementation=5, hardware=5)
    custom = {"defensibility": 0.50, "financial": 0.20, "implementation": 0.15, "hardware": 0.15}
    # With heavy defensibility weight, the d=10 case should jump
    val = composite(s, weights=custom)
    assert val > 6.5  # should now be ~6.69


def test_invalid_score_outside_range_raises():
    with pytest.raises(ValueError):
        composite(Scores(defensibility=11, financial=5, implementation=5, hardware=5))
    with pytest.raises(ValueError):
        composite(Scores(defensibility=-1, financial=5, implementation=5, hardware=5))


def test_weights_must_sum_to_one():
    s = Scores(defensibility=5, financial=5, implementation=5, hardware=5)
    with pytest.raises(ValueError, match="weights"):
        composite(s, weights={"defensibility": 0.5, "financial": 0.5, "implementation": 0.5, "hardware": 0.5})
