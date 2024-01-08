import os.path

import pytest

from hades.parser.map import load_map, get_number

pytestmark = pytest.mark.skipif(not (os.path.isdir("./pdk")), reason="PDK not installed.")


def test_load_map():
    layers = load_map("gf180mcu")

    assert layers["Via1"]["VIA"] == (35, 0)
    assert layers["Via2"]["VIA"] == (38, 0)


def test_get_number():
    layer, datatype = get_number("gf180mcu", "Via1", "VIA")
    assert layer == 35
    assert datatype == 0

    layer, datatype = get_number("gf180mcu", "Metal1", "NET")
    assert layer == 34
    assert datatype == 0

    with pytest.raises(KeyError):
        get_number("gf180mcu", "Via1", "NET")
