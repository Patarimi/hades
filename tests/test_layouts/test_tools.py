from os.path import dirname, join, isdir
import os
import pytest
from hades.layouts import tools
import logging


def test_tools():
    lay = tools.Layer(100, 4, "Via1")
    assert str(lay) == "Via1: 100/4"
    lay2 = tools.Layer(141)
    assert str(lay2) == "None: 141/0"
    base_path = dirname(__file__)
    ref = join(base_path, "ref_ind.gds")
    logging.debug(os.name)
    tools.check_diff(ref, ref)
    with pytest.raises(ValueError):
        tools.check_diff(ref, join(base_path, "ref_ms.gds"))


@pytest.mark.skipif(
    not isdir("./pdk/gf180mcuD"), reason="The PDK gf180mcu not installed."
)
def test_layer_stack_gf():
    layer_stack = tools.LayerStack("gf180mcu")
    logging.debug(layer_stack)
    assert layer_stack.stack[0].layer == 34
    assert layer_stack.get_metal_layer(1) == tools.Layer(34, 0, "Metal1", 0.23, 0.3)
    assert layer_stack.get_metal_layer(2) == tools.Layer(36, 0, "Metal2", 0.28, 0.3)
    assert layer_stack.get_metal_layer(-1) == tools.Layer(81, 0, "Metal5", 0.44, 0.6)

    assert layer_stack.get_via_layer(1) == tools.ViaLayer(
        35, 0, "Via1", 0.26, 0.26, 0.01
    )
    assert layer_stack.get_via_layer(2) == tools.ViaLayer(
        38, 0, "Via2", 0.26, 0.26, 0.01
    )
    assert layer_stack.get_via_layer(-1) == tools.ViaLayer(
        41, 0, "Via4", 0.26, 0.26, 0.01
    )


@pytest.mark.skipif(not isdir("./pdk/sky130A"), reason="The PDK sky130 not installed.")
def test_layer_stack_sw():
    layer_stack = tools.LayerStack("sky130")
    logging.debug(layer_stack)
    assert layer_stack.stack[0].layer == 68
    assert layer_stack.get_metal_layer(1) == tools.Layer(68, 20, "met1", 0.14)
    assert layer_stack.get_metal_layer(2) == tools.Layer(69, 20, "met2", 0.14)
    assert layer_stack.get_metal_layer(-1) == tools.Layer(72, 20, "met5", 1.6)

    assert layer_stack.get_via_layer(1) == tools.ViaLayer(
        68, 44, "via", 0.15, 0.17, 0.055
    )
    assert layer_stack.get_via_layer(2) == tools.ViaLayer(
        69, 44, "via2", 0.2, 0.2, 0.065
    )
    assert layer_stack.get_via_layer(-1) == tools.ViaLayer(
        71, 44, "via4", 0.8, 0.8, 0.31
    )
