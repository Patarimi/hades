from os.path import dirname, join

import gdstk

from hades.devices.p_layouts.microstrip import straight_line
from hades.devices.p_layouts.tools import Layer, check_diff


def test_inductor(tmp_path):
    ms = straight_line(10e-6,
                       50e-6,
                       Layer(10, 2),
                       Layer(50))
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(tmp_path / "ms.gds")
    ref_path = dirname(__file__)
    check_diff(tmp_path / "ms.gds", join(ref_path, "ms_ref.gds"))
