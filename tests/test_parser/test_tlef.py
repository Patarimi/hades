import pytest
from hades.parsers.tlef import load_tlef, get_metal, get_via
from hades.techno import load_pdk
from os.path import join, dirname, isdir

pytestmark = pytest.mark.skipif(not (isdir("./pdk/mock")), reason="PDK not installed.")


def test_load_tlef():
    pdk = load_pdk("mock")
    path = join(dirname(dirname(__file__)), pdk["base_dir"], pdk["techlef"])
    layers = load_tlef(path)
    print(layers)

    assert get_metal(1, path) == "Metal1"
    assert get_metal(-1, path) == "Metal5"
    with pytest.raises(ValueError):
        get_metal(0, path)
    assert get_via(1, path) == "CON"
