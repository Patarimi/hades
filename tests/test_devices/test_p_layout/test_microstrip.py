from os.path import dirname, join

import gdstk

from hades.devices.p_layouts.microstrip import straight_line, coupled_lines
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
