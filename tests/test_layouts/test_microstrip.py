from os.path import dirname, join, isdir

import gdstk
import pytest
from hades.layouts.microstrip import (
    straight_line,
    coupled_lines,
    lange_coupler,
    marchand_balun,
)
from hades.layouts.tools import LayerStack, check_diff

pytestmark = pytest.mark.skipif(not isdir("./pdk/mock"), reason="PDK not installed.")

if isdir("./pdk/mock"):
    layerstack = LayerStack("mock")
    REF_PATH = dirname(__file__)


def test_straight_line(tmp_path):
    ms = straight_line(10e-6, 50e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(tmp_path / "ms.gds")
    check_diff(tmp_path / "ms.gds", join(REF_PATH, "ref_ms.gds"))


def test_coupler(tmp_path):
    ms = coupled_lines(10e-6, 50e-6, 20e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "cpl.gds"))
    check_diff(tmp_path / "cpl.gds", join(REF_PATH, "ref_cpl.gds"))


def test_lange(tmp_path):
    ms = lange_coupler(1.3e-6, 405e-6, 3.7e-6, layerstack)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "lange.gds"))
    check_diff(tmp_path / "lange.gds", join(REF_PATH, "ref_lange.gds"))


def test_marchand(tmp_path):
    ms = marchand_balun(2e-6, 400e-6, 4e-6, 66e-6, layerstack, widths=25e-6)
    lib = gdstk.Library()
    lib.add(ms)
    lib.write_gds(join(tmp_path, "marchand.gds"))
    check_diff(tmp_path / "marchand.gds", join(REF_PATH, "ref_marchand.gds"))
