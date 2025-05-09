import klayout.db as kl

from hades.layouts.general import via, via_stack, ground_plane, get_dtext
from hades.layouts.tools import LayerStack, check_diff
from os.path import dirname, join

stack = LayerStack("mock")
REF_PATH = dirname(__file__)


def test_via(tmp_path):
    opnng = stack.get_via_layer(-1)
    assert opnng.name == "Opening"
    lib = kl.Layout()
    via(lib, stack.get_via_layer(2), (3, 4))
    lib.write(tmp_path / "via.gds")
    check_diff(tmp_path / "via.gds", join(REF_PATH, "ref_via.gds"))


def test_via_stack(tmp_path):
    lib = kl.Layout()
    via_stack(lib, stack, 2, 1, (3, 4))
    lib.write(tmp_path / "via_stack.gds")
    check_diff(tmp_path / "via_stack.gds", join(REF_PATH, "ref_via_stack.gds"))

    lib = kl.Layout()
    via_stack(lib, stack, -3, -4, (3, 4))
    lib.write(tmp_path / "via_stack_neg.gds")
    check_diff(tmp_path / "via_stack_neg.gds", join(REF_PATH, "ref_via_stack.gds"))


def test_dtext():
    lib = kl.Layout()
    lib.read(join(REF_PATH, "ref_line.gds"))
    gnd = get_dtext(lib, "gnd")
    assert gnd == kl.DText("gnd", 0, -0.9)


def test_ground_plane(tmp_path):
    lib = kl.Layout()
    ground_plane(lib, stack, (3, 4), 1)
    lib.write(tmp_path / "ground_plane.gds")
    check_diff(tmp_path / "ground_plane.gds", join(REF_PATH, "ref_ground_plane.gds"))
