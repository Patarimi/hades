from os.path import dirname, join, isdir
import pytest
from hades.layouts.inductor import octagonal_inductor
from hades.layouts.tools import LayerStack, check_diff
import gdstk

REF_PATH = dirname(__file__)
pytestmark = pytest.mark.skipif(not isdir("./pdk/mock"), reason="PDK not installed.")


def test_inductor(tmp_path):
    layerstack = LayerStack("mock")
    ind = octagonal_inductor(120e-6, 1, 5e-6, 2e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ind)
    lib.write_gds(tmp_path / "ind.gds")
    check_diff(tmp_path / "ind.gds", join(REF_PATH, "ref_ind.gds"))