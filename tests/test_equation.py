import hades.equation.inductor as ind
import hades.equation.micro_strip as ms
import pytest


def test_inductor():
    ref = (
        (1.0449259729944358e-10, 1.6718815567910975e-10),
        (4.179703891977743e-10, 6.68752622716439e-10),
    )
    for i, n in enumerate((1, 2)):
        for j, d in enumerate((50e-6, 80e-6)):
            assert ind.wheeler(n, d, 0.1, "hexagonal") == pytest.approx(ref[i][j])


def test_micro_strip_impedance():
    ref = (
        80.84395749319764,
        50.052965553475644,
        59.58804940235251,
        113.70422352016742,
    )
    for i, w in enumerate((5, 12, 9, 2)):
        assert ms.wheeler(w * 1e-6, 4e-6, 2, 1e-6) == pytest.approx((ref[i], 0))


def test_micro_strip_phase():
    ref_d = (4.540148543324036e-14, 2.2700742716620183e-13, 4.086133688991633e-12)
    for i, l in enumerate((10, 50, 900)):
        _, delay = ms.wheeler(12e-6, 4e-6, 2, 1e-6, l * 1e-6)
        assert delay == pytest.approx(ref_d[i])
