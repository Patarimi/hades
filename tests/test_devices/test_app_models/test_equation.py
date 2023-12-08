import hades.devices.app_models.inductor as ind
import hades.devices.app_models.micro_strip as ms
import hades.devices.app_models.matching as mt
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


def test_lumped_l():
    z_in = 50
    z_out = 60 - 80j
    f = 2e9
    s1, s2 = mt.lumped_l(z_out, z_in)
    assert s1 == pytest.approx((0.0011651513899116792, 76.37626158259741))
    assert s2 == pytest.approx((-0.01716515138991168, -76.37626158259734))
    assert mt.denorm(s1[0], f).readable_value() == "92.720 f"
    assert mt.denorm(s1[1], f).readable_value() == "6.078 n"
    assert mt.denorm(s2[1], f).readable_value() == "1.042 p"
    assert mt.denorm(s2[0], f).readable_value() == "4.636 n"

    z_in = 9.3 - 17.16j
    z_out = 11.35 - 20.95j
    s1, s2 = mt.lumped_l(z_in, z_out)
    assert s1 == pytest.approx((178.178, 0.38215))
    assert s2 == pytest.approx((11.83755, 0.02545615))


def test_single_stub():
    z_in = 50
    z_out = 60 - 80j
    f = 2e9
    d, lo, ls = mt.single_shunt_stub(z_out, z_in)
    assert d == pytest.approx((0.11042321863830025, 0.2594445306228258))
    assert lo == pytest.approx((0.34497462163589154, 0.15502537836410857))
    assert ls == pytest.approx((0.09497462163589154, 0.40502537836410857))
    d, lo, ls = mt.single_series_stub(z_out, z_in)
    assert d == pytest.approx((0.3604232186383003, 0.00944453062282582))
    assert lo == pytest.approx((0.09497462163589143, 0.40502537836410857))
    assert ls == pytest.approx((0.34497462163589143, 0.15502537836410857))
