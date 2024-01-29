import os.path

import pytest

from hades.parsers.layermap import load_map, get_number

pytestmark = pytest.mark.skipif(
    not (os.path.isdir("./pdk/mock")), reason="PDK not installed."
)


def test_load_map():
    layers = load_map("mock")

    assert layers["Via1"]["VIA"] == (35, 0)
    assert layers["Via2"]["VIA"] == (12, 0)


def test_get_number():
    layers = load_map("mock")
    layer, datatype = get_number(layers, "Via1", "VIA")
    assert layer == 35
    assert datatype == 0

    layer, datatype = get_number(layers, "Metal1", "NET")
    assert layer == 34
    assert datatype == 0

    with pytest.raises(KeyError):
        get_number(layers, "Via1", "NET")
