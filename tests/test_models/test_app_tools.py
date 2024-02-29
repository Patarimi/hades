from math import sqrt

from hades.models import tools
from pytest import approx


def test_db10():
    assert approx(tools.db20(1)) == 0
    assert approx(tools.db20(sqrt(2))) == 3.0103
    assert approx(tools.db20(2, 2)) == 9.0309


def test_quality():
    assert approx(tools.quality(1 + 1j)) == 1
    assert approx(tools.quality(1 + 0.5j)) == 0.5
    assert approx(tools.quality(5 + 10j)) == 2


def test_norm_diff():
    assert approx(tools.norm_diff(1, 1)) == 0
    assert approx(tools.norm_diff(1, 2)) == 1 / 3
    assert approx(tools.norm_diff(2, 1)) == 1 / 3
    assert approx(tools.norm_diff(1, -1)) == 1
    assert approx(tools.norm_diff(-1, 1)) == 1
    assert approx(tools.norm_diff(1, 0)) == 1
    assert approx(tools.norm_diff(0, 1)) == 1
    assert approx(tools.norm_diff(1, -2)) == 1
    assert approx(tools.norm_diff(-2, 1)) == 1
