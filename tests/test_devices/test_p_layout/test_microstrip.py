from os.path import dirname, join

import gdstk

from hades.devices.p_layouts.microstrip import (
    straight_line,
    coupled_lines,
    lange_coupler,
)
from hades.devices.p_layouts.tools import Layer, check_diff


def test_straight_line(tmp_path):
    ms = straight_line(10e-6, 50e-6, Layer(10, 2), Layer(50))
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(tmp_path / "ms.gds")
    ref_path = dirname(__file__)
    check_diff(tmp_path / "ms.gds", join(ref_path, "ms_ref.gds"))


def test_coupler(tmp_path):
    ref_path = dirname(__file__)
    ms = coupled_lines(10e-6, 50e-6, 20e-6, Layer(10, 2), Layer(50))
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "cpl.gds"))
    check_diff(tmp_path / "cpl.gds", join(ref_path, "cpl_ref.gds"))


def test_lange(tmp_path):
    mt = Layer(37, 140)
    via = Layer(56, 140)
    mb = Layer(36, 140)
    mg = Layer(32)
    ref_path = dirname(__file__)
    ms = lange_coupler(
        1.3e-6,
        405e-6,
        3.7e-6,
        (mt, via, mb),
        mg,
    )
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "lange.gds"))
    check_diff(tmp_path / "lange.gds", join(ref_path, "lange_ref.gds"))
