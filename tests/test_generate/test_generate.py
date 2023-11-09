import os
import warnings
from hades.main import generate_cli
from os import chdir


def test_generation():
    chdir("./tests/test_generate/")
    if os.name == "nt":
        warnings.warn(
            "Windows system not supported for local generation. Skipping Test"
        )
        return
    generate_cli(design_yaml="./design ind gf.yml", stop="geometries")
    generate_cli(design_yaml="./design ms sky.yml", stop="geometries")
