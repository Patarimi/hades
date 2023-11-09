import hades.devices.app_models.filter as flr
from pytest import approx
from numpy import array


def test_filter():
    proto = flr.prototype(5, "flat")
    assert proto == approx(array([0.6180, 1.6180, 2, 1.618, 0.618]), 5)

    proto = flr.prototype(3, "ripple", 0.5)
    assert proto == approx(array([1.5963, 1.0967, 1.5963, 1]), 5)
