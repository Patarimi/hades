from hades.main import generate_cli
from os import chdir


def test_generation():
    chdir("./tests/test_generate/")
    generate_cli(design_yaml="./design ind gf.yml", stop="geometries")
    generate_cli(design_yaml="./design ms sky.yml", stop="geometries")
