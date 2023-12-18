from hades.devices.p_layouts.inductor import octagonal_inductor
from hades.devices.p_layouts.tools import Layer


def test_inductor():
    ind = octagonal_inductor(120e-6,
                             1,
                             5e-6,
                             2e-6,
                             Layer(10, 2))
