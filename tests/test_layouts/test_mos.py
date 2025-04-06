from os.path import dirname, join
import pytest
from klayout import db

from hades.devices.mos import Mos, Dimensions
from hades.layouts.tools import check_diff

REF_PATH = dirname(__file__)


@pytest.mark.skip(reason="To be rewrite with active branch")
def test_mos(tmp_path):
    mos = Mos()
    lib = db.Layout()
    cell = mos.update_cell(
        Dimensions(n=1, w=130e-9, le=2e-6), {"pplus": (1, 0), "poly": (2, 0)}
    )
    lib = lib.add_cell(cell)
    lib.write(tmp_path / "mos.gds")
    assert check_diff(tmp_path / "mos.gds", join(REF_PATH, "ref_mos.gds"))
