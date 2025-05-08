from os.path import dirname, join
from klayout import db

from hades.layouts.active import mosfet
from hades.layouts.tools import check_diff, LayerStack, Layer

REF_PATH = dirname(__file__)

stack = LayerStack("mock")


def test_mos(tmp_path):
    lib = db.Layout()
    mosfet(
        lib,
        stack,
        nf = 1,
        doping_layer=Layer(1, 0),
        poly_layer=Layer(2, 0, spacing=0.5),
    )
    lib.write(tmp_path / "mos.gds")
    assert check_diff(tmp_path / "mos.gds", join(REF_PATH, "ref_mos.gds"))
