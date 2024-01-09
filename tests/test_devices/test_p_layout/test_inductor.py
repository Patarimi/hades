from os.path import dirname, join

from hades.layouts.inductor import octagonal_inductor
from hades.layouts.tools import LayerStack, check_diff
import gdstk

REF_PATH = dirname(__file__)


def test_inductor(tmp_path):
    layerstack = LayerStack("gf180mcu")
    ind = octagonal_inductor(120e-6, 1, 5e-6, 2e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ind)
    lib.write_gds(tmp_path / "ind.gds")
    check_diff(tmp_path / "ind.gds", join(REF_PATH, "ind_ref.gds"))
