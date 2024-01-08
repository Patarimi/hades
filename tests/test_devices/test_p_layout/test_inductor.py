from os.path import dirname, join

from hades.devices.p_layouts.inductor import octagonal_inductor
from hades.devices.p_layouts.tools import LayerStack, check_diff
import gdstk


def test_inductor(tmp_path):
    layerstack = LayerStack("gf180mcu")
    ind = octagonal_inductor(120e-6, 1, 5e-6, 2e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ind)
    lib.write_gds(tmp_path / "ind.gds")
    ref_path = dirname(__file__)
    check_diff(tmp_path / "ind.gds", join(ref_path, "ind_ref.gds"))
