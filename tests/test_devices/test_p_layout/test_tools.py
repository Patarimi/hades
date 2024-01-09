from os.path import dirname, join
import os

from hades.layouts import tools


def test_tools():
    lay = tools.Layer(100, 4)
    assert str(lay) == "100/4"
    lay2 = tools.Layer(141)
    assert str(lay2) == "141/0"
    base_path = dirname(__file__)
    ref = join(base_path, "ind_ref.gds")
    print(os.name)
    tools.check_diff(ref, ref)


def test_layer_stack_gf():
    layer_stack = tools.LayerStack("gf180mcu")
    print(layer_stack)
    assert layer_stack.stack[0].data == 34
    assert layer_stack.get_metal_layer(1) == tools.Layer(34, 0, "Metal1")
    assert layer_stack.get_metal_layer(2) == tools.Layer(36, 0, "Metal2")
    assert layer_stack.get_metal_layer(-1) == tools.Layer(81, 0, "Metal5")

    assert layer_stack.get_via_layer(1) == tools.Layer(35, 0, "Via1")
    assert layer_stack.get_via_layer(2) == tools.Layer(38, 0, "Via2")
    assert layer_stack.get_via_layer(-1) == tools.Layer(41, 0, "Via4")


def test_layer_stack_sw():
    layer_stack = tools.LayerStack("sky130")
    print(layer_stack)
    assert layer_stack.stack[0].data == 67
    assert layer_stack.get_metal_layer(1) == tools.Layer(67, 20, "li1")
    assert layer_stack.get_metal_layer(2) == tools.Layer(68, 20, "met1")
    assert layer_stack.get_metal_layer(-1) == tools.Layer(72, 20, "met5")

    assert layer_stack.get_via_layer(1) == tools.Layer(67, 44, "mcon")
    assert layer_stack.get_via_layer(2) == tools.Layer(68, 44, "via")
    assert layer_stack.get_via_layer(-1) == tools.Layer(71, 44, "via4")
