from os.path import dirname, join

import gdstk

from hades.layouts.microstrip import (
    straight_line,
    coupled_lines,
    lange_coupler,
)
from hades.layouts.tools import LayerStack, check_diff


layerstack = LayerStack("gf180mcu")
REF_PATH = dirname(__file__)


def test_straight_line(tmp_path):
    ms = straight_line(10e-6, 50e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(tmp_path / "ms.gds")
    check_diff(tmp_path / "ms.gds", join(REF_PATH, "ms_ref.gds"))


def test_coupler(tmp_path):
    ms = coupled_lines(10e-6, 50e-6, 20e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "cpl.gds"))
    check_diff(tmp_path / "cpl.gds", join(REF_PATH, "cpl_ref.gds"))


def test_lange(tmp_path):
    ms = lange_coupler(1.3e-6, 405e-6, 3.7e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "lange.gds"))
    check_diff(tmp_path / "lange.gds", join(REF_PATH, "lange_ref.gds"))
