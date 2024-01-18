from os.path import dirname, join, isdir
import os
import pytest
from hades.layouts import tools


def test_tools():
    lay = tools.Layer(100, 4, "Via1")
    assert str(lay) == "Via1: 100/4"
    lay2 = tools.Layer(141)
    assert str(lay2) == "None: 141/0"
    base_path = dirname(__file__)
    ref = join(base_path, "ref_ind.gds")
    print(os.name)
    tools.check_diff(ref, ref)
    with pytest.raises(ValueError):
        tools.check_diff(ref, join(base_path, "ref_ms.gds"))


@pytest.mark.skipif(
    not isdir("./pdk/gf180mcuD"), reason="The PDK gf180mcu not installed."
)
def test_layer_stack_gf():
    layer_stack = tools.LayerStack("gf180mcu")
    print(layer_stack)
    assert layer_stack.stack[0].layer == 34
    assert layer_stack.get_metal_layer(1) == tools.Layer(
        34, 0, "Metal1", tools.LayerType.METAL
    )
    assert layer_stack.get_metal_layer(2) == tools.Layer(
        36, 0, "Metal2", tools.LayerType.METAL
    )
    assert layer_stack.get_metal_layer(-1) == tools.Layer(
        81, 0, "Metal5", tools.LayerType.METAL
    )

    assert layer_stack.get_via_layer(1) == tools.Layer(35, 0, "Via1")
    assert layer_stack.get_via_layer(2) == tools.Layer(38, 0, "Via2")
    assert layer_stack.get_via_layer(-1) == tools.Layer(41, 0, "Via4")


@pytest.mark.skipif(not isdir("./pdk/sky130A"), reason="The PDK sky130 not installed.")
def test_layer_stack_sw():
    layer_stack = tools.LayerStack("sky130")
    print(layer_stack)
    assert layer_stack.stack[0].layer == 68
    assert layer_stack.get_metal_layer(1) == tools.Layer(
        68, 20, "met1", tools.LayerType.METAL
    )
    assert layer_stack.get_metal_layer(2) == tools.Layer(
        69, 20, "met2", tools.LayerType.METAL
    )
    assert layer_stack.get_metal_layer(-1) == tools.Layer(
        72, 20, "met5", tools.LayerType.METAL
    )

    assert layer_stack.get_via_layer(1) == tools.Layer(68, 44, "via")
    assert layer_stack.get_via_layer(2) == tools.Layer(69, 44, "via2")
    assert layer_stack.get_via_layer(-1) == tools.Layer(71, 44, "via4")
