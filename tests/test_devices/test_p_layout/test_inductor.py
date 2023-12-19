from hades.devices.p_layouts.inductor import octagonal_inductor
from hades.devices.p_layouts.tools import Layer, check_diff
import gdstk


def test_inductor():
    ind = octagonal_inductor(120e-6,
                             1,
                             5e-6,
                             2e-6,
                             Layer(10, 2))
    lib = gdstk.Library()
    lib.add(ind)
    lib.write_gds("ind.gds")
    check_diff("ind.gds", "./tests/test_devices/test_p_layout/ind_ref.gds")
