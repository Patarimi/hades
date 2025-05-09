from os.path import dirname, join
from klayout import db

from hades.layouts.active import mosfet, line
from hades.layouts.tools import check_diff, LayerStack, Layer

REF_PATH = dirname(__file__)

stack = LayerStack("mock")


def test_mos(tmp_path):
    lib = db.Layout()
    mosfet(
        lib,
        stack,
        nf=1,
        doping_layer=Layer(1, 0),
        poly_layer=Layer(2, 0, spacing=0.5),
    )
    lib.write(tmp_path / "mos.gds")
    assert check_diff(tmp_path / "mos.gds", join(REF_PATH, "ref_mos.gds"))


def test_line(tmp_path):
    lib = db.Layout()
    lyr = stack.get_metal_layer(2)
    top = lib.create_cell("top")
    mos = mosfet(
        lib, stack, nf=5, doping_layer=Layer(1, 0), poly_layer=Layer(5, 0, spacing=0.5)
    )
    top.insert(db.DCellInstArray(mos, db.DVector(0, 0)))
    vdd = line(lib, "vdd", lyr)
    top.insert(db.DCellInstArray(vdd, db.DVector(0, 0)))
    gnd = line(lib, "gnd", lyr, below=True)
    top.insert(db.DCellInstArray(gnd, db.DVector(0, 0)))
    lib.write(tmp_path / "h_line.gds")
    assert check_diff(tmp_path / "h_line.gds", join(REF_PATH, "ref_line.gds"))
