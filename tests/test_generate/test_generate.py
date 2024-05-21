import os
from hades.main import generate_cli
from hades.parsers.layermap import get_number
from os import chdir, getcwd
import yaml
import pytest

pytestmark = pytest.mark.skipif(
    not (os.path.isdir("./pdk/sky130B")) or not (os.path.isdir("./pdk/gf180mcuD")),
    reason="PDK not installed.",
)


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows system not supported for local generation. Skipping Test",
)
def test_generation():
    cwd = getcwd()
    chdir("./tests/test_generate/")
    for design in ("./design ind gf.yml", "./design ms sky.yml"):
        with open(design) as f:
            conf = yaml.load(f, Loader=yaml.Loader)
        pdk = conf["techno"]
        try:
            get_number(pdk, "toto")
        except FileNotFoundError:
            pytest.skip(f"The pdk {pdk} is not installed. Skipping")
        except KeyError:
            pass
        generate_cli(design_yaml=design, stop="geometries")
    chdir(cwd)
