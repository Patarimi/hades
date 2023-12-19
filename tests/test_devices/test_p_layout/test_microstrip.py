from hades.devices.p_layouts.microstrip import straight_line
from hades.devices.p_layouts.tools import Layer


def test_inductor():
    ms = straight_line(10e-6,
                       50e-6,
                       Layer(10, 2),
                       Layer(50))
