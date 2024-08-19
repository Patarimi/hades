from os.path import dirname, join
from hades.devices.mos import Mos, Dimensions
import gdstk
from hades.layouts.tools import check_diff

REF_PATH = dirname(__file__)

def test_mos(tmp_path):
    mos = Mos()
    cell = mos.update_cell(Dimensions(n=1, w=130e-9, le=2e-6), {"pplus": (1, 0), "poly": (2, 0)})
    lib = gdstk.Library().add(cell)
    lib.write_gds(tmp_path / "mos.gds")
    assert check_diff(tmp_path / "mos.gds", join(REF_PATH, "ref_mos.gds"))
