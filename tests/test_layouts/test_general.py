import gdstk

from hades.layouts.general import via, via_stack, ground_plane
from hades.layouts.tools import LayerStack, check_diff
from os.path import dirname, join

stack = LayerStack("mock")
REF_PATH = dirname(__file__)


def test_via(tmp_path):

    v = via(stack.get_via_layer(2), (3, 4))
    lib = gdstk.Library("toto")
    lib.add(v)
    lib.write_gds(tmp_path / "via.gds")
    check_diff(tmp_path / "via.gds", join(REF_PATH, "ref_via.gds"))


def test_via_stack(tmp_path):

    v = via_stack(stack, 2, 1, (3, 4))
    lib = gdstk.Library("toto")
    lib.add(v)
    lib.write_gds(tmp_path / "via_stack.gds")
    check_diff(tmp_path / "via_stack.gds", join(REF_PATH, "ref_via_stack.gds"))


def test_ground_plane(tmp_path):

    v = ground_plane(stack, (3, 4), 1)
    lib = gdstk.Library("toto")
    lib.add(v)
    lib.write_gds(tmp_path / "ground_plane.gds")
    check_diff(tmp_path / "ground_plane.gds", join(REF_PATH, "ref_ground_plane.gds"))
