import os
from os.path import dirname

from hades.devices.p_layouts.inductor import octagonal_inductor
from hades.devices.p_layouts.tools import Layer, check_diff
import gdstk


def test_inductor():
    ind = octagonal_inductor(120e-6,
                             1,
                             5e-6,
                             2e-6,
                             Layer(10, 2))
    lib = gdstk.Library()
    lib.add(ind)
    lib.write_gds("ind.gds")
    ref_path = dirname(__file__)
    gen_path = os.getcwd()
    check_diff(gen_path + "ind.gds", ref_path + "ind_ref.gds")
