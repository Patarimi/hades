import os
from hades.main import generate_cli
from hades.techno import get_layer
from os import chdir
import yaml
import pytest


def test_generation():
    chdir("./tests/test_generate/")
    if os.name == "nt":
        pytest.skip(
            "Windows system not supported for local generation. Skipping Test"
        )
    for design in ("./design ind gf.yml", "./design ms sky.yml"):
        with open(design) as f:
            conf = yaml.load(f, Loader=yaml.Loader)
        pdk = conf["techno"]
        try:
            get_layer(pdk, "M6")
        except FileNotFoundError:
            pytest.skip(f"The pdk {pdk} is not installed. Skipping")
        generate_cli(design_yaml=design, stop="geometries")